from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext as _
from .errormessages import *

from .models import ScreenDoorUser, Position


# For creating a new position
class CreatePositionForm(forms.ModelForm):
    class Meta:
        model = Position
        fields = ('pdf', 'url_ref')
        widgets = {'url_ref': forms.TextInput(attrs={'disabled': 'disabled'})}

    # Ensures strictly one of: pdf or url. mg
    def clean(self):
        pdf = self.cleaned_data.get('pdf')
        url = self.cleaned_data.get('url_ref')
        if not pdf and not url:
            msg = forms.ValidationError(errormsg_empty_create_position_form)
            self.add_error('pdf', msg)
        elif pdf and url:
            msg = forms.ValidationError(errormsg_overfilled_create_position_form)
            self.add_error('pdf', msg)

        return self.cleaned_data


class ScreenDoorUserCreationForm(UserCreationForm):
    text = _("Create Account")

    class Meta(UserCreationForm):
        model = ScreenDoorUser
        fields = ('email',)

    # Clean and validate fields. Password validation is handled by Django UserCreationForm
    def clean(self):
        email = self.cleaned_data.get('email')
        # Validate e-mail domain (canada.ca only)
        email_domain = email.split('@')[1].lower()
        if email_domain != "canada.ca":
            message = forms.ValidationError(format(errormsg_invalid_email_domain % email_domain))
            self.add_error('email', message)

        # Validate if e-mail is unique in system
        elif get_user_model().objects.filter(username=email.lower()).exists():
            message = forms.ValidationError(format(errormsg_user_already_exists % email))
            self.add_error('email', message)

        return self.cleaned_data


class LoginForm(forms.Form):
    login_text = _("Login")
    create_account_text = _("Create Account")
    email = forms.EmailField(
        label=_('Username/Email Address'), max_length=100)
    password = forms.CharField(
        label=_('Password'), min_length=8, max_length=42, widget=forms.PasswordInput)

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        user = authenticate(username=email, password=password)
        # Does user exist in system?
        if user is None:
            message = forms.ValidationError(errormsg_invalid_un_or_pw)
            self.add_error('email', message)
        # Has user confirmed e-mail address?
        elif user.email_confirmed == False:
            message = forms.ValidationError(errormsg_unconfirmed_email)
            self.add_error('email', message)

        return self.cleaned_data

    def get_user(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        return authenticate(username=email, password=password)



class LogoutForm(forms.Form):
    text = _("Log out")
