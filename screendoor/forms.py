from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import ScreenDoorUser, Position
from django.utils.translation import gettext as _


#For creating a new position
class CreatePositionForm(forms.ModelForm):
    class Meta:
        model = Position
        fields = ('pdf', 'url_ref')

    #Ensures strictly one of: pdf or url. mg
    def clean(self):
        pdf = self.cleaned_data.get('pdf')
        url = self.cleaned_data.get('url_ref')

        if not pdf and not url:
            msg = forms.ValidationError(_('Please enter either a pdf file or a url link.'))
            self.add_error('pdf', msg)
        elif pdf and url:
            msg = forms.ValidationError(_('Please enter *either* a pdf file or a url link, but not both.'))
            self.add_error('pdf', msg)

        return self.cleaned_data


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
