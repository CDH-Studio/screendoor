from io import BytesIO
from string import digits

from celery.result import AsyncResult
from dateutil import parser as dateparser
from django.contrib.auth import get_user_model
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import FileSystemStorage
from django.core.mail import send_mail
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.template import Context
from django.template.loader import get_template, render_to_string
from django.views.decorators.csrf import csrf_exempt
from weasyprint import HTML
from weasyprint.fonts import FontConfiguration

from .forms import ScreenDoorUserCreationForm, LoginForm, CreatePositionForm, ImportApplicationsForm
from .models import EmailAuthenticateToken, Position, Applicant, Education, FormAnswer, Stream, Classification, \
    NlpExtract, Note, Qualifier, ScreenDoorUser
from .parseposter import parse_upload
from .redactor import redact_applications
from .tasks import process_applications
from .uservisibletext import InterfaceText, CreateAccountFormText, PositionText, PositionsViewText, LoginFormText, \
    ApplicantViewText

# Each view is responsible for doing one of two things: returning an HttpResponse object containing the content for
# the requested page, or raising an exception such as Http404.
# The @login_required decorator redirects unauthenticated sessions to 'settings.LOGIN_URL' or the specified URL


# Index currently redirects to the positions view if logged in
@login_required(login_url='login', redirect_field_name=None)
def index(request):
    return redirect('positions')
    # Returns main page
    return render(request, 'index.html', {
        'user': request.user,
        'baseVisibleText': InterfaceText
    })


# Renders account registration form
def register_form(request):
    register_form = ScreenDoorUserCreationForm()
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        register_form = ScreenDoorUserCreationForm(request.POST)
        # check whether form data is valid
        if register_form.is_valid():
            # Create user
            user = create_account(request)
            # Send confirmation e-mail
            send_user_email(request, user)
            # Redirects to...
            return render(
                request, 'registration/register.html', {
                    'register_form':
                    register_form,
                    'account_created':
                    format(CreateAccountFormText.account_created % user)
                })
    # Returns form page
    return render(request, 'registration/register.html',
                  {'register_form': register_form})


# Creates and returns user object from request data
def create_account(request):
    # Creates account and saves email, password, username to database
    user = get_user_model().objects.create_user(
        request.POST['email'].lower(),
        password=request.POST['password1'],
        email=request.POST['email'].lower())
    # Extrapolate first and last name from e-mail account (experimental)
    user.first_name = request.POST['email'].split('.')[0].title()
    user.last_name = request.POST['email'].split('.')[1].split(
        '@')[0].title().translate({ord(n): None
                                   for n in digits})
    # Set user as inactive until e-mail confirmation
    user.email_confirmed = False
    # Save updated user info to database
    user.save()
    return user


# Sends account confirmation e-mail to user
# Currently sends mock e-mail via console
def send_user_email(request, user):
    url = generate_confirmation_url(request, user)
    send_mail(
        'ScreenDoor: Please confirm e-mail address',
        'Please visit the following URL to confirm your account: ' + url,
        'screendoor@screendoor.ca',
        # Address: should be user.email
        [user.email],
        fail_silently=False,
    )


# Creates and returns a working account confirmation URL
def generate_confirmation_url(request, user):
    token = EmailAuthenticateToken()
    token.user = user
    token.create_key()
    token.save()
    # TODO: generate first part of URL programmatically not as hardcoded string
    return "http://localhost/confirm?key=" + str(token.key)


# Clears any GET data, i.e. account confirmation token string from URL
def clear_get_data(request):
    # Clears any GET data
    request.GET._mutable = True
    request.GET['key'] = None
    request.GET._mutable = False


# Returns true if user authentication token is valid and userhas been validated and saved
def authenticate_user(account_key):
    # If authentication key is valid, activate user and delete authentication token
    if EmailAuthenticateToken.objects.filter(key=account_key).exists():
        token = EmailAuthenticateToken.objects.get(key=account_key)
        user = token.user
        user.email_confirmed = True
        user.save()
        token.delete()
        return user
    return None


