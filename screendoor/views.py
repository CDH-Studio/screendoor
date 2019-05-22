from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _


from .forms import RegisterForm

# Each view is responsible for doing one of two things: returning an HttpResponse object containing the content for the requested page, or raising an exception such as Http404.


# @login_required
# The login_required decorator redirects unauthenticated sessions to settings.LOGIN_URL
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
    first_name = request.POST['email'].split('.')[0]
    last_name = request.POST['email'].split('.')[1].split('@')[0]
    user = User.objects.create_user(
        request.POST['email'], request.POST['password'], request.POST['email'], first_name, last_name)
    return render(request, 'screendoor/index.html',
                  {'register_form': register_form})


def login(request):
    return render(request, 'screendoor/login.html', context)


# def login_validate(request):
#    # The only view which does not require user authentication
#    email = request.POST['email']
#    password = request.POST['password']
#    user = authenticate(request, username=username, password=password)
#    if user is not None:
#        login(request, user)
#        # Redirect to landing/job view
#    else:
#        # Redirect / show incorrect credentials login
#        return None  # Temporary
#    return None  # Temporary


# @login_required
# def logout_view(request):
#    logout(request)
#    return None


# Exceptions - shortcut: get_object_or_404()
# e.g.     question = get_object_or_404(Question, pk=question_id)


# Reverse function
# return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
# reverse function belongs to HttpResponseRedirect constructor.
# Given name of the view we want to pass control to, and the variable portion
# of the URL pattern that points to that view (plus arguments).


# View component reuse: generic views
