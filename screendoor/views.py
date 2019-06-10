from string import digits
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required

from .uservisibletext import InterfaceText, CreateAccountFormText, PositionText, PositionsViewText, LoginFormText
from .forms import ScreenDoorUserCreationForm, LoginForm, CreatePositionForm, ImportApplicationsForm, ImportApplicationsText
from .models import EmailAuthenticateToken, Position
from screendoor.parseposter import parse_upload
from screendoor.redactor import parse_applications


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
        return True
    return False


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
            if (authenticate_user(request.GET.get('key'))):
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
            return position(request, Position.objects.get(
                id=request.POST.get("id")))
        # User wants to delete position
        elif request.POST.get("delete"):
            Position.objects.get(
                id=request.POST.get("id")).delete()
        # User wants to upload applications for a position
        elif request.POST.get("upload-applications"):
            upload_applications(request)
            return position(request, Position.objects.get(
                id=request.POST.get("id")))
    # Persists positions sorting
    request.session['position_sort'] = sort_by
    # Displays list of positions
    return render(request, 'positions.html', positions_list_data(request, sort_by))


# Data and visible text to render with positions
def position_detail_data(request, position):
    return {'baseVisibleText': InterfaceText, 'applicationsForm': ImportApplicationsForm, 'positionText': PositionText, 'userVisibleText': PositionsViewText, 'position': position}


# Position detail view
@login_required(login_url='/login/', redirect_field_name=None)
def position(request, position):
    return render(request, 'position.html', position_detail_data(request, position))


def upload_applications(request):
    position = Position.objects.get(
        id=request.POST.get("id"))
    # form = ImportApplicationsForm(request.POST, request.FILES)
    # applications = import_applications(request)
    # position.applications.add(applications)
    # position.save()


def import_applications(request):
    if request.method == 'POST':
        form = ImportApplicationsForm(request.POST, request.FILES)
        if form.is_valid():
            breakpoint()
            parse_applications()
            # Call application parser logic here##

            return render(request, 'importapplications/applications.html', {
                'form': form})

    form = ImportApplicationsForm()
    return render(request, 'importapplications/applications.html', {
        'form': form})