# Displays form for user login and calls validation methods
def login_form(request):
    # If user is not logged in, display login form
    if not request.user.is_authenticated:
        form = LoginForm()
        # Has the user hit login button
        if request.method == 'POST':
            clear_get_data(request)
            # Instantiate form object
            form = LoginForm(request.POST)
            # Validates form and persists username data
            if form.is_valid():
                user = form.get_user()
                # Logs in and redirects user
                login(request, user)
                return redirect('home')
        if request.GET.get('key') is not None:
            # Check if authentication key is valid
            user = authenticate_user(request.GET.get('key'))
            if (user is not None):
                # Display account confirmation message
                return render(
                    request, 'registration/login.html', {
                        'login_form':
                        form,
                        'account_confirmed':
                        format(LoginFormText.account_confirmed % user.email)
                    })
            # Display validation error message
            return render(
                request, 'registration/login.html', {
                    'login_form': form,
                    'validation_error': LoginFormText.validation_error
                })
        # Display login page
        return render(request, 'registration/login.html', {'login_form': form})
    # If the user is already logged in, redirect to home
    return redirect('home')


# Logs out user
@login_required(login_url='login', redirect_field_name=None)
def logout_view(request):
    logout(request)
    return redirect('login')


# Run parse upload script and return dictionary
def parse_position_return_dictionary(create_position_form):
    # don't commit partial positions with only pdf/url into db
    return parse_upload(create_position_form.save(commit=False))


# Adds position to user data
def save_position_to_user(request):
    request.user.positions.add(
        Position.objects.get(id=request.session['position_id']))


@login_required(login_url='login', redirect_field_name=None)
def edit_position(request):
    if request.method == 'POST':
        # User wants to edit a position
        if request.POST.get("save-position"):
            try:
                # Populate the fields with hidden input data from position template
                position = Position.objects.get(
                    id=request.POST.get("position-id"))
                position.position_title = request.POST.get("position-title")
                position.classification = request.POST.get(
                    "position-classification")
                position.reference_number = request.POST.get(
                    "position-reference")
                position.selection_process_number = request.POST.get(
                    "position-selection")
                position.date_closed = dateparser.parse(
                    request.POST.get("position-date-closed"))
                position.num_positions = request.POST.get(
                    "position-num-positions")
                position.salary = request.POST.get("position-salary")
                position.open_to = request.POST.get("position-open-to")
                position.description = request.POST.get("position-description")
                counter = 1
                for requirement in position.requirement_set.all().reverse():
                    requirement.description = request.POST.get(
                        "position-requirement" + str(counter))
                    counter += 1
                    requirement.save()
                position.save()
                return redirect('position', position.reference_number,
                                position.id)
            except TypeError:
                # In case of errors, return the current position with no edits
                # TODO: implement validation for position editing and error messages
                return Position.objects.get(id=request.POST.get("position-id"))


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
            # edit_position(request)
            return redirect('home')
    # Default view for GET request
    create_position_form = CreatePositionForm()
    return render(request, 'createposition/importposition.html', {
        'form': CreatePositionForm,
        'baseVisibleText': InterfaceText
    })


@login_required(login_url='login', redirect_field_name=None)
def filter_applicants(request, reference, position_id, applicant_filter):
    request.session['applicant_filter'] = applicant_filter
    return redirect('position', reference=reference, position_id=position_id)


@login_required(login_url='login', redirect_field_name=None)
def sort_applicants(request, reference, position_id, sort_by):
    request.session['applicants_sort'] = sort_by
    return redirect('position', reference=reference, position_id=position_id)


@login_required(login_url='login', redirect_field_name=None)
def sort_positions(request, sort_by):
    # Persists positions sorting
    request.session['position_sort'] = sort_by
    return redirect('positions')


# Gets user's persisted positions sort method, or returns default
def get_positions_sort_method(request):
    try:
        return request.session['position_sort']
    except KeyError:
        return '-created'


# Gets user's persisted applicants sort method, or returns default
def get_applicants_sort_method(request):
    try:
        return request.session['applicants_sort']
    except KeyError:
        return '-percentage_correct'


def get_applicant_filter_method(request):
    try:
        return request.session['applicant_filter']
    except KeyError:
        return "all"


# Data and visible text to render with positions list view
def positions_list_data(request):
    # Order of positions display
    sort_by = get_positions_sort_method(request)
    # Get positions according to specific sorting
    positions = request.user.positions.all().order_by(sort_by)
    # Attach applicants to position object if exist
    for position in positions:
        position.applicants = Applicant.objects.filter(
            parent_position=position) if Applicant.objects.filter(
                parent_position=position).count() > 0 else None
    # Return data for display
    return {
        'baseVisibleText': InterfaceText,
        'positionText': PositionText,
        'userVisibleText': PositionsViewText,
        'applicationsForm': ImportApplicationsForm,
        'positions': positions,
        'sort': sort_by
    }


