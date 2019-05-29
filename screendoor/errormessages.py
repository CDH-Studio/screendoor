from django.utils.translation import gettext as _

    ## CreatePositionForm Errors ##
# Translators: When a user tries to upload a blank position form.
errormsg_empty_create_position_form = _('Please enter either a pdf file or a url link.')
# Translators: When a user tries to upload a position form with too much data.
errormsg_overfilled_create_position_form = _('Please enter *either* a pdf file or a url link, but not both.')


    ## ScreenDoorUserCreationForm Errors ##
# Translators: When a user tries to make a duplicate account. %s is the email (i.e. joesmith@canada.ca)
errormsg_user_already_exists = _('Username %s already exists.')
# Translators: When a user tries to sign on with something that isn't a government email. %s is the email domain (i.e. email.ca)
errormsg_invalid_email_domain = _('Invalid e-mail address domain: %s. Canada.ca email required.')


    ## LoginForm Errors ##
# Translators: When a user tries to login with an unauthenticated account
errormsg_unconfirmed_email = _('Email address for user not confirmed.')
# Translators: When a user submits an invalid username and/or password.
errormsg_invalid_un_or_pw = _('Invalid username or password.')


#translate command (in web sh): python manage.py makemessages -l pl
#note: Translators: is specific syntax that makes the comment appear in the translation file
#dont omit it