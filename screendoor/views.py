from string import digits
from dateutil import parser as dateparser
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required

from screendoor.parseapplication import parse_application
from .uservisibletext import InterfaceText, CreateAccountFormText, PositionText, PositionsViewText, LoginFormText
from .forms import ScreenDoorUserCreationForm, LoginForm, CreatePositionForm, ImportApplicationsForm, ImportApplicationsText
from .models import EmailAuthenticateToken, Position, Applicant, Education, Classification, Requirement
from screendoor.parseposter import parse_upload
from screendoor.redactor import redact_applications
import os

# Each view is responsible for doing one of two things: returning an HttpResponse object containing the content for
# the requested page, or raising an exception such as Http404.
# The @login_required decorator redirects unauthenticated sessions to 'settings.LOGIN_URL' or the specified URL


# Index currently redirects to the positions view if logged in
@login_required(login_url='login/', redirect_field_name=None)
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
@login_required(login_url='/login/', redirect_field_name=None)
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


def edit_position(request):
    try:
        # Populate the fields with hidden input data from position template
        position = Position.objects.get(
            id=request.POST.get("position-id"))
        position.position_title = request.POST.get("position-title")
        position.classification = request.POST.get("position-classification")
        position.reference_number = request.POST.get("position-reference")
        position.selection_process_number = request.POST.get(
            "position-selection")
        position.date_closed = dateparser.parse(
            request.POST.get("position-date-closed"))
        position.num_positions = request.POST.get("position-num-positions")
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
        return position
    except TypeError:
        # In case of errors, return the current position with no edits
        # TODO: implement validation for position editing and error messages
        return Position.objects.get(
            id=request.POST.get("position_id"))


# Displays form allowing users to upload job posting PDF files and URLs
@login_required(login_url='/login/', redirect_field_name=None)
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
           #  edit_position(request)
            save_position_to_user(request)
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
        'baseVisibleText': InterfaceText, 'positionText': PositionText, 'userVisibleText': PositionsViewText, 'applicationsForm': ImportApplicationsForm, 'positions': request.user.positions.all().order_by(sort_by), 'sort': request.session['position_sort']
    }


# View of all positions associated with a user account
@login_required(login_url='/login/', redirect_field_name=None)
def positions(request):
    # Order of positions display
    sort_by = get_positions_sort_method(request)
    if request.method == 'POST':
        sort_by = change_positions_sort_method(request, sort_by)
        # User wants to view position detail
        if request.POST.get("position"):
            return position_detail(request, Position.objects.get(
                id=request.POST.get("id")))
        # User wants to delete position
        elif request.POST.get("delete"):
            Position.objects.get(
                id=request.POST.get("id")).delete()
        # User wants to upload applications for a position
        elif request.POST.get("upload-applications"):
            upload_applications(request)
            return position_detail(request, Position.objects.get(
                id=request.POST.get("id")))
        # User wants to edit a position
        elif request.POST.get("edit-position"):
            return position_detail(request, edit_position(request))
    # Persists positions sorting
    request.session['position_sort'] = sort_by
    # Displays list of positions
    return render(request, 'positions.html', positions_list_data(request, sort_by))


# Data and visible text to render with positions
def position_detail_data(request, position):
    return {'baseVisibleText': InterfaceText, 'applicationsForm': ImportApplicationsForm, 'positionText': PositionText, 'userVisibleText': PositionsViewText, 'position': position, 'applications': position.applications}


# Position detail view
@login_required(login_url='/login/', redirect_field_name=None)
def position_detail(request, position):
    return render(request, 'position.html', position_detail_data(request, position))


def upload_applications(request):
    pos = Position.objects.get(
        id=request.POST.get("id"))

    pdf = request.FILES['pdf']
    with open('/code/applications/' + pdf.name, 'wb+') as destination:
        for chunk in pdf.chunks():
            destination.write(chunk)

    form = ImportApplicationsForm(request.POST, request.FILES)
    if form.is_valid():
        applications = parse_application(form.save(commit=False))
        pos.save()
        for applicant in applications:
            pos.applications.add(applicant)

        pos.save()
        os.chdir("..")
        os.remove("/code/applications/" + pdf.name)


def import_applications(request):
    if request.method == 'POST':

        form = ImportApplicationsForm(request.POST, request.FILES)
        if form.is_valid():
            breakpoint()
            redact_applications()
            # Call application parser logic here##

            return render(request, 'importapplications/applications.html', {
                'form': form})

    form = ImportApplicationsForm()
    return render(request, 'importapplications/applications.html', {
        'form': form})


def nlp(request):
    text = u"""During my employment at CRA as a permanent IT Project Leader from January 2010 until present, I provided strategic advice and
recommendations on IM/IT risks or issues to my directors (EX1, EX3, and higher ) in relation to various legislated projects such as
Foreign Account Tax Compliance Act (FATCA), Electronic Funds Transfer (EFT) and Charities Internet applications.
For the Charities Internet application, I provided recommendations and briefings to senior management on how to protect CRA and
minimize the risks of cyber-attacks by developing a pre-emption process. The goal was to minimize the effects of the attack on the
Charities application.
For the FATCA project, I developed corporate strategies and reccomendations to senior management resulted in new and improved
services (e.g. in-house development tools for data compression and encryption, and in-house development tools for data conversion).
I liaised with Technology Advisors, Architects and Security Specialists to produce architecture and security recommendations, for the
FATCA project.
For the FATCA and EFT projects, I prepared Solutions dashboards and Project Gating reports and hosted meetings to obtain approval
from all gatekeepers and identified IM/IT issues and presented them to senior management (Ex01, EX02, and higher). I chaired IT
strategic meetings with clients and various stakeholders and created cost/benefit analyses, business cases, briefing notes, memos for
senior management (CS05, EX01). I presented at the Solutions Major Project Review Committee (MPRC) about the IM and IT issues
that requires immediate attention (such as procurement of the Sterling software - tracking system to track outgoing and incoming XML
file with ability of performing encryption and digital signature) with respect to FATCA project. I presented these recommendations to
the DAC (EX5), DG (EX3), and directors (CS05)."""
    from .NLP import test_spacy_functionality
    test_spacy_functionality(text)
    return redirect('positions')
