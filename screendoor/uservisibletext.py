from django.utils.translation import gettext as _


class StandardFormText():
    # Translators: StandardFormText
    username_or_email_label = _('Username/Email Address')
    # Translators: StandardFormText
    create_account = _("Create Account")


class ErrorMessages():
    # Translators: When a user tries to upload a blank position form.
    empty_create_position_form = _(
        'Please enter either a pdf file or a url link.')
    # Translators: When a user tries to upload a position form with too much data.
    overfilled_create_position_form = _(
        'Please enter *either* a pdf file or a url link, but not both.')
    # Translators: When a user tries to make a duplicate account. %s is the email (i.e. joesmith@canada.ca).
    user_already_exists = _('Username %s already exists.')
    # Translators: When a user tries to sign on with something that isn't a government email. %s is the email domain (i.e. email.ca).
    invalid_email_domain = _(
        'Invalid e-mail address domain: %s. Canada.ca email required.')
    # Translators: When a user tries to login with an unauthenticated account.
    unconfirmed_email = _('Email address for user not confirmed.')
    # Translators: When a user submits an invalid username and/or password.
    invalid_un_or_pw = _('Invalid username or password.')
    # Translators: When a user tries to upload a faulty pdf/
    incorrect_mime_type = _('Please enter a valid PDF file.')
    # Translators: When a user tries to upload a url other than the jobs.gc.ca posters.
    invalid_url_domain = _('Please enter a jobs.gc.ca url.')
    # Translators: When a user tries to upload a pdf we cant parse.
    incorrect_pdf_file = _(
        'Unable to parse pdf. Please enter a pdf from jobs.gc.ca.')
    # Translators: When a user tries to upload a url.
    url_upload_not_supported_yet = _(
        'URL uploading not currently supported. Please upload a pdf file.')


class InterfaceText():
    # Translators: Sidebar
    view_positions = _('View Positions')
    # Translators: Sidebar
    new_position = _('New Position')
    # Translators: Sidebar
    welcome_user = _("Welcome, %s")
    # Translators: Sidebar
    logout = _("Logout")


class PositionText():
    # Translators: Confirming Position Information
    we_think_this_is_correct = _(
        'We think this is the position. Can you take a look and make sure it is correct?')
    # Translators: Confirming Position Information
    classification = _('Classification')
    # Translators: Confirming Position Information
    reference_number = _("Reference number")
    # Translators: Confirming Position Information
    selection_process_number = _("Selection process number")
    # Translators: Confirming Position Information
    date_closed = _("Date closed")
    # Translators: Confirming Position Information
    number_of_positions = _("No. positions")
    # Translators: Confirming Position Information
    salary_range = _("Salary range")
    # Translators: Confirming Position Information
    open_to = _("Open to")
    # Translators: Confirming Position Information
    position_information = _("Position information")
    # Translators: Confirming Position Information
    education_and_experience_criteria = _("Education and Experience Criteria")
    # Translators: Confirming Position Information
    education = _("Education")
    # Translators: Confirming Position Information
    experience = _("Experience")
    # Translators: Confirming Position Information
    assets = _("Assets")
    # Translators: Confirming Position Information
    save = _("Save")
    # Translators: Confirming Position Information
    edit = _("Edit")
    # Translators: Confirming Position Information
    back_to_positions = _("Back to Positions")
    # Translators: Confirming Position Informatino
    cannot_display_position = _("Error: Position cannot be displayed")


class CreatePositionFormText():
    # Translators: CreatePositionForm
    upload_new_position = _("Upload New Position")
    # Translators: CreatePositionForm
    please_select_either_filetype = _(
        "Please select either PDF or link to the jobs.gc.ca posting")
    # Translators: CreatePositionForm
    pdf = _("PDF")
    # Translators: CreatePositionForm
    url = _("URL")
    # Translators: CreatePositionForm
    browse_for_pdf = _("Drag or browse for a PDF file")
    # Translators: CreatePositionForm
    link_to_job_description = _("Link to job description")
    # Translators: CreatePositionForm
    choose_a_file = _("Choose a file")
    # Translators: CreatePositionForm
    browse = _("Browse")
    # Translators: CreatePositionForm
    submit = _("Submit")


class CreateAccountFormText():
    # Translators: CreatePositionForm
    create_account = _("Create Account")
    # Translators: CreatePositionForm
    email_address = _("Email address")
    # Translators: CreatePositionForm
    choose_password = _("Choose a password")
    # Translators: CreatePositionForm
    confirm_password = _("Re-enter your password")
    # Translators: CreatePositionForm
    have_an_account_sign_in = _("Have an account? Sign in")
    # Translators: CreatePositionForm
    account_created = _(
        "Account %s created. Please check your e-mail for an activation link.")


class LoginFormText():
    # Translators: LoginForm
    login = _("Login")
    # Translators: LoginForm
    password = _("Password")
    # Translators: LoginForm
    account_confirmed = _("Account %s confirmed. Please sign in below.")
    # Translators: LoginForm
    validation_error = _(
        "Validation token error: invalid link or account is already confirmed.")


class PositionsViewText():
    # Translators: Position View
    sort_by = _("Sort by")
    # Translators: Position View
    position = _("Position")
    # Translators: Position View
    score = _("Avg Score")
    # Translators: Position View
    no_applicants = _("Applicants")
    # Translators: Position View
    date_closed = _("Date closed")
    # Translators: Position View
    date_uploaded = _("Date uploaded")
    # Translators: Position View
    view = _("View")
    # Translators: Position View
    download = _("Download")
    # Translators: Position View
    delete = _("Delete")
    # Translators: Position View
    upload_applications = _("Upload applications")
    # Translators: Position View
    no_positions = _(
        'You have not uploaded any positons. Click %s to get started.')
    # Translators: Position View
    confirm_delete_header = _("Please Confirm Deletion")
    # Translators: Position View
    confirm_delete = _("Are you sure you want to delete this position?")


# translate command (in web sh): python manage.py makemessages -l pl
# note: Translators: is specific syntax that makes the comment appear in the translation file
# dont omit it
