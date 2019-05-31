from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext as _

from .models import ScreenDoorUser, Position
from .uservisibletext import ErrorMessages, CreatePositionFormText, \
    CreateAccountFormText, StandardFormText, LoginFormText


# For creating a new position
class CreatePositionForm(forms.ModelForm):
    text = CreatePositionFormText.upload_new_position
    description = CreatePositionFormText.please_select_either_filetype
    pdf_name = CreatePositionFormText.pdf
    url_name = CreatePositionFormText.url
    pdf_text = CreatePositionFormText.browse_for_pdf
    url_text = CreatePositionFormText.link_to_job_description
    upload_text = CreatePositionFormText.choose_a_file
    browse_text = CreatePositionFormText.browse
    submit_text = CreatePositionFormText.submit

    class Meta:
        model = Position
        fields = ('pdf', 'url_ref')
        widgets = {'url_ref': forms.TextInput(attrs={'disabled': 'disabled'})}

    # Ensures strictly one of: pdf or url. mg
    def clean(self):
        pdf = self.cleaned_data.get('pdf')
        url = self.cleaned_data.get('url_ref')
        if not pdf and not url:
            msg = forms.ValidationError(ErrorMessages.empty_create_position_form)
            self.add_error('pdf', msg)
        elif pdf and url:
            msg = forms.ValidationError(
                ErrorMessages.overfilled_create_position_form)
            self.add_error('pdf', msg)
        # TODO: validate file is genuine PDF using https://github.com/ahupp/python-magic
        # Python implementation libmagic unix program for validating file types
        # TODO: validate that URL is from jobs.gc.ca.

        return self.cleaned_data


class ScreenDoorUserCreationForm(UserCreationForm):
    text = CreateAccountFormText.create_account
    email_text = CreateAccountFormText.email_address
    password_text = CreateAccountFormText.choose_password
    password_confirm_text = CreateAccountFormText.confirm_password
    email = forms.EmailField(
        label=StandardFormText.username_or_email_label, max_length=100)
    login_button_text = CreateAccountFormText.have_an_account_sign_in

    class Meta(UserCreationForm):
        model = ScreenDoorUser
        fields = ('email',)

    # Clean and validate fields. Password validation is handled by Django UserCreationForm
    def clean(self):
        email = self.cleaned_data.get('email')
        # Validate e-mail domain (canada.ca only)
        email_domain = email.split('@')[1].lower()
        if email_domain != "canada.ca":
            message = forms.ValidationError(
                format(ErrorMessages.invalid_email_domain % email_domain))
            self.add_error('email', message)
        # Validate if e-mail is unique in system
        elif get_user_model().objects.filter(username=email.lower()).exists():
            message = forms.ValidationError(
                format(ErrorMessages.user_already_exists % email))
            self.add_error('email', message)

        return self.cleaned_data


class LoginForm(forms.Form):
    login_text = LoginFormText.login
    create_account_text = StandardFormText.create_account
    email = forms.EmailField(
        label=StandardFormText.username_or_email_label, max_length=100)
    password = LoginFormText.password

    def clean(self):
        # Entered e-mail is compared as lower to ensure login is not case-sensitive
        email = self.cleaned_data.get('email').lower()
        password = self.cleaned_data.get('password')
        user = authenticate(username=email, password=password)

        # Does user exist in system?
        if user is None:
            message = forms.ValidationError(ErrorMessages.invalid_un_or_pw)
            self.add_error('email', message)
        # Has user confirmed e-mail address
        elif user.email_confirmed is False:
            message = forms.ValidationError(ErrorMessages.unconfirmed_email)
            self.add_error('email', message)

        return self.cleaned_data

    def get_user(self):
        # Entered e-mail is compared as lower to ensure login is not case-sensitive
        email = self.cleaned_data.get('email').lower()
        password = self.cleaned_data.get('password')
        return authenticate(username=email, password=password)
