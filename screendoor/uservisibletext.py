from django.utils.translation import gettext as _


class ToolTips():
    favourite = _("Favourite or unfavourite applicant")
    pdf = _("Download PDF Screening Evaluation Sheet")
    screening_evaluation_sheet = _("Download Screening Evaluation Sheet PDF")
    qualifier_tooltip = _(
        """Whether the identified information met the requirements stated by the question.
    Passed: The applicant's experience explicitly met the requirement.
    Failed: The applicant's experience did not explicity meet the requirement.
    Indeterminate: The applicant's experience could not be determined from the provided information.
    NOTE: Ambigious dates (e.g. over 10 years) excluded.""")
    complementary_response_tooltip = _(
        """Additional information given by the applicant to explain/clarify their experience(s).
                      Only present if the applicant responded "yes" to the question."""
    )
    extracts_tooltip = _(
        """Relevant dates and experiences from Complementary Response, provided by ScreenDoor's Natural Language Processing (NLP)."""
    )
    add_note_tooltip = _("Add a note on this answer")
    # how_extract_tooltip = _("An action, duty, or task identified by the NLP model. Statements that do not refer to the applicant are exluded.")
    # when_extract_tooltip = _("A date identified by the NLP model, and how that date is used in the statement. Dates that do not refer to an applicant's experience are excluded.")


class StandardFormText():
    # Translators: StandardFormText
    username_or_email_label = _('Username/Email Address')
    # Translators: StandardFormText
    create_account = _("Create Account")


class ErrorMessages():
    # Translators: When a user tries to upload a blank application
    empty_application_form = _("Please attach a PDF file")
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
    # Translators: An error that should not be possible, a user must submit either a pdf or url.
    no_pdf_or_url_submitted = _('No pdf or url submitted')


class InterfaceText():
    # Translators: Sidebar
    view_positions = _('View Positions')
    # Translators: Sidebar
    new_position = _('New Position')
    # Translators: Sidebar
    welcome_user = _("Welcome, %s")
    # Translators: Sidebar
    logout = _("Logout")


class ImportApplicationsText():
    # Translators: text for importing job applications for a position
    title = _('Upload Completed Applications')
    # Translators: text for importing job applications for a position
    description = _(
        'Click "Browse" and select one or more completed applications for position %s, then click "Upload." Note that PDFs are the only file format supported.'
    )
    # Translators: text for importing job applications for a position
    upload = _('Upload')
    # Translators: text for importing job applications for a position
    browse = _('Browse')
    # Translators: text for importing job applications for a position
    choose_files = _('Choose one or more files')
    # Translators: text for importing job applications for a position
    processing_applicant = _('Processing applicant')
    # Translators: text for importing job applications for a position
    of = _('of')
    calculating_number_applicants = _("Calculating number of applicants")
    upload_error = _("Error displaying upload progress")


class PositionText():
    # Translators: Confirming Position Information
    we_think_this_is_correct = _(
        'We think this is the position. Can you take a look and make sure it is correct?'
    )
    # Translators: Confirming Position Information
    classification = _('Classification')
    # Translators: Confirming Position Inforation
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
    processing_applications = _("Processing Applications...")
    processing_detail_1 = _(
        "ScreenDoor is processing the following applications:")
    processing_detail_2 = _(
        "Their current status will appear below, or you can leave this page and return to view the processed applications shortly."
    )
    ok = _("OK")
    cancel = _("Cancel")
    applicant_id = _("Applicant ID")
    classifications = _("Classifications")
    streams = _("Streams")
    score = _("Tabulation")
    pdf = _("PDF")


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
    ok = _("OK")
    cancel = _("Cancel")


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
        "Validation token error: invalid link or account is already confirmed."
    )


