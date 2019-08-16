import datetime
from django.test import TestCase
from django.test.client import Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from screendoor.models import Position, Applicant, Requirement, ScreenDoorUser, FormAnswer, Note
import json

class FavouriteTests(TestCase):

    def setUp(self):
        self.c = Client()
        self.user = ScreenDoorUser.objects.create_user(
            username="good@canada.ca", email="good@canada.ca",
            password="password76")
        self.testApplication = Applicant(
            applicant_id="testId",
            citizenship='Canadian Citizen',
            priority=False,
            veteran_preference=False,
            french_working_ability='Advanced',
            english_working_ability='Advanced',
            first_official_language='French',
            written_exam='English',
            correspondence='English',
            interview='English',
            number_questions=24,
            number_yes_responses=13,
            percentage_correct=54,
            stream_count=2
        )
        self.user.save()
        self.testApplication.save()


    # Favourite applicant tests
    def test_change_favourites_path_redirects_logged_out_users(self):
        response = self.c.get(reverse('change_favourites_status'))
        self.assertEqual(response.status_code, 302)


    def test_add_and_remove_applicant_from_favourites(self):
        self.c.login(username="good@canada.ca", password="password76")
        response = self.c.get(reverse('change_favourites_status'), {'app_id': self.testApplication.applicant_id, 'favouriteStatus': "False"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user.favourites.all()[0], self.testApplication)
        response = self.c.get(reverse('change_favourites_status'), {'app_id': self.testApplication.applicant_id, 'favouriteStatus': "True"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(self.user.favourites.all()), 0)


class UserTests(TestCase):

    def setUp(self):
        self.c = Client()
        self.user = ScreenDoorUser.objects.create_user(
            username="good@canada.ca", email="good@canada.ca",
            password="password76")
        self.anotherUser = ScreenDoorUser.objects.create_user(
            username="alsogood@canada.ca", email="alsogood@canada.ca",
            password="password76")
        self.testPosition = Position(
            position_title="Senior Program Support",
            classification="AS-05",
            reference_number="SHC19J-020046-000203",
            selection_process_number="19-NHW-CSB-IA-NCR-262953",
            date_closed= datetime(2019, 5, 21, 23, 59),
            num_positions="1",
            open_to="Employees of Health Canada working in National Capital Region (NCR)*",
            salary="$80,274 to $86,788"
        )
        self.user.save()
        self.testPosition.save()
        self.testPosition.position_users.add(self.user)


    # Add user tests
    def test_add_user_path_redirects_logged_out_users(self):
        response = self.c.get(reverse('add_user_to_position'))
        self.assertEqual(response.status_code, 302)


    def test_add_user_path_rejects_existing_user(self):
        self.c.login(username="good@canada.ca", password="password76")
        response = self.c.get(reverse('add_user_to_position'), {'email': "good@canada.ca", 'id': self.testPosition.id})
        
        parsed_response = json.loads(response.content.decode())
        self.assertTrue(parsed_response['exception'], "User already has access to this position.")
        

    def test_add_user_path_rejects_bad_user(self):
        self.c.login(username="good@canada.ca", password="password76")
        response = self.c.get(reverse('add_user_to_position'), {'email': "notauseremail", 'id': self.testPosition.id})
        
        parsed_response = json.loads(response.content.decode())
        self.assertTrue(parsed_response['exception'], "User does not exist.")


    def test_add_user(self):
        self.c.login(username="good@canada.ca", password="password76")
        response = self.c.get(reverse('add_user_to_position'), {'email': "alsogood@canada.ca", 'id': self.testPosition.id})
        self.assertEqual(response.status_code, 200)

        parsed_response = json.loads(response.content.decode())
        self.assertEqual(parsed_response['userName'] , "alsogood@canada.ca")


    # Remove user tests
    def test_remove_user_path_redirects_logged_out_users(self):
        response = self.c.get(reverse('remove_user_from_position'))
        self.assertEqual(response.status_code, 302)


    def test_remove_user(self):  
        self.c.login(username="alsogood@canada.ca", password="password76")
        response = self.c.get(reverse('remove_user_from_position'), {'email': "good@canada.ca", 'id': self.testPosition.id})
        self.assertEqual(response.status_code, 200)

        parsed_response = json.loads(response.content.decode())
        self.assertEqual(parsed_response['userEmail'] , "good@canada.ca")

    
class NoteTests(TestCase):

    def setUp(self):
        self.c = Client()
        self.user = ScreenDoorUser.objects.create_user(
            username="good@canada.ca", email="good@canada.ca",
            password="password76")
        self.testApplication = Applicant(
            applicant_id="testId",
            citizenship='Canadian Citizen',
            priority=False,
            veteran_preference=False,
            french_working_ability='Advanced',
            english_working_ability='Advanced',
            first_official_language='French',
            written_exam='English',
            correspondence='English',
            interview='English',
            number_questions=24,
            number_yes_responses=13,
            percentage_correct=54,
            stream_count=2
        )
        self.testApplication.save()

        self.testAnswer = FormAnswer(
            applicant_answer=True
        )
        self.testAnswer.save()

        self.testNote = Note(
            author = self.user
        )
        self.testNote.save()

        
        self.testAnswer.note.add(self.testNote)
        self.testApplication.answers.add(self.testAnswer)


    # Add notes test
    def test_add_note_redirects_logged_out_users(self):
        response = self.c.get(reverse('add_note'))
        self.assertEqual(response.status_code, 302)


    def test_add_note(self): 
        self.c.login(username="good@canada.ca", password="password76")
        response = self.c.get(reverse('add_note'), {'noteText': "NEWNOTETEXT", 'parentAnswerId': self.testAnswer.id})
        self.assertEqual(response.status_code, 200)

        parsed_response = json.loads(response.content.decode())
        self.assertEqual(parsed_response['noteText'] , "NEWNOTETEXT")
        self.assertEqual(parsed_response['noteAuthor'] , self.user.username)


    # Remove notes test
    def test_remove_note_redirects_logged_out_users(self):
        response = self.c.get(reverse('remove_note'))
        self.assertEqual(response.status_code, 302)


    def test_remove_note(self): 
        self.c.login(username="good@canada.ca", password="password76")
        response = self.c.get(reverse('remove_note'), {'noteId': self.testNote.id, 'parentAnswerId': self.testAnswer.id})
        self.assertEqual(response.status_code, 200)

        parsed_response = json.loads(response.content.decode())
        self.assertEqual(parsed_response['noteId'] , str(self.testNote.id))


class EditPositionTests(TestCase):

    def setUp(self):
        self.c = Client()
        self.user = ScreenDoorUser.objects.create_user(
            username="good@canada.ca", email="good@canada.ca",
            password="password76")
        self.anotherUser = ScreenDoorUser.objects.create_user(
            username="alsogood@canada.ca", email="alsogood@canada.ca",
            password="password76")
        self.testPosition = Position(
            position_title="UNEDITED",
            classification="UNEDITED",
            reference_number="UNEDITED",
            selection_process_number="UNEDITED",
            date_closed= datetime(2001, 1, 1, 1, 1),
            num_positions="UNEDITED",
            open_to="UNEDITED",
            salary="UNEDITED",
            last_modified_by=self.anotherUser
        )

        self.ed1 = Requirement(
            requirement_type="Education",
            abbreviation="ED1",
            description="UNEDITED"
        )

        self.exp1 = Requirement(
            requirement_type="Experience",
            abbreviation="EXP1",
            description="UNEDITED"
        )
        self.exp2 = Requirement(
            requirement_type="Experience",
            abbreviation="EXP2",
            description="UNEDITED"
        )
        self.exp3 = Requirement(
            requirement_type="Experience",
            abbreviation="EXP3",
            description="UNEDITED"
        )
        self.exp4 = Requirement(
            requirement_type="Experience",
            abbreviation="EXP4",
            description="UNEDITED"
        )

        self.aexp1 = Requirement(
            requirement_type="Asset",
            abbreviation="AEXP1",
            description="UNEDITED"
        )
        self.aexp2 = Requirement(
            requirement_type="Asset",
            abbreviation="AEXP2",
            description="UNEDITED"
        )
        self.aexp3 = Requirement(
            requirement_type="Asset",
            abbreviation="AEXP3",
            description="UNEDITED"
        )
        self.aexp4 = Requirement(
            requirement_type="Asset",
            abbreviation="AEXP4",
            description="UNEDITED"
        )

        self.user.save()
        self.testPosition.save()
        self.testPosition.position_users.add(self.user)


    # Edit positions tests
    def test_edit_position_redirects_logged_out_users(self):
        response = self.c.post(reverse('edit-position'))
        self.assertEqual(response.status_code, 302)

    def test_edit(self):
        self.c.login(username="good@canada.ca", password="password76")
        response = self.c.post(reverse('edit-position'), {
            'positionId': self.testPosition.id,
            'position-title': 'EDITED',
            'position-classification': 'EDITED',
            'position-reference': 'EDITED',
            'position-selection': 'EDITED',
            'position-date-closed': 'May 2 2020',
            'position-num-positions': 'EDITED',
            'position-salary': 'EDITED',
            'position-open-to': 'EDITED',
            'position-description': 'EDITED'
        }, content_type="application/json")

        parsed_response = json.loads(response.content.decode())
        self.assertEqual(parsed_response['message'] , 'success')
        position = Position.objects.get(id=self.testPosition.id)
        self.assertEqual(position.position_title, 'EDITED')
        self.assertEqual(position.classification, 'EDITED')
        self.assertEqual(position.reference_number, 'EDITED')
        self.assertEqual(position.selection_process_number, 'EDITED')
        self.assertEqual(position.num_positions, 'EDITED')
        self.assertEqual(position.salary, 'EDITED')
        self.assertEqual(position.open_to, 'EDITED')
        self.assertEqual(position.description, 'EDITED')
        self.assertEqual(position.last_modified_by , self.user)


#python manage.py test