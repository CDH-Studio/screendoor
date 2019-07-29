import string
import time
import os
from celery import shared_task, current_task
from celery.contrib import rdb
from celery.result import AsyncResult

from datetime import datetime, timedelta
from django.core.files import File
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect

from screendoor_app.settings import PROJECT_ROOT

from .models import EmailAuthenticateToken, Position
from .parseapplication import tabula_read_pdf, clean_and_parse, get_total_applicants
from .forms import ScreenDoorUserCreationForm, LoginForm, CreatePositionForm, ImportApplicationsForm

# Triggered tasks


@shared_task(bind=True)
def process_applications(self, file_paths, position_id):
    task_id = self.request.id
    applicant_counter = 0
    batch_counter = 0
    self.update_state(state='PENDING', meta={'total': 0})
    total_applicants = int(get_total_applicants(file_paths, task_id))
    position = Position.objects.get(id=position_id)
    applications = []
    for file_path in file_paths:
        batch_counter += 1
        print("BATCH " + str(batch_counter) + ": READING TABLES")
        data_frame_list = tabula_read_pdf(file_path)
        applications = clean_and_parse(data_frame_list, position, task_id,
                                       total_applicants, applicant_counter)
        applicant_counter += len(applications)
        os.remove(file_path)
        for application in applications:
            print("APPLICANT COUNTER: " + str(applicant_counter))
            application.parent_position = position
            application.update_question_fields()
            application.save()
        print("BATCH " + str(batch_counter) + ": TABLES SUCCESSFULLY READ")
    position.update_applicant_fields()


# Scheduled tasks


# Once per day
@shared_task
def delete_authorization_tokens():
    EmailAuthenticateToken.objects.filter(created=datetime.now() -
                                          timedelta(days=2)).delete()


# Once per day
@shared_task
def delete_orphaned_positions():
    Position.objects.filter(screendooruser=None).delete()