class PositionsViewText():
    # Translators: Position View
    sort_by = _("Sort by")
    # Translators: Position View
    position = _("Position")
    # Translators: Position View
    score = _("Average")
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
    edit = _("Edit")
    # Translators: Position View
    upload_applications = _("Upload applications")
    # Translators: Position View
    no_positions = _(
        'You have not uploaded any positons. Click %s to get started.')
    # Translators: Position View
    confirm_delete_header = _("Please Confirm Deletion")
    # Translators: Position View
    confirm_delete = _("Are you sure you want to delete this position?")
    # Translators: Position View
    cancel = _("Cancel")
    # Translators: Position View
    expand_all = _("Expand all")
    # Translators: Position View
    collapse_all = _("Collapse all")
    # Translators: Position View
    position_added = _("Position added")
    # Translators: Position View
    applicants = _("Applicants")
    # Translators: Position View
    applicant = _("Applicant")
    # Translators: Position View
    average_score = _("Average Tabulation")
    # Translators: Position View
    no_applicants = _("No. Applicants")
    # Translators: Position View
    avg_score = _("Average Tabulation")
    id = _("ID")
    classifications = _("Classifications")
    streams = _("Streams")
    score = _("Tabulation")
    add_users = _("Add Users")
    add_user = _("Add another user to this position")
    current_users = _("Current users")
    you = _("you")


class ApplicantViewText():
    # Translators: Applicant View
    back_to_position = _("Back to Position")
    # Translators: Applicant View
    applicant_information = _("Applicant Information")
    # Translators: Applicant View
    applicant_id = _("Application ID")
    # Translators: Applicant View
    citizenship = _("Citizenship")
    # Translators: Applicant View
    priority = _("Priority?")
    # Translators: Applicant View
    veteran_preference = _("Veteran Preference?")
    # Translators: Applicant View
    classifications = _("Classifications")
    # Translators: Applicant View
    streams_selected = _("Streams Selected")
    # Translators: Applicant View
    french_working_ability = _("French Working Ability")
    # Translators: Applicant View
    english_working_ability = _("English Working Ability")
    # Translators: Applicant View
    first_official_language = _("First Official Language")
    # Translators: Applicant View
    written_exam_language = _("Written Exam Language")
    # Translators: Applicant View
    correspondence_language = _("Correspondence Language")
    # Translators: Applicant View
    interview_language = _("Interview Language")
    # Translators: Applicant View
    questions = _("Questions")
    # Translators: Applicant View
    question = _("Question")
    # Translators: Applicant View
    response = _("Response")
    # Translators: Applicant View
    yes = _("Yes")
    # Translators: Applicant View
    no = _("No")
    # Translators: Applicant View
    complementary_question = _("Complementary Question")
    # Translators: Applicant View
    complementary_response = _("Complementary Response")
    # Translators: Applicant View
    education = _("Education")
    # Translators: Applicant View
    academic_level = _("Academic Level")
    # Translators: Applicant View
    institution = _("Institution")
    # Translators: Applicant View
    area_of_study = _("Area of Study")
    # Translators: Applicant View
    specialization = _("Specialization")
    # Translators: Applicant View
    program_length = _("Program Length")
    # Translators: Applicant View
    years_completed = _("Years Completed")
    # Translators: Applicant View
    graduation_date = _("Graduation Date")
    # Translators: Applicant View
    yes = _("Yes")
    # Translators: Applicant View
    no = _("No")
    # Translators: Applicant View
    score = _("Score")
    # Translators: Applicant View
    analysis = _("Analysis")
    # Translators: Applicant View
    streams = _("Streams")
    stream = _("Stream")
    # Translators: Applicant View
    substantive = _("Substantive")
    # Translators: Applicant View
    current = _("Current")
    # Translators: Applicant View
    expand_all = _("Expand all")
    # Translators: Applicant View
    collapse_all = _("Collapse all")
    extract = _("Extract")
    extracts = _("Extracts")
    no_analysis = _("No Analysis")
    close = _("Close")
    notes = _("Notes")
    na = _("N/A")


# translate command (in web sh): python manage.py makemessages -l pl
# note: Translators: is specific syntax that makes the comment appear in the translation file
# dont omit it