# View of all positions associated with a user account
@login_required(login_url='login', redirect_field_name=None)
def positions(request):
    # Displays list of positions
    return render(request, 'positions.html', positions_list_data(request))


# Return whether the position exists and the user has access to it
def user_has_position(request, reference, position_id):
    if Position.objects.filter(reference_number=reference).exists(
    ) and request.user.positions.filter(reference_number=reference).exists():
        return Position.objects.get(id=position_id)
    return None


# Data and visible text to render with positions
def position_detail_data(request, position_id, task_id):
    applicant_filter = get_applicant_filter_method(request)
    sort_by = get_applicants_sort_method(request)
    position = Position.objects.get(id=position_id)
    if applicant_filter == "all":
        applicants = list(position.applicant_set.all().order_by(
            sort_by)) if Applicant.objects.filter(
                parent_position=position).count() > 0 else []
    elif applicant_filter == "favourites":
        applicants = list(
            request.user.favourites.filter(parent_position=position).order_by(
                sort_by)) if request.user.favourites.filter(
                    parent_position=position).count() > 0 else []
    favourites = request.user.favourites.filter(parent_position=position)
    applicant_dict = create_applicants_wth_favourite_information(
        applicants, favourites)
    for applicant in applicants:
        applicant.classifications_set = Classification.objects.filter(
            parent_applicant=applicant)
        applicant.streams_set = Stream.objects.filter(
            parent_applicant=applicant)

    other_users = [
        x for x in position.position_users.all() if not x == request.user
    ]
    print(other_users)
    return {
        'baseVisibleText': InterfaceText,
        'applicationsForm': ImportApplicationsForm,
        'positionText': PositionText,
        'userVisibleText': PositionsViewText,
        'position': position,
        'applicants': applicant_dict,
        'task_id': task_id,
        'sort': sort_by,
        'current_user': request.user,
        'other_users': other_users,
        'applicant_filter': applicant_filter
    }


def create_applicants_wth_favourite_information(applicants, favourites):
    stitched_lists = {}
    for applicant in applicants:
        if applicant in favourites:
            stitched_lists[applicant] = True
        else:
            stitched_lists[applicant] = False
    return stitched_lists


# Position detail view
@login_required(login_url='login', redirect_field_name=None)
def position_detail(request, reference, position_id, task_id=None):
    # GET request
    try:
        position = user_has_position(request, reference, position_id)
        if position is not None:
            return render(request, 'position.html',
                          position_detail_data(request, position.id, task_id))
    except ObjectDoesNotExist:
        # TODO: add error message that position cannot be retrieved
        return redirect('home')


@login_required(login_url='login', redirect_field_name=None)
def delete_position(request):
    # User wants to delete position
    if request.POST.get("delete"):
        Position.objects.get(id=request.POST.get("position-id")).delete()
    # TODO: render error that position could not be deleted
    return redirect('home')


@csrf_exempt
@login_required(login_url='login', redirect_field_name=None)
def upload_applications(request):
    if request.POST.get("upload-applications"):
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
        return redirect('position_upload',
                        Position.objects.get(id=position_id).reference_number,
                        position_id, task_result.id)
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


# Verify that the applicant exists and belongs to position that user has access to
def position_has_applicant(request, app_id):
    if Applicant.objects.filter(
            applicant_id=app_id).exists() and user_has_position(
                request,
                Applicant.objects.get(
                    applicant_id=app_id).parent_position.reference_number,
                Applicant.objects.get(applicant_id=app_id).parent_position.id):
        return Applicant.objects.get(applicant_id=app_id)


# Data for applicant view
def applicant_detail_data(request, applicant_id, position_id):

    applicant = Applicant.objects.get(id=applicant_id)
    if [x for x in request.user.favourites.all() if x == applicant]:
        is_favourited = True
    else:
        is_favourited = False

    print(is_favourited)
    position = Position.objects.get(id=position_id)
    answers = FormAnswer.objects.filter(
        parent_applicant=applicant).order_by("parent_question")
    for answer in answers:
        answer.qualifier_set = Qualifier.objects.filter(
            parent_answer=answer).order_by(
                'qualifier_type') if Qualifier.objects.filter(
                    parent_answer=answer).count() > 0 else None
        answer.extract_set = NlpExtract.objects.filter(
            parent_answer=answer).order_by(
                'next_extract_index',
                '-extract_type') if NlpExtract.objects.filter(
                    parent_answer=answer).count() > 0 else None
        answer.note_set = Note.objects.filter(
            parent_answer=answer).order_by('created') if Note.objects.filter(
                parent_answer=answer).count() > 0 else None
    return {
        'baseVisibleText':
        InterfaceText,
        'applicationsForm':
        ImportApplicationsForm,
        'position':
        position,
        'applicant':
        applicant,
        'educations':
        Education.objects.filter(parent_applicant=applicant),
        'classifications':
        Classification.objects.filter(parent_applicant=applicant),
        'streams':
        Stream.objects.filter(parent_applicant=applicant),
        'applicantText':
        ApplicantViewText,
        'answers':
        answers,
        "favourite":
        is_favourited
    }


