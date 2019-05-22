from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# Each view is responsible for doing one of two things: returning an HttpResponse object containing the content for the requested page, or raising an exception such as Http404.


# @login_required
# The login_required decorator redirects unauthenticated sessions to settings.LOGIN_URL
def index(request):
    return HttpResponse("Hello, world!")


#def login(request):
#    return render(request, 'screendoor/login.html', context)


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
