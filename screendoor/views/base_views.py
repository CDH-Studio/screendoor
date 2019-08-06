from string import digits

from django.contrib.auth import get_user_model
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import render, redirect

from screendoor.forms import ScreenDoorUserCreationForm, LoginForm
from screendoor.models import EmailAuthenticateToken
from screendoor.uservisibletext import InterfaceText, CreateAccountFormText, LoginFormText


# Index currently redirects to the positions view if logged in
@login_required(login_url='login', redirect_field_name=None)
def index(request):
    return redirect('positions')
    # Returns main page
    # return render(request, 'index.html', {
    #     'user': request.user,
    #     'baseVisibleText': InterfaceText
    # })


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