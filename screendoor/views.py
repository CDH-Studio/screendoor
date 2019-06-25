import json

from string import digits
from dateutil import parser as dateparser

from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect

from celery.result import AsyncResult

from .uservisibletext import InterfaceText, CreateAccountFormText, PositionText, PositionsViewText, LoginFormText, \
    ApplicantViewText
from .forms import ScreenDoorUserCreationForm, LoginForm, CreatePositionForm, ImportApplicationsForm
from .models import EmailAuthenticateToken, Position, Applicant, Education, FormAnswer, Stream, Classification
from .tasks import process_applications
from .parseposter import parse_upload
from .redactor import redact_applications


# Each view is responsible for doing one of two things: returning an HttpResponse object containing the content for
# the requested page, or raising an exception such as Http404.
# The @login_required decorator redirects unauthenticated sessions to 'settings.LOGIN_URL' or the specified URL


# Index currently redirects to the positions view if logged in
@login_required(login_url='login', redirect_field_name=None)
def index(request):
    return redirect('positions')
    # Returns main page
    return render(request, 'index.html',
                  {'user': request.user, 'baseVisibleText': InterfaceText})


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
            return render(request, 'registration/register.html',
                          {'register_form': register_form,
                           'account_created': format(CreateAccountFormText.account_created % user)})
    # Returns form page
    return render(request, 'registration/register.html',
                  {'register_form': register_form})


# Creates and returns user object from request data
def create_account(request):
    # Creates account and saves email, password, username to database
    user = get_user_model().objects.create_user(
        request.POST['email'].lower(), password=request.POST['password1'], email=request.POST['email'].lower())
    # Extrapolate first and last name from e-mail account (experimental)
    user.first_name = request.POST['email'].split('.')[0].title()
    user.last_name = request.POST['email'].split(
        '.')[1].split('@')[0].title().translate({ord(n): None for n in digits})
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
    return "http://localhost:8000/confirm?key=" + str(token.key)


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
                return render(request, 'registration/login.html',
                              {'login_form': form,
                               'account_confirmed': format(LoginFormText.account_confirmed % user.email)})
            # Display validation error message
            return render(request, 'registration/login.html',
                          {'login_form': form, 'validation_error': LoginFormText.validation_error})
        # Display login page
        return render(request, 'registration/login.html',
                      {'login_form': form})
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
    request.user.positions.add(Position.objects.get(
        id=request.session['position_id']))


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
                position.salary_min = request.POST.get(
                    "position-salary-range").split("$")[1].split("-")[0]
                position.salary_max = request.POST.get(
                    "position-salary-range").split("-")[1].split("$")[1]
                position.open_to = request.POST.get("position-open-to")
                position.description = request.POST.get("position-description")
                counter = 1
                for requirement in position.requirement_set.all().reverse():
                    requirement.description = request.POST.get(
                        "position-requirement" + str(counter)).split(":")[1]
                    counter += 1
                    requirement.save()
                position.save()
                return redirect('position', position.reference_number, position.id)
            except TypeError:
                # In case of errors, return the current position with no edits
                # TODO: implement validation for position editing and error messages
                return Position.objects.get(
                    id=request.POST.get("position-id"))


# Displays form allowing users to upload job posting PDF files and URLs
@login_required(login_url='login', redirect_field_name=None)
def import_position(request):
    if request.method == 'POST':
        create_position_form = CreatePositionForm(
            request.POST, request.FILES)
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
                return render(request, 'createposition/importposition.html',
                              {'position': position, 'form': create_position_form,
                               'baseVisibleText': InterfaceText,
                               'userVisibleText': PositionText})
            # Display errors
            return render(request, 'createposition/importposition.html',
                          {'form': create_position_form,
                           'baseVisibleText': InterfaceText,
                           'userVisibleText': PositionText})
        # User pressed save button on uploaded and parsed position
        if request.POST.get("save-position"):
            save_position_to_user(request)
            edit_position(request)
            return redirect('home')
    # Default view for GET request
    create_position_form = CreatePositionForm()
    return render(request, 'createposition/importposition.html', {
        'form': CreatePositionForm, 'baseVisibleText': InterfaceText
    })


# Gets user's persisted positions sort method, or returns default
def get_positions_sort_method(request):
    try:
        return request.session['position_sort']
    except KeyError:
        return '-created'


# Changes positions sort method
def change_positions_sort_method(request, sort_by):
    if request.POST.get("sort-created"):
        return '-created'
    elif request.POST.get("sort-closed"):
        return '-date_closed'
    elif request.POST.get("sort-position"):
        return 'position_title'
    return sort_by


# Data and visible text to render with positions list view
def positions_list_data(request, sort_by):
    return {
        'baseVisibleText': InterfaceText, 'positionText': PositionText, 'userVisibleText': PositionsViewText,
        'applicationsForm': ImportApplicationsForm, 'positions': request.user.positions.all().order_by(sort_by),
        'sort': request.session['position_sort']
    }


# View of all positions associated with a user account
@login_required(login_url='login', redirect_field_name=None)
def positions(request):
    # Order of positions display
    sort_by = get_positions_sort_method(request)
    if request.method == 'POST':
        sort_by = change_positions_sort_method(request, sort_by)
    # Persists positions sorting
    request.session['position_sort'] = sort_by
    # Displays list of positions
    return render(request, 'positions.html', positions_list_data(request, sort_by))


# Return whether the position exists and the user has access to it
def user_has_position(request, reference, position_id):
    if Position.objects.filter(reference_number=reference).exists() and request.user.positions.filter(
            reference_number=reference).exists():
        return Position.objects.get(id=position_id)
    return None


# Data and visible text to render with positions
def position_detail_data(request, position):
    # Implement logic for viewing applicant "scores"
    applicants = list(Applicant.objects.filter(parent_position=position))
    for applicant in applicants:
        applicant.number_questions = FormAnswer.objects.filter(
            parent_applicant=applicant).count()
        applicant.number_yes_responses = FormAnswer.objects.filter(
            parent_applicant=applicant, applicant_answer=True).count()
        applicant.percentage_correct = applicant.number_yes_responses * \
            100 // applicant.number_questions
        applicant.classifications_set = Classification.objects.filter(
            parent_applicant=applicant)
        applicant.streams_set = Stream.objects.filter(
            parent_applicant=applicant)
    # Default sorting: higher scores at the top
    applicants.sort(
        key=lambda applicant: applicant.number_yes_responses, reverse=True)
    return {'baseVisibleText': InterfaceText, 'applicationsForm': ImportApplicationsForm, 'positionText': PositionText,
            'userVisibleText': PositionsViewText, 'position': position, 'applicants': applicants, }


# Position detail view
@login_required(login_url='login', redirect_field_name=None)
def position_detail(request, reference, position_id):
    # GET request
    try:
        position = user_has_position(request, reference, position_id)
        if position is not None:
            return render(request, 'position.html', position_detail_data(request, position))
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
            form.save()
            position_id = int(request.POST.get("position-id"))
            position = Position.objects.get(id=position_id)
            files = request.FILES.getlist('pdf')
            file_paths = [str(file.temporary_file_path()) for file in files]
            task_result = process_applications.run(
                list(file_paths), position_id)
        return redirect('position', position.reference_number, position.id)
    # TODO: render error message that application could not be added
    return redirect('home')


def import_applications_redact(request):
    if request.method == 'POST':
        form = ImportApplicationsForm(request.POST, request.FILES)
        if form.is_valid():
            redact_applications()
            # Call application parser logic here##
            return render(request, 'importapplications/applications.html#applications', {
                'form': form})
    form = ImportApplicationsForm()
    return render(request, 'importapplications/applications.html', {
        'form': form})


# Verify that the applicant exists and belongs to position that user has access to
def position_has_applicant(request, app_id):
    if Applicant.objects.filter(applicant_id=app_id).exists() and user_has_position(request, Applicant.objects.get(
        applicant_id=app_id).parent_position.reference_number, Applicant.objects.get(
            applicant_id=app_id).parent_position.id):
        return Applicant.objects.get(applicant_id=app_id)


# Data for applicant view
def applicant_detail_data(applicant, position):
    answers = FormAnswer.objects.filter(parent_applicant=applicant)
    number_questions = len(answers)
    number_yes_responses = FormAnswer.objects.filter(
        parent_applicant=applicant, applicant_answer=True).count()
    number_no_responses = FormAnswer.objects.filter(
        parent_applicant=applicant, applicant_answer=False).count()
    percentage_correct = number_yes_responses * 100 // number_questions
    return {'baseVisibleText': InterfaceText, 'applicationsForm': ImportApplicationsForm, 'position': position,
            'applicant': applicant, 'educations': Education.objects.filter(parent_applicant=applicant),
            'classifications': Classification.objects.filter(parent_applicant=applicant),
            'streams': Stream.objects.filter(parent_applicant=applicant), 'applicantText': ApplicantViewText,
            'answers': answers, 'number_questions': number_questions, 'number_yes_responses': number_yes_responses,
            'number_no_responses': number_no_responses, 'percentage_correct': percentage_correct}


# View an application
@login_required(login_url='login', redirect_field_name=None)
def application(request, app_id):
    applicant = position_has_applicant(request, app_id)
    if applicant is not None:
        return render(request, 'application.html',
                      applicant_detail_data(applicant, Applicant.objects.get(applicant_id=app_id).parent_position))
    # TODO: render error message that the applicant trying to be access is unavailable/invalid
    return redirect('home')


def get_task_status(request, task_id):
    task = AsyncResult(task_id)
    response_data = {
        'state': task.state,
        'details': task.info,
    }
    return HttpResponse(json.dumps(response_data), content_type='application/json')


def nlp(request):
    text = u"""Some of the IM/IT projects I have managed at PCO since June 2014:
Project 1 - Upgrade of the department-wide Electronic Document Management System (eDOCS 5.3.1 software) on two corporate
networks (825 users)
As IM Systems lead, I managed my team's functional testing and troubleshooting activities of the upgraded EDMS software and all
interactions with the information technology (IT) programmers for two networks (Protected B and Secret). I informed business group
representatives (stakeholders) weekly of progress through conference calls and in person meetings when required.
Project 2 - Remote deployment of the new eDOCS software package on the Protected network
I oversaw the deployment of the software to 30 business groups, totalling close to 500 users via SCCM, managing the work of my staff
and individuals in the IT directorate responsible for the packaging of the software and its remote deployment, I also engaged business
unit representatives to ensure a transparent and easy process.
Project 3 - Onboarding of two clients groups onto the EDMS (RDIMS)
I managed the deployment of the EDMS (RDIMS/eDOCS) to two new client groups (150 users), directing the work of my staff for all
onboarding activities (filing structure evaluation, access groups configurations, training, etc.) and engaging key personnel in the client
and IM Policy groups, when needed.
At OCOL between March 2010 and June 2014:
Project 1 - Pilot of a new department-wide Electronic Document and Records Management System (EDRMS) to the Corporate
Services Branch (50 users)
As the IM Lead (stakeholder) on a major IM/IT Integrated Electronic Management Solution (IEMS) project, which included GCDOCS
as our EDRMS base Module 1 (Module 2 - Case Management, Module 3 - Web Management), I managed the pilot deployment of the
EDRMS (GCDOCS) to the Corporate Management Branch and managed the work of consultants and my staff, including presentations
and training activities.
Project 2 - Department-wide implementation of EDRMS - GCDOCS/Content Server 10
As the IM Lead (stakeholder) on the same major IM/IT project, I also facilitated the department-wide implementation of the EDRMS
(GCDOCS), including one-on-one meetings with business process owners (EX-01 level) to inform them of the implementation
progress, organised and offered client training, negotiating with clients regarding system integration, configuration and access
permissions, providing one-on-one coaching sessions, when needed.
Project 3 - Department-wide training on the new EDRMS (GCDOCS/Content Server 10)
I facilitated the department-wide implementation of the EDRMS by managing the department-wide training efforts to all our offices
throughout Canada, overseeing sessions given by consultants and my staff offering training and coaching myself on occasion.
Project 4 - Information Frameworks
As the IM Lead, I managed the validation of Information Frameworks for OCOL's 17 business processes, initiated consultations with
business process owners and aligned the IM Framework within the architecture of the Electronic Document Management System
(GCDOCS), as well as the filing scheme and retention periods.
I also:
- Managed the upgrade of the Library system, from Portfolio 6 to Portfolio 7 and Zones 2, including client testing.
- Managed the implementation of e-copy software to facilitate ATIP processes.
- Lead the development, revamp and implementation of Library services (ex. Catalogue upgrade, online subscriptions, orientation
sessions, new acquisitions list, etc.)
- Managed the weeding process of the Library's paper collection in view of a March 2014 physical move.
- Managed the physical move of the Records Management office in March 2014.
- Managed the physical move of the Library in March 2014."""
    from screendoor.NLP.whenextraction import extract_dates
    from screendoor.NLP.howextraction import extract_how
    extract_dates(text)
    extract_how(text)
    return redirect('positions')
