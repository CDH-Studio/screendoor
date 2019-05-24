from string import digits
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _

from .forms import ScreenDoorUserCreationForm, LoginForm, LogoutForm

# Each view is responsible for doing one of two things: returning an HttpResponse object containing the content for the requested page, or raising an exception such as Http404.


# @login_required
# The login_required decorator redirects unauthenticated sessions to settings.LOGIN_URL

@login_required(login_url='login/', redirect_field_name=None)
def index(request):
    # Returns main page
    return render(request, 'index.html',
                  {'user': request.user})


def register_form(request):
    register_form = ScreenDoorUserCreationForm
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        register_form = ScreenDoorUserCreationForm(request.POST)
        # check whether it's valid
        if register_form.is_valid():
            email_domain = request.POST['email'].split('@')[1].lower()
            email_error = False
            password_error = False
            # Warning message for invalid e-mail domain
            if email_domain != "canada.ca" and email_domain != "algonquinlive.com":
                messages.warning(request, format(
                    _('Invalid e-mail address domain: %s. Canada.ca email required.') % email_domain))
                email_error = True
            # Warning message for duplicate username/email
            elif get_user_model().objects.filter(username=request.POST['email']).exists():
                messages.warning(request, _(
                    'Username %s already exists.') % request.POST['email'])
                email_error = True
            # # Warning message for mismatched password fields
            # if request.POST['password'] != request.POST['password_repeat']:
            #     messages.warning(request, _(
            #         'Password confirmation does not match original.'))
            #     password_error = True
            # Success
            if (not email_error and not password_error):
                create_account(request)
    # Returns form page
    return render(request, 'registration/register.html',
                  {'register_form': register_form})


def send_user_email(request):
    None


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
    # Redirect to login screen
    return redirect('login')


def login_form(request):
    # Instantiate form object
    login_form = LoginForm(request.POST)
    # Has the user hit login button
    if request.method == 'POST':
        # Validate form and persists username data
        if login_form.is_valid():
            # Returns not null if username and password match a user
            user = authenticate(
                username=request.POST['email'].lower(), password=request.POST['password'])
            # Does user with this email and password exist
            if user is not None:
                # Has user confirmed e-mail address
                if user.email_confirmed == False:
                    messages.warning(request, _(
                        'Email address for user not confirmed.'))
                # Login successfully
                else:
                    login(request, user)
                    return redirect('home')
            # Display warning
            else:
                messages.warning(request, _('Invalid username or password.'))
    # Display login page
    return render(request, 'registration/login.html',
                  {'login_form': login_form})


def logout_view(request):
    logout(request)
    return redirect('login')

# Exceptions - shortcut: get_object_or_404()
# e.g.     question = get_object_or_404(Question, pk=question_id)


# Reverse function
# return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
# reverse function belongs to HttpResponseRedirect constructor.
# Given name of the view we want to pass control to, and the variable portion
# of the URL pattern that points to that view (plus arguments).


# View component reuse: generic views
