import json
import sys, traceback
from io import BytesIO
from string import digits
from urllib import parse
import dateutil

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from screendoor.models import Position, Applicant, Education, FormAnswer, Note, Qualifier, ScreenDoorUser, Requirement


# Ajax url
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
        position.save()
        return JsonResponse({
            'userName': new_user.username,
            'userEmail': new_user.email
        })
    except:
        return JsonResponse({'exception': 'User does not exist.'})


# Ajax url
def remove_user_from_position(request):
    user_email = request.GET.get("email")
    position_id = request.GET.get("id")
    position = Position.objects.get(id=position_id)

    try:
        user_to_remove = ScreenDoorUser.objects.get(email=user_email)
        position.position_users.remove(user_to_remove)
        position.save()
        return JsonResponse({'userEmail': user_email})

    except:
        return JsonResponse({})


# Ajax url
def add_note(request):
    note_text = parse.unquote_plus(request.GET.get("noteText"))
    answer_id = request.GET.get("parentAnswerId")

    try:
        answer = FormAnswer.objects.get(id=answer_id)
        note = Note(author=request.user,
                    parent_answer=answer,
                    note_text=note_text)
        note.save()
        return JsonResponse({
            'noteId': note.id,
            'noteAuthor': note.author.username,
            'noteCreated': note.created,
            'noteText': note.note_text
        })

    except:
        return JsonResponse({})


# Ajax url
def remove_note(request):
    note_id = request.GET.get("noteId")
    try:
        note = Note.objects.get(id=note_id)
        note.delete()
        return JsonResponse({'noteId': note_id})
    except:
        return JsonResponse({})


# Ajax url
@csrf_exempt
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
