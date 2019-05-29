from django.test import TestCase
from .forms import CreatePositionForm
from .models import ScreenDoorUser
from django.test.client import Client
from django.urls import reverse
from .errormessages import *
# Create your tests here.

class UserRegistrationTests(TestCase):

    def setUp(self):
        self.c = Client()
        self.user = ScreenDoorUser.objects.create_user(username="good@canada.ca", email="good@canada.ca",
                                                  password="password76")
        self.user.save()

    def test_register_view_exists(self):
        response = self.c.post(reverse('register'), {'email': "test@email.ca" })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/register.html")

    def test_logged_out_user_gets_redirected(self):
        response = self.c.get(reverse('home'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/login/")

    def test_logged_in_user_doesnt_get_redirected(self):
        self.c.login(username="good@canada.ca", password="password76")
        response = self.c.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_bad_domain_error(self):
        response = self.c.post(reverse('register'), {'email': "test@bad.ca" })
        self.assertFormError(response, "register_form", "email", format(errormsg_invalid_email_domain % "bad.ca"))

    def test_user_already_exists_error(self):
        response = self.c.post(reverse('register'), {'email': "good@canada.ca" })
        self.assertFormError(response, "register_form", "email", format(errormsg_user_already_exists % "good@canada.ca"))


class UserLoginTests(TestCase):
    #note: uses first way to test forms, submitting the form through the post request
    def setUp(self):
        self.c = Client()
        unconfirmed_user = ScreenDoorUser.objects.create_user(username="bad@canada.ca", email="bad@canada.ca",
                                                  password="password76", email_confirmed=False)
        confirmed_user = ScreenDoorUser.objects.create_user(username="good@canada.ca", email="good@canada.ca",
                                                              password="password76", email_confirmed=True)
        unconfirmed_user.save()
        confirmed_user.save()

    def test_login(self):
        response = self.c.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_no_account(self):
        response = self.c.post(reverse('login'), {'email': "test@canada.ca",'password': "password76"})
        self.assertFormError(response, "login_form", "email", errormsg_invalid_un_or_pw)

    def test_no_activated_account(self):
        response = self.c.post(reverse('login'), {'email': "bad@canada.ca", 'password': "password76"})
        self.assertFormError(response, "login_form", "email", errormsg_unconfirmed_email)


class CreatePositionTests(TestCase):
    #note: uses second way to test forms, creating the form object and validating it
    def setUp(self):
        self.c = Client()

    def test_create_position_view_exists(self):
        response = self.c.post(reverse('importposition'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "createposition/importposition.html")

    def test_reject_empty_form(self):
        form = CreatePositionForm(data={})
        self.assertFalse(form.is_valid())
        self.assertTrue(form.errors['pdf'], errormsg_empty_create_position_form)

    def test_reject_overfilled_form(self):
        form = CreatePositionForm(data={'url_ref': 'http://localhost:8000/createnewposition'})
        form.fields['url_ref'].initial = "http://localhost:8000/createnewposition"
        form.fields['pdf'].initial = "positions/heck.pdf"
        self.assertFalse(form.is_valid())
        self.assertTrue(form.errors['pdf'], errormsg_overfilled_create_position_form)

    def test_pass_good_form(self):
        form = CreatePositionForm(data={})
        form.fields['pdf'].initial = "positions/heck.pdf"
        self.assertTrue(form.is_valid())
#python manage.py test











