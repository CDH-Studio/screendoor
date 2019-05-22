from django.core.exceptions import ValidationError
from django import forms
from django.utils.translation import gettext as _

class RegisterForm(forms.Form):
    text = _("Create Account")
    email = forms.EmailField(label=_('Canada.ca Email Address'), max_length=100)
    password = forms.CharField(label=_('Password'), min_length=12, max_length=42, widget=forms.PasswordInput)
    password_repeat = forms.CharField(label=_('Confirm Password'), min_length=12, max_length=42, widget=forms.PasswordInput)
