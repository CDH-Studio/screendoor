import datetime
from django.test import TestCase
from django.test.client import Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ObjectDoesNotExist

from screendoor.uservisibletext import ErrorMessages
from screendoor.forms import CreatePositionForm, LoginForm, ImportApplicationsForm
from screendoor.models import ScreenDoorUser, Position
from screendoor.parseposter import parse_upload


class UserRegistrationTests(TestCase):

    def setUp(self):
        self.c = Client()
        self.user = ScreenDoorUser.objects.create_user(
            username="good@canada.ca", email="good@canada.ca",
            password="password76")
        self.user.save()

    def test_register_view_exists(self):
        response = self.c.post(reverse('register'), {'email': "test@email.ca"})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/register.html")

    def test_logged_out_user_gets_redirected(self):
        response = self.c.get(reverse('home'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/login")

    def test_logged_in_user_doesnt_get_redirected(self):
        self.c.login(username="good@canada.ca", password="password76")
        response = self.c.get(reverse('positions'))
        self.assertEqual(response.status_code, 200)

    def test_bad_domain_error(self):
        response = self.c.post(reverse('register'), {'email': "test@bad.ca"})
        self.assertFormError(response, "register_form", "email", format(
            ErrorMessages.invalid_email_domain % "bad.ca"))

    def test_user_already_exists_error(self):
        response = self.c.post(reverse('register'), {
                               'email': "good@canada.ca"})
        self.assertFormError(response, "register_form", "email", format(
            ErrorMessages.user_already_exists % "good@canada.ca"))


class UserLoginTests(TestCase):
    # note: uses first way to test forms, submitting the form through the post request
    def setUp(self):
        self.c = Client()
        self.unconfirmed_user = ScreenDoorUser.objects.create_user(
            username="bad@canada.ca", email="bad@canada.ca",
            password="password76", email_confirmed=False)
        self.confirmed_user = ScreenDoorUser.objects.create_user(
            username="good@canada.ca", email="good@canada.ca",
            password="password76", email_confirmed=True)
        self.unconfirmed_user.save()
        self.confirmed_user.save()
        self.error_strings = ErrorMessages()

    def test_login(self):
        response = self.c.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_no_account(self):
        response = self.c.post(
            reverse('login'), {'email': "test@canada.ca", 'password': "password76"})
        self.assertFormError(response, "login_form", "email",
                             ErrorMessages.invalid_un_or_pw)

    def test_no_activated_account(self):
        form = LoginForm(
            data={'email': 'bad@canada.ca', 'password': 'password76'})
        self.assertFalse(form.is_valid())
        self.assertTrue(form.errors['email'],
                        ErrorMessages.unconfirmed_email)


class CreatePositionTests(TestCase):
    # note: uses second way to test forms, creating the form object and validating it
    def setUp(self):
        self.c = Client()
        self.user = ScreenDoorUser.objects.create_user(
            username="good@canada.ca", email="good@canada.ca",
            password="password76")
        self.user.save()
        self.pdf_file = SimpleUploadedFile("tests/Sample Job Poster.pdf",
                                           b"file_content",
                                           content_type="application/pdf")
        self.html_file = SimpleUploadedFile("tests/Sample Job Poster.html",
                                            b"file_content",
                                            content_type="application/html")

    def test_logged_out_user_gets_redirected(self):
        response = self.c.get(reverse('importposition'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/login")

    def test_logged_in_user_doesnt_get_redirected(self):
        self.c.login(username="good@canada.ca", password="password76")
        response = self.c.get(reverse('importposition'))
        self.assertEqual(response.status_code, 200)

    def test_reject_empty_form(self):
        form = CreatePositionForm(data={})
        self.assertFalse(form.is_valid())
        self.assertTrue(form.errors['pdf'],
                        ErrorMessages.empty_create_position_form)

    def test_reject_overfilled_form(self):
        form = CreatePositionForm(
            data={'url_ref': 'http://localhost:8000/createnewposition'})
        form.fields['url_ref'].initial = "http://localhost:8000/createnewposition"
        form.fields['pdf'].initial = self.pdf_file
        self.assertFalse(form.is_valid())
        self.assertTrue(
            form.errors['pdf'], ErrorMessages.overfilled_create_position_form)

    # needs to be verbose, else the mime type gets identified as .ksh
    def test_pass_good_form(self):
        with open(
                'tests/Sample Job Poster.pdf'.format("Sample Job Poster.pdf"),
                'rb') as file:
            form = CreatePositionForm(data={})
            form.fields['pdf'].initial = file
            self.assertTrue(form.is_valid())

    def test_reject_bad_file_type(self):
        form = CreatePositionForm(data={})
        form.fields['pdf'].initial = self.html_file
        self.assertFalse(form.is_valid())
        self.assertTrue(form.errors['pdf'], ErrorMessages.incorrect_mime_type)

    def test_reject_bad_url(self):
        form = CreatePositionForm(
            data={'url_ref': 'http://localhost:8000/createnewposition'})
        self.assertFalse(form.is_valid())
        self.assertTrue(form.errors['url_ref'],
                        ErrorMessages.invalid_url_domain)
# python manage.py test


class UploadApplicationTests(TestCase):

    def setUp(self):
        self.c = Client()
        self.user = ScreenDoorUser.objects.create_user(
            username="good@canada.ca", email="good@canada.ca",
            password="password76")
        self.user.save()
        # self.pdf_file = SimpleUploadedFile("tests/sample_app.pdf",
        #                                    b"file_content",
        #                                    content_type="application/pdf")
        self.html_file = SimpleUploadedFile("tests/Sample Job Poster.html",
                                            b"file_content",
                                            content_type="application/html")
        self.position = Position()
        self.position.title = "Test Position"
        self.position.reference_number = "1234"
        self.position.save()
        self.user.positions.add(self.position)
        self.user.save()

    def test_reject_empty_form(self):
        form = ImportApplicationsForm(data={})
        self.assertFalse(form.is_valid())
        self.assertTrue(form.errors['pdf'],
                        ErrorMessages.empty_application_form)

    def test_reject_bad_file_type(self):
        form = ImportApplicationsForm(data={})
        form.fields['pdf'].initial = self.html_file
        self.assertFalse(form.is_valid())
        self.assertTrue(form.errors['pdf'], ErrorMessages.incorrect_mime_type)


class PositionDeleteTests(TestCase):

    def setUp(self):
        self.c = Client()
        self.user = ScreenDoorUser.objects.create_user(
            username="good@canada.ca", email="good@canada.ca",
            password="password76")
        self.user.save()
        self.c.login(username="good@canada.ca", password="password76")
        self.position = Position()
        self.position.title = "Test Position"
        self.position.reference_number = "1234"
        self.position.save()
        self.user.positions.add(self.position)
        self.user.save()

    def test_successful_delete(self):
        self.c.post('/position/delete',
                    {'delete': 'Delete', 'position-id': self.position.id})
        with self.assertRaises(Position.DoesNotExist):
            Position.objects.get(id=self.position.id)

    def test_unsuccessful_delete(self):
        with self.assertRaises(Position.DoesNotExist):
            self.c.post('/position/delete',
                        {'delete': 'Delete', 'position-id': 99999})

#python manage.py test

