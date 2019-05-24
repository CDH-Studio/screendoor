from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import ScreenDoorUser
from django.utils.translation import gettext as _


class ScreenDoorUserCreationForm(UserCreationForm):
    text = _("Create Account")

    class Meta(UserCreationForm):
        model = ScreenDoorUser
        fields = ('email',)


class ScreenDoorUserChangeForm(UserChangeForm):

    class Meta:
        model = ScreenDoorUser
        fields = ('email',)


# class ScreenDoorLoginForm(UserLoginForm):

#     class Meta(UserCreationForm):
#         model = ScreenDoorUser
#         fields = ('email',)


class LoginForm(forms.Form):
    login_text = _("Login")
    create_account_text = _("Create Account")
    email = forms.EmailField(label=_('Username/Email Address'), max_length=100)
    password = forms.CharField(
        label=_('Password'), min_length=8, max_length=42, widget=forms.PasswordInput)


class LogoutForm(forms.Form):
    text = _("Log out")
