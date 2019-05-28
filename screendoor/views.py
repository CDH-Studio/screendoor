from string import digits
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _
from screendoor.parseposter import parse_upload
from .forms import ScreenDoorUserCreationForm, LoginForm, LogoutForm, CreatePositionForm

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
            # Success
            # create_account(request)
            send_user_email(request)
            # Redirects to...
            return redirect('account_created')
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


def account_created(request):
    if request.META.get('HTTP_REFERER') != None:
        text = _(
            "We have created your account. Please check your e-mail for a confirmation link to activate your account.")
        return render(request, 'registration/account_created.html',
                      {'text': text})
    return redirect('login')


def send_user_email(request):
    mail_sent = send_mail(
        'ScreenDoor: Please confirm e-mail address',
        'Test.',
        'screendoor@screendoor.ca',
        ['heat0072@algonquinlive.com'],
        fail_silently=False,
    )
    if mail_sent == 1:
        create_account(request)


def login_form(request):
    # Instantiate form object
    login_form = LoginForm(request.POST)
    # Has the user hit login button
    if request.method == 'POST':
        # Validates form and persists username data
        if login_form.is_valid():
            login(request, login_form.get_user)
            return redirect('home')
    # Display login page
    return render(request, 'registration/login.html',
                  {'login_form': login_form})


def logout_view(request):
    logout(request)
    return redirect('login')


def import_position(request):

    if request.method == 'POST':
        # valid form
        create_position_form = CreatePositionForm(request.POST, request.FILES)
        if create_position_form.is_valid():
            # don't commit partial positions with only pdf/url into db
            position = create_position_form.save()
            position = parse_upload(position)
            return render(request, 'position.html', {'position': position})
    else:
        # blank form
        create_position_form = CreatePositionForm()
    return render(request, 'createposition/importposition.html', {
        'form': create_position_form
    })


# Exceptions - shortcut: get_object_or_404()
# e.g.     question = get_object_or_404(Question, pk=question_id)


# Reverse function
# return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
# reverse function belongs to HttpResponseRedirect constructor.
# Given name of the view we want to pass control to, and the variable portion
# of the URL pattern that points to that view (plus arguments).


# View component reuse: generic views
