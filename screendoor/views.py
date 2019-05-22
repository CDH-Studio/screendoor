from string import digits
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _

from .forms import RegisterForm, LoginForm

# Each view is responsible for doing one of two things: returning an HttpResponse object containing the content for the requested page, or raising an exception such as Http404.


# @login_required
# The login_required decorator redirects unauthenticated sessions to settings.LOGIN_URL

@login_required
def index(request):
    return HttpResponse(_("Hello, world!"))


@login_required
def dashboard(request):
    return HttpResponse("Valid user logged in")


def register_form(request):
    register_form = RegisterForm
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        register_form = RegisterForm(request.POST)
        # check whether it's valid
        if register_form.is_valid():
            email_domain = request.POST['email'].split('@')[1].lower()
            email_error = False
            password_error = False
            # Warning message for invalid e-mail address
            if email_domain != "canada.ca":
                messages.warning(request, format(
                    _('Invalid e-mail address domain: %s. Canada.ca email required.') % email_domain))
                email_error = True
            # Warning message for mismatched password fields
            if request.POST['password'] != request.POST['password_repeat']:
                messages.warning(request, _(
                    'Password confirmation does not match original.'))
                password_error = True
            # Success
            if (not email_error and not password_error):
                create_account(request)
    # Returns form page
    return render(request, 'screendoor/register.html',
                  {'register_form': register_form})


def create_account(request):
    # Creates account and saves email, password, username to database
    user = User.objects.create_user(
        request.POST['email'].lower(), password=request.POST['password'], email=request.POST['email'].lower())
    # Extrapolate first and last name (experimental)
    user.first_name = request.POST['email'].split('.')[0].title()
    user.last_name = request.POST['email'].split(
        '.')[1].split('@')[0].title().translate({ord(n): None for n in digits})
    # Saves updated user info to database
    user.save()
    # Redirects to...
    return render(request, 'screendoor/index.html',
                  {'register_form': register_form})


def login_form(request):
    # Instantiate form object
    login_form = LoginForm(request.POST)
    # Has the user hit login button
    if request.method == 'POST':
        # Validates form and persists username data
        if login_form.is_valid():
            # Returns not null if username and password match a user
            user = authenticate(
                username=request.POST['email'].lower(), password=request.POST['password'])
            # Success
            if user is not None:
                login(request, user)
                return render(request, 'screendoor/index.html')
            # Display warning
            else:
                messages.warning(request, _('Invalid username or password.'))
    # Display login page
    return render(request, 'screendoor/login.html',
                  {'login_form': login_form})


@login_required
def logout_view(request):
    logout(request)
    return None


# Exceptions - shortcut: get_object_or_404()
# e.g.     question = get_object_or_404(Question, pk=question_id)


# Reverse function
# return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
# reverse function belongs to HttpResponseRedirect constructor.
# Given name of the view we want to pass control to, and the variable portion
# of the URL pattern that points to that view (plus arguments).


# View component reuse: generic views
