import json
import sys, traceback
from io import BytesIO
from string import digits
from urllib import parse
from datetime import datetime, timezone
from dateutil.relativedelta import *
import dateutil
from django.contrib.auth.decorators import login_required

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from screendoor.models import Position, Applicant, Education, FormAnswer, Note, Qualifier, ScreenDoorUser, Requirement


# Ajax url
@login_required(login_url='login', redirect_field_name=None)
def change_favourites_status(request):
    app_id = request.GET.get("app_id")
    applicant = Applicant.objects.get(applicant_id=app_id)
    favourite_status = request.GET.get("favouriteStatus")

    if favourite_status == "True":
        request.user.favourites.remove(applicant)
    else:
        request.user.favourites.add(applicant)

    request.user.save()
    return JsonResponse({
        'app_id': app_id,
        'favourite_status': favourite_status
    })


# Ajax url
@login_required(login_url='login', redirect_field_name=None)
def add_user_to_position(request):
    user_email = request.GET.get("email")
    position_id = request.GET.get("id")
    position = Position.objects.get(id=position_id)
    try:
        new_user = ScreenDoorUser.objects.get(email=user_email)
        if new_user in position.position_users.all():
            return JsonResponse(
                {'exception': 'User already has access to this position.'})
        position.position_users.add(new_user)
        position.last_modified_by = request.user
        position.save()
        return JsonResponse({
            'userName': new_user.username,
            'userEmail': new_user.email
        })
    except:
        return JsonResponse({'exception': 'User does not exist.'})


# Ajax url
@login_required(login_url='login', redirect_field_name=None)
def remove_user_from_position(request):
    user_email = request.GET.get("email")
    position_id = request.GET.get("id")
    position = Position.objects.get(id=position_id)

    try:
        user_to_remove = ScreenDoorUser.objects.get(email=user_email)
        position.position_users.remove(user_to_remove)
        position.last_modified_by = request.user
        position.save()
        return JsonResponse({'userEmail': user_email})

    except:
        return JsonResponse({})


# Ajax url
@login_required(login_url='login', redirect_field_name=None)
def add_note(request):
    note_text = parse.unquote_plus(request.GET.get("noteText"))
    answer_id = request.GET.get("parentAnswerId")

    try:
        answer = FormAnswer.objects.get(id=answer_id)
        note = Note(author=request.user,
                    parent_answer=answer,
                    note_text=note_text)
        note.save()

        # Change who last modified the application
        answer.parent_applicant.last_modified_by = request.user
        answer.parent_applicant.save()

        return JsonResponse({
            'noteId': note.id,
            'noteAuthor': note.author.username,
            'noteCreated': note.created,
            'noteText': note.note_text
        })

    except:
        return JsonResponse({})


# Ajax url
@login_required(login_url='login', redirect_field_name=None)
def remove_note(request):
    note_id = request.GET.get("noteId")
    answer_id = request.GET.get("parentAnswerId")
    answer = FormAnswer.objects.get(id=answer_id)
    try:
        note = Note.objects.get(id=note_id)
        note.delete()
        # # Change who last modified the application
        answer.parent_applicant.last_modified_by = request.user
        answer.parent_applicant.save()
        return JsonResponse({'noteId': note_id})
    except:
        return JsonResponse({})


# Ajax url
@csrf_exempt
@login_required(login_url='login', redirect_field_name=None)
def edit_position(request):
    try:
        
        position_dictionary = json.loads(request.body.decode('utf-8'))
        position_id = int(position_dictionary["positionId"])
        position = Position.objects.get(id=position_id)
        position.position_title = position_dictionary["position-title"]
        position.classification = position_dictionary[
            "position-classification"]
        position.reference_number = position_dictionary["position-reference"]
        position.selection_process_number = position_dictionary[
            "position-selection"]
        position.date_closed = dateutil.parser.parse(
            position_dictionary["position-date-closed"])
        position.num_positions = position_dictionary["position-num-positions"]
        position.salary = position_dictionary["position-salary"]
        position.open_to = position_dictionary["position-open-to"]
        position.description = position_dictionary["position-description"]
        position.last_modified_by = request.user
        position.save()

        for requirement in Requirement.objects.filter(position=position):
            requirement.delete()

        education_count = 1
        experience_count = 1
        asset_count = 1

        for key, value in position_dictionary.items():
            if "education" in key:
                requirement = Requirement(position=position,
                                          requirement_type="Education",
                                          abbreviation="ED" +
                                          str(education_count),
                                          description=value)
                requirement.save()
                education_count += 1
            elif "experience" in key:
                requirement = Requirement(position=position,
                                          requirement_type="Experience",
                                          abbreviation="EXP" +
                                          str(experience_count),
                                          description=value)
                requirement.save()
                experience_count += 1
            elif "asset" in key:
                requirement = Requirement(position=position,
                                          requirement_type="Asset",
                                          abbreviation="AEXP" +
                                          str(asset_count),
                                          description=value)
                requirement.save()
                asset_count += 1
        return JsonResponse({'message': 'success'})
    except:
        print("ERROR!")
        traceback.print_exc(file=sys.stdout)
        return JsonResponse({'message': 'failure'})


# Ajax url
@csrf_exempt
@login_required(login_url='login', redirect_field_name=None)
def change_notification(request):
    # Determine what type of view the user is on based on the url pathname
    data = json.loads(request.body.decode('utf-8'))
    path_identifier = data["pageType"].split('/')[1]

    # position list view
    if path_identifier == 'positions':
        # Pull all of the positions on the page
        for position in request.user.positions.all():
            # If any changed recently, trigger a change-notification toast
            if check_if_within_time_interval(position.updated_at):
                return  JsonResponse({'message': 'change', 'lastEditedBy' : position.last_modified_by.email})

    # position detail view
    elif path_identifier == 'position':
        # Pull the position being looked at
        position = Position.objects.get(id=int(data["positionId"]))

        # If changed recently, trigger a change-notification toast
        if check_if_within_time_interval(position.updated_at):
                return  JsonResponse({'message': 'change', 'lastEditedBy' : position.last_modified_by.email})

    # applicant view
    elif path_identifier == 'application':
        # Pull the application being looked at
        applicant = Applicant.objects.get(id=int(data["applicantId"]))

        # If changed recently, trigger a change-notification toast
        if check_if_within_time_interval(applicant.updated_at):
                return  JsonResponse({'message': 'change', 'lastEditedBy' : applicant.last_modified_by.email})

    # Return nothing
    return JsonResponse({})

# check if the updated at date was within the last 7 seconds
def check_if_within_time_interval(updated_at_date):
    lower_bound = datetime.now(timezone.utc) + relativedelta(seconds=-7)
    if updated_at_date > lower_bound:
        return True
    return False