from django.utils.translation import gettext as _

errormsg_unconfirmed_email = _('Email address for user not confirmed.')
errormsg_empty_create_position_form = _('Please enter either a pdf file or a url link.')
errormsg_overfilled_create_position_form = _('Please enter *either* a pdf file or a url link, but not both.')
errormsg_user_already_exists = _('Username %s already exists.')
errormsg_invalid_email_domain = _('Invalid e-mail address domain: %s. Canada.ca email required.')
errormsg_invalid_un_or_pw = _('Invalid username or password.')


#translate command (in web sh: python manage.py makemessages -l pl)