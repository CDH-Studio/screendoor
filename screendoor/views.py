from string import digits
from django.http import HttpResponse
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required

from .uservisibletext import InterfaceText, CreateAccountFormText, PositionText, PositionsViewText, LoginFormText
from django.utils.translation import gettext as _
from screendoor.redactor import parse_applications
from .forms import ScreenDoorUserCreationForm, LoginForm, CreatePositionForm, ImportApplicationsForm
from .models import EmailAuthenticateToken, Position
from screendoor.parseposter import parse_upload


# Each view is responsible for doing one of two things: returning an HttpResponse object containing the content for
# the requested page, or raising an exception such as Http404.


# @login_required
# The login_required decorator redirects unauthenticated sessions to 'settings.LOGIN_URL'

@login_required(login_url='login/', redirect_field_name=None)
def index(request):
    return redirect('positions')
    # Returns main page
    return render(request, 'index.html',
                  {'user': request.user, 'baseVisibleText': InterfaceText})


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


def send_user_email(request, user):
    url = generate_confirmation_url(request, user)
    mail_sent = send_mail(
        'ScreenDoor: Please confirm e-mail address',
        'Please visit the following URL to confirm your account: ' + url,
        'screendoor@screendoor.ca',
        # Address: should be user.email
        [user.email],
        fail_silently=False,
    )


def generate_confirmation_url(request, user):
    token = EmailAuthenticateToken()
    token.user = user
    token.create_key()
    token.save()
    # TODO: generate first part of URL programmatically not as hardcoded string
    return "http://localhost:8000/confirm?key=" + str(token.key)


def login_form(request):
    # If user is not logged in, display login form
    if not request.user.is_authenticated:
        form = LoginForm()
        # Has the user hit login button
        if request.method == 'POST':
            # Clears any GET data
            request.GET._mutable = True
            request.GET['key'] = None
            request.GET._mutable = False
            # Instantiate form object
            form = LoginForm(request.POST)
            # Validates form and persists username data
            if form.is_valid():
                user = form.get_user()
                login(request, user)
                return redirect('home')
        if request.GET.get('key') is not None:
            account_key = request.GET.get('key')
            # Is the token valid in the database
            if EmailAuthenticateToken.objects.filter(key=account_key).exists():
                token = EmailAuthenticateToken.objects.get(key=account_key)
                user = token.user
                user.email_confirmed = True
                user.save()
                token.delete()
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


@login_required(login_url='/login/', redirect_field_name=None)
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required(login_url='/login/', redirect_field_name=None)
def import_position(request):
    if request.method == 'POST':
        # if request.POST.get("upload-position"):
        # valid form
        create_position_form = CreatePositionForm(
            request.POST, request.FILES)
        if create_position_form.is_valid():
            # don't commit partial positions with only pdf/url into db
            position = create_position_form.save(commit=False)
            d = parse_upload(position)
            errors = d.get('errors')
            if errors:
                create_position_form.add_error('pdf', errors)
            # second check
            if create_position_form.is_valid():
                position = d.get('position')
                # Persist position ID in session for saving and editing
                request.session['position_id'] = position.id
                # Successful render of a position
                return render(request, 'createposition/importposition.html',
                              {'position': position, 'form': create_position_form,
                               'baseVisibleText': InterfaceText,
                               'userVisibleText': PositionText})

            # Default view for a form with errors
            return render(request, 'createposition/importposition.html',
                          {'form': create_position_form,
                           'baseVisibleText': InterfaceText,
                           'userVisibleText': PositionText})
        if request.POST.get("save-position"):
            position = Position.objects.get(id=request.session['position_id'])
            request.user.positions.add(position)
            return redirect('home')
    # view for a GET request instead of a POST request
    create_position_form = CreatePositionForm()
    return render(request, 'createposition/importposition.html', {
        'form': CreatePositionForm, 'baseVisibleText': InterfaceText
    })


@login_required(login_url='/login/', redirect_field_name=None)
def positions(request):
    try:
        sort_by = request.session['position_sort']
    except KeyError:
        sort_by = '-created'
    if request.method == 'POST':
        if request.POST.get("sort-created"):
            sort_by = '-created'
        elif request.POST.get("sort-closed"):
            sort_by = '-date_closed'
        elif request.POST.get("sort-position"):
            sort_by = 'position_title'
        elif request.POST.get("position"):
            return position(request, Position.objects.get(
                id=request.POST.get("id")))
        elif request.POST.get("delete"):
            Position.objects.get(
                id=request.POST.get("id")).delete()

    request.session['position_sort'] = sort_by
    return render(request, 'positions.html', {
        'baseVisibleText': InterfaceText, 'positionText': PositionText, 'userVisibleText': PositionsViewText, 'positions': request.user.positions.all().order_by(sort_by), 'sort': request.session['position_sort']
    })


@login_required(login_url='/login/', redirect_field_name=None)
def position(request, position):
    return render(request, 'position.html', {
        'baseVisibleText': InterfaceText, 'positionText': PositionText, 'userVisibleText': PositionsViewText, 'position': position
    })


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
