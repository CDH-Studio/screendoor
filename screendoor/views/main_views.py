from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from weasyprint import HTML
from weasyprint.fonts import FontConfiguration

from screendoor.forms import ImportApplicationsForm
from screendoor.models import Position, Applicant, Education, FormAnswer, Stream, Classification, \
    NlpExtract, Note, Qualifier
from screendoor.uservisibletext import InterfaceText, PositionText, PositionsViewText, ApplicantViewText, ToolTips
from .helper_views import get_positions_sort_method, get_applicants_sort_method, get_applicant_filter_method, user_has_position, position_has_applicant, create_applicants_wth_favourite_information


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


# Data and visible text to render with a position
def position_detail_data(request, position_id, task_id, error_msg):
    # Filter applicants by the last chosen method or default
    applicant_filter = get_applicant_filter_method(request)
    # Sort applicants by the last chosen methdod or default
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
    # Applicants the user has favourited
    favourites = request.user.favourites.filter(parent_position=position)
    # Dictionary of applicants with the favourites information
    applicant_dict = create_applicants_wth_favourite_information(
        applicants, favourites)
    # Attach streams and classifications to each applicant
    for applicant in applicants:
        applicant.classifications_set = Classification.objects.filter(
            parent_applicant=applicant)
        applicant.streams_set = Stream.objects.filter(
            parent_applicant=applicant)
    # Any other users with access to the position
    other_users = [
        x for x in position.position_users.all() if not x == request.user
    ]
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
        'applicant_filter': applicant_filter,
        'toolTips': ToolTips,
        'errorMsg': error_msg
    }


# Position detail view
@login_required(login_url='login', redirect_field_name=None)
def position_detail(request, reference, position_id, task_id=None):
    # GET request
    try:
        # Verify that user has access to position
        position = user_has_position(request, reference, position_id)
        if position is not None:
            return render(
                request, 'position.html',
                position_detail_data(request, position.id, task_id, None))
    except ObjectDoesNotExist:
        # Redirects user if position does not exist
        return redirect('home')


# Position detail view, which renders the upload application modal with the presence of an error message
# the above either renders the default page, or the processing view, depending on the prescence of the task id
@login_required(login_url='login', redirect_field_name=None)
def position_detail_with_upload_error(request,
                                      reference,
                                      position_id,
                                      error_msg=None):
    # GET request
    try:
        # Verify that user has access to position
        position = user_has_position(request, reference, position_id)
        if position is not None:
            return render(
                request, 'position.html',
                position_detail_data(request, position.id, None, error_msg))
    except ObjectDoesNotExist:
        # Redirects user if position does not exist
        return redirect('home')


@login_required(login_url='login', redirect_field_name=None)
def delete_position(request):
    # User wants to delete position
    if request.POST.get("delete"):
        Position.objects.get(id=request.POST.get("position-id")).delete()
    return redirect('home')


# Data for applicant view
def applicant_detail_data(request, applicant_id, position_id):

    applicant = Applicant.objects.get(id=applicant_id)
    # Determine whether applicant is in user's favourites list
    if [x for x in request.user.favourites.all() if x == applicant]:
        is_favourited = True
    else:
        is_favourited = False

    position = Position.objects.get(id=position_id)
    answers = FormAnswer.objects.filter(
        parent_applicant=applicant).order_by("parent_question")
    # Attach qualifiers, extracts, and notes to answer objects
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
        is_favourited,
        "toolTips":
        ToolTips
    }


# Applicant view using applicant_detail_data
@login_required(login_url='login', redirect_field_name=None)
def application(request, app_id):
    # Verify that applicant belongs to position held by user
    applicant = position_has_applicant(request, app_id)
    if applicant is not None:
        return render(
            request, 'application.html',
            applicant_detail_data(
                request, applicant.id,
                Applicant.objects.get(applicant_id=app_id).parent_position.id))
    return redirect('home')


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
