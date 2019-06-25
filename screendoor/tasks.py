import random
import string
import os
from celery import shared_task
from celery.contrib import rdb
from datetime import datetime, timedelta
from django.core.files import File
from django.views.decorators.csrf import csrf_protect

from screendoor_app.settings import PROJECT_ROOT

from .models import EmailAuthenticateToken, Position
from .parseapplication import parse_application
from .forms import ScreenDoorUserCreationForm, LoginForm, CreatePositionForm, ImportApplicationsForm


# Notes
# Backends use resources to store and transmit results. To ensure that resources are released, you must
# eventually call get() or forget() on EVERY AsyncResult instance returned after calling a task.
# Information about currently executing task can be accessed like:
# function_name.request.
# e.g.
# function_name.request.id
# or, if the function is annotated with (bind=True), use self.
# You should pass self into the function in this case.
# Get ID in the view when you call a task function, and then pass it to the
# template so it can be a accessed via the JS function to poll for results.


# Triggered tasks

@shared_task(bind=True)
def process_position(self):
    pass


@shared_task(bind=True)
def process_applications(self, file_paths, position_id):
    applicant_counter = 0
    batch_counter = 0
    for file_path in file_paths:
        batch_counter += 1
        applicant_counter += parse_application(
            position_id, file_path, applicant_counter, batch_counter)
        os.remove(file_path)

# Scheduled tasks

# Once per day
@shared_task
def delete_authorization_tokens():
    EmailAuthenticateToken.objects.filter(
        created=datetime.now() - timedelta(days=2)).delete()


# Once per day
@shared_task
def delete_orphaned_positions():
    Position.objects.filter(screendooruser=None).delete()