# View an application
@login_required(login_url='login', redirect_field_name=None)
def application(request, app_id):
    applicant = position_has_applicant(request, app_id)
    if applicant is not None:
        return render(
            request, 'application.html',
            applicant_detail_data(
                request, applicant.id,
                Applicant.objects.get(applicant_id=app_id).parent_position.id))
    # TODO: render error message that the applicant trying to be access is unavailable/invalid
    return redirect('home')


# Add a note to an applicant answer
@login_required(login_url='login', redirect_field_name=None)
def add_note(request):
    if request.POST.get("note-input"):
        answer = FormAnswer.objects.get(id=request.POST.get("parent-answer"))
        note = Note(author=request.user,
                    parent_answer=answer,
                    note_text=request.POST.get("note-input"))
        note.save()
        return redirect('application', answer.parent_applicant.applicant_id)


# Delete a note
@login_required(login_url='login', redirect_field_name=None)
def delete_note(request):
    if request.POST.get("note-id"):
        answer = FormAnswer.objects.get(id=request.POST.get("parent-answer"))
        note = Note.objects.get(id=request.POST.get("note-id"))
        note.delete()
        return redirect('application', answer.parent_applicant.applicant_id)


@login_required(login_url='login', redirect_field_name=None)
def render_pdf(request, app_id):
    applicant = position_has_applicant(request, app_id)
    answers = FormAnswer.objects.filter(
        parent_applicant=applicant).order_by("parent_question")
    for answer in answers:
        answer.qualifier_set = Qualifier.objects.filter(
            parent_answer=answer).order_by(
                'qualifier_type') if Qualifier.objects.filter(
                    parent_answer=answer).count() > 0 else None
        answer.extract_set = NlpExtract.objects.filter(
            parent_answer=answer).order_by(
                'next_extract_index',
                '-extract_type') if NlpExtract.objects.filter(
                    parent_answer=answer).count() > 0 else None
        answer.note_set = Note.objects.filter(
            parent_answer=answer).order_by('created') if Note.objects.filter(
                parent_answer=answer).count() > 0 else None
    if applicant is not None:
        response = HttpResponse(content_type="application/pdf")
        html = render_to_string("sbr_pdf.html", {
            'applicant': applicant,
            'answers': answers
        })
        font_config = FontConfiguration()
        HTML(string=html).write_pdf(response, font_config=font_config)
        return response
    return redirect('home')


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


def nlp(request):
    answer = FormAnswer.objects.get(id=449)
    qualifiers = answer.qualifier_set.all()
    breakpoint()
    return redirect('positions')


def add_to_favourites(request):
    app_id = request.GET.get("app_id")
    applicant = Applicant.objects.get(applicant_id=app_id)
    favourite_status = request.GET.get("favouriteStatus")

    if favourite_status == "True":
        request.user.favourites.remove(applicant)
    else:
        request.user.favourites.add(applicant)

    request.user.save()
    return JsonResponse({
        'app_id': app_id,
        'favourite_status': favourite_status
    })


def add_user_to_position(request):
    user_email = request.GET.get("email")
    position_id = request.GET.get("id")
    position = Position.objects.get(id=position_id)

    try:
        new_user = ScreenDoorUser.objects.get(email=user_email)
        if new_user in position.position_users.all():
            return JsonResponse(
                {'exception': 'User already has access to this position.'})
        position.position_users.add(new_user)
        position.save()
        return JsonResponse({
            'userName': new_user.username,
            'userEmail': new_user.email
        })
    except:
        return JsonResponse({'exception': 'User does not exist.'})


def remove_user_from_position(request):
    user_email = request.GET.get("email")
    position_id = request.GET.get("id")
    position = Position.objects.get(id=position_id)

    try:
        user_to_remove = ScreenDoorUser.objects.get(email=user_email)
        position.position_users.remove(user_to_remove)
        position.save()
        return JsonResponse({'userEmail': user_email})

    except:
        return JsonResponse({})
