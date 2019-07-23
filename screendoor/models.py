import base64
import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from cryptography.fernet import Fernet


class Position(models.Model):
    position_title = models.TextField(blank=True)
    date_closed = models.DateField(null=True, blank=True)
    num_positions = models.CharField(max_length=200, blank=True)
    salary_min = models.DecimalField(
        decimal_places=2, max_digits=10, null=True, blank=True)
    salary_max = models.DecimalField(
        decimal_places=2, max_digits=10, null=True, blank=True)
    classification = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    open_to = models.TextField(blank=True)
    reference_number = models.CharField(max_length=200, blank=True)
    selection_process_number = models.CharField(max_length=200, blank=True)
    pdf = models.FileField(upload_to="positions/", validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
                           blank=True)
    url_ref = models.URLField(max_length=200, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    # For sorting purposes
    number_applicants = models.IntegerField(blank=True, null=True, default=0)
    mean_score = models.IntegerField(blank=True, null=True, default=0)

    def __str__(self):
        return self.position_title

    def update_applicant_fields(self):
        if self.applicant_set.all().count() > 0:
            self.number_applicants = self.applicant_set.all().count()
            self.mean_score = sum([FormAnswer.objects.filter(parent_applicant=applicant, applicant_answer=True).count(
            ) * 100 // FormAnswer.objects.filter(parent_applicant=applicant).count() for applicant in self.applicant_set.all()]) // self.applicant_set.all().count()
            self.save()


class ScreenDoorUser(AbstractUser):
    email_confirmed = models.BooleanField(default=False)
    positions = models.ManyToManyField(Position, blank=True)

    def confirm_email(self):
        self.email_confirmed = True


class EmailAuthenticateToken(models.Model):
    user = models.OneToOneField(
        get_user_model(), on_delete=models.CASCADE, primary_key=False)
    key = models.CharField(max_length=500, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def create_key(self):
        initial_key = Fernet.generate_key()
        byte_values = bytes(str(self.user.email) +
                            str(datetime.datetime.now()), 'utf-8')
        encoded_bytes = Fernet(initial_key).encrypt(byte_values)
        self.key = base64.b64encode(encoded_bytes).decode('utf-8')


class Applicant(models.Model):
    parent_position = models.ForeignKey(
        Position, on_delete=models.CASCADE, null=True)
    applicant_id = models.CharField(max_length=200, default='N/A')

    citizenship = models.CharField(max_length=200, null=True)
    priority = models.BooleanField(null=True)
    veteran_preference = models.BooleanField(null=True)

    LANGUAGE_CHOICES = [
        ('FR', 'French'),
        ('EN', 'English'),
        ('FREN', 'French or English')
    ]

    LANGUAGE_PROFICIENCY_CHOICES = [
        ('NA', 'None'),
        ('BEG', 'Beginner'),
        ('INT', 'Intermediate'),
        ('ADV', 'Advanced')
    ]
    french_working_ability = models.CharField(
        choices=LANGUAGE_PROFICIENCY_CHOICES, max_length=200, null=True)
    english_working_ability = models.CharField(
        choices=LANGUAGE_PROFICIENCY_CHOICES, max_length=200, null=True)
    first_official_language = models.CharField(
        choices=LANGUAGE_CHOICES, max_length=200, null=True)
    written_exam = models.CharField(
        choices=LANGUAGE_CHOICES, max_length=200, null=True)
    correspondence = models.CharField(
        choices=LANGUAGE_CHOICES, max_length=200, null=True)
    interview = models.CharField(
        choices=LANGUAGE_CHOICES, max_length=200, null=True)

    pdf = models.FileField(upload_to="applications/", validators=[
        FileExtensionValidator(allowed_extensions=['pdf'])],
        blank=True)
    ranking = models.PositiveIntegerField(null=True)
    # For sorting purposes
    number_questions = models.PositiveIntegerField(default=0)
    number_yes_responses = models.PositiveIntegerField(default=0)
    percentage_correct = models.PositiveIntegerField(default=0)
    stream_count = models.PositiveIntegerField(default=0)
    classification_names = models.TextField(null=True)

    def __str__(self):
        return self.applicant_id

    def update_question_fields(self):
        self.number_questions = FormAnswer.objects.filter(
            parent_applicant=self).count()
        self.number_yes_responses = FormAnswer.objects.filter(
            parent_applicant=self, applicant_answer=True).count()
        self.percentage_correct = self.number_yes_responses * 100 // self.number_questions
        self.stream_count = Stream.objects.filter(
            parent_applicant=self).count()
        classifications = list(
            Classification.objects.filter(parent_applicant=self))
        self.classification_names = "".join([(classification.classification_substantive or "") for classification in classifications]).join(
            " ").join([(classification.classification_current or "") for classification in classifications])


class RequirementMet(models.Model):
    parent_applicant = models.ForeignKey(
        Applicant, on_delete=models.CASCADE, null=True, related_name='requirementsmet')
    requirement_type = models.CharField(max_length=200)
    abbreviation = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    met = models.BooleanField()

    def __str__(self):
        return self.abbreviation


class Stream(models.Model):
    parent_applicant = models.ForeignKey(
        Applicant, on_delete=models.CASCADE, null=True, related_name='streams')
    stream_name = models.CharField(max_length=200, null=True)
    stream_response = models.BooleanField(null=True)
    stream_description = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.stream_name


class Classification(models.Model):
    parent_applicant = models.ForeignKey(
        Applicant, on_delete=models.CASCADE, null=True, related_name='classifications')

    classification_substantive = models.CharField(max_length=200, null=True)
    classification_current = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.classification_substantive


class Education(models.Model):
    parent_applicant = models.ForeignKey(
        Applicant, on_delete=models.CASCADE, null=True, related_name='educations')
    academic_level = models.TextField(null=True)
    area_of_study = models.TextField(null=True)
    specialization = models.TextField(null=True)
    program_length = models.TextField(null=True)
    num_years_completed = models.TextField(null=True)
    institution = models.TextField(null=True)
    graduation_date = models.TextField(null=True)

    def __str__(self):
        return self.academic_level


class Requirement(models.Model):
    position = models.ForeignKey(
        Position, on_delete=models.CASCADE, null=True)
    requirement_type = models.CharField(max_length=200)
    abbreviation = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.position.__str__() + " - " + self.abbreviation


class FormQuestion(models.Model):
    parent_position = models.ForeignKey(
        Position, on_delete=models.CASCADE, null=True, related_name='questions')
    parent_requirement = models.ForeignKey(
        Requirement, on_delete=models.CASCADE, null=True, related_name='parent_req')
    question_text = models.TextField(blank=True, null=True)
    short_question_text = models.TextField(blank=True, null=True)
    complementary_question_text = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.question_text


class FormAnswer(models.Model):
    parent_question = models.ForeignKey(
        FormQuestion, on_delete=models.CASCADE, null=True, related_name='answer')
    parent_applicant = models.ForeignKey(
        Applicant, on_delete=models.CASCADE, null=True, related_name='answers')

    applicant_answer = models.BooleanField()
    applicant_complementary_response = models.TextField(
        blank=True, null=True)

    def __str__(self):
        return str(self.applicant_answer) + ": " + str(self.parent_question)


class Qualifier(models.Model):
    QUALIFIER_TYPES = [
        ('RECENCY', 'Recency'),
        ('SIGNIFICANCE', 'Significance')
    ]
    RESULT = [
        ('PASS', "Passed"),
        ('IND', "Indeterminate"),
        ('FAIL', "Failed")
    ]

    parent_answer = models.ForeignKey(
        FormAnswer, on_delete=models.CASCADE, null=True, related_name='qualifier')
    qualifier_text = models.TextField(
        blank=True, null=True)
    qualifier_type = models.CharField(
        choices=QUALIFIER_TYPES, max_length=200, null=True)
    status = models.CharField(
        choices=RESULT, max_length=200, null=True)

    def __str__(self):
        return str(self.qualifier_text)


class Note(models.Model):
    author = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name='author')
    parent_answer = models.ForeignKey(
        FormAnswer, on_delete=models.CASCADE, null=True, related_name='notes')
    note_text = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)


class NlpExtract(models.Model):
    EXTRACT_TYPES = [
        ('WHEN', 'A date or date range, and its context'),
        ('HOW', 'What applicant did to fulfill a requirement')
    ]
    parent_answer = models.ForeignKey(
        FormAnswer, on_delete=models.CASCADE, null=True, related_name='extract')
    extract_type = models.CharField(
        choices=EXTRACT_TYPES, max_length=200, null=True)
    extract_text = models.TextField()
    extract_sentence_index = models.PositiveIntegerField(null=True)
    extract_ending_index = models.PositiveIntegerField(null=True)
    next_extract_index = models.PositiveIntegerField(null=True)

    # for key, value in dates.items()
    def __str__(self):
        return str(self.extract_type) + ": " + str(self.extract_text)
