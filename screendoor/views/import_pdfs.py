from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from screendoor.forms import CreatePositionForm, ImportApplicationsForm
from screendoor.models import Position
from screendoor.parseposter import parse_upload
from screendoor.redactor import redact_applications
from screendoor.tasks import process_applications
from screendoor.uservisibletext import InterfaceText, PositionText
from .main_views import position_detail
from celery.result import AsyncResult


def parse_position_return_dictionary(create_position_form):
    # don't commit partial positions with only pdf/url into db
    return parse_upload(create_position_form.save(commit=False))


# Adds position to user data
def save_position_to_user(request):
    request.user.positions.add(
        Position.objects.get(id=request.session['position_id']))


# Displays form allowing users to upload job posting PDF files and URLs
@login_required(login_url='login', redirect_field_name=None)
def import_position(request):
    if request.method == 'POST':
        create_position_form = CreatePositionForm(request.POST, request.FILES)

        # Is the form data valid
        if create_position_form.is_valid():
            dictionary = parse_position_return_dictionary(create_position_form)
            errors = dictionary.get('errors')
            if errors:
                create_position_form.add_error('pdf', errors)

            # Is the parsed data valid (any errors added)
            if create_position_form.is_valid():
                position = dictionary.get('position')

                # Persist position ID in session for saving and editing
                request.session['position_id'] = position.id

                # Successful render of a position
                return render(
                    request, 'createposition/importposition.html', {
                        'position': position,
                        'form': create_position_form,
                        'baseVisibleText': InterfaceText,
                        'userVisibleText': PositionText
                    })

            # Display errors
            return render(
                request, 'createposition/importposition.html', {
                    'form': create_position_form,
                    'baseVisibleText': InterfaceText,
                    'userVisibleText': PositionText
                })

        # User pressed save button on uploaded and parsed position
        if request.POST.get("save-position"):
            save_position_to_user(request)
            return redirect('home')

    # Default view for GET request
    create_position_form = CreatePositionForm()
    return render(request, 'createposition/importposition.html', {
        'form': CreatePositionForm,
        'baseVisibleText': InterfaceText
    })



@csrf_exempt
@login_required(login_url='login', redirect_field_name=None)
def upload_applications(request):
    if request.POST.get("upload-applications"):
        # position_id = int(request.POST.get("position-id"))
        form = ImportApplicationsForm(request.POST, request.FILES)
        if form.is_valid():

            position_id = int(request.POST.get("position-id"))
            files = request.FILES.getlist('pdf')
            file_names = [
                FileSystemStorage().save(file.name, file) for file in files
            ]
            file_paths = [
                FileSystemStorage().url(file_name) for file_name in file_names
            ]
            # Call process applications task to execute in Celery
            task_result = process_applications.delay(file_paths, position_id)
            return redirect(position_detail,
                        Position.objects.get(id=position_id).reference_number,
                        position_id, task_result.id)
        # form.add_error('pdf', "w-oeuibfhwpioqubfwpi")
        # print(form)
        # return redirect(position_detail,
        #                 None,
        #                 position_id)
    # TODO: render error message that application could not be added
    return redirect('home')



def import_applications_redact(request):
    if request.method == 'POST':
        form = ImportApplicationsForm(request.POST, request.FILES)
        if form.is_valid():
            redact_applications()
            # Call application parser logic here##
            return render(request,
                          'importapplications/applications.html#applications',
                          {'form': form})
    form = ImportApplicationsForm()
    return render(request, 'importapplications/applications.html',
                  {'form': form})


def task_status(request, task_id):
    if task_id is not None:
        task = AsyncResult(task_id)
        if task is not None:
            try:
                response_data = {
                    'state': task.state,
                    'meta': task.info,
                }
            except TypeError:
                response_data = {
                    'state': "FAILURE",
                    'meta': None,
                }
            return JsonResponse(response_data)
    return None