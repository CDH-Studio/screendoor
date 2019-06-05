from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext as _
import magic, mimetypes

from .models import ScreenDoorUser, Position, Applicant
from .uservisibletext import ErrorMessages, CreatePositionFormText, \
    CreateAccountFormText, StandardFormText, LoginFormText

# For creating a new position
class ImportApplicationsForm(forms.ModelForm):
    class Meta:
        model = Applicant
        fields = ('pdf', )

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


    def clean(self):
        pdf = self.cleaned_data.get('pdf')
        url = self.cleaned_data.get('url_ref')
        # Check for an empty form
        if not pdf and not url:
            msg = forms.ValidationError(ErrorMessages.empty_create_position_form)
            self.add_error('pdf', msg)
            return
        # Check for an overfilled form
        elif pdf and url:
            msg = forms.ValidationError(
                ErrorMessages.overfilled_create_position_form)
            self.add_error('pdf', msg)
            return

        # Verify if the pdf upload has an correct mimetype (i.e. a pdf file)
        if pdf:
            file_type = mimetypes.MimeTypes().types_map_inv[1][
                magic.from_buffer(self.cleaned_data['pdf'].read(), mime=True)
            ][0]
            if not (file_type == '.pdf'):
                msg = forms.ValidationError(
                    ErrorMessages.incorrect_mime_type)
                self.add_error('pdf', msg)

        # Verify if the url matches the job.gc.ca domain
        if url:
            ## Note: Below code is temporary, until url uploading is supported.
            msg = forms.ValidationError(
                     ErrorMessages.url_upload_not_supported_yet)
            self.add_error('url_ref', msg)


            ## Note: Desired code below.
            # if not "https://emploisfp-psjobs.cfp-psc.gc.ca" in url:
            #     msg = forms.ValidationError(
            #         ErrorMessages.invalid_url_domain)
            #     self.add_error('url_ref', msg)

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
    password = forms.CharField(
        label=LoginFormText.password, min_length=8, max_length=42, widget=forms.PasswordInput)

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
