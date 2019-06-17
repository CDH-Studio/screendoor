import base64
import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from cryptography.fernet import Fernet


class Position(models.Model):
    position_title = models.CharField(max_length=200, blank=True)
    date_closed = models.DateField(null=True, blank=True)
    num_positions = models.CharField(max_length=200, blank=True)
    salary_min = models.DecimalField(
        decimal_places=2, max_digits=10, null=True, blank=True)
    salary_max = models.DecimalField(
        decimal_places=2, max_digits=10, null=True, blank=True)
    classification = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    open_to = models.CharField(max_length=200, blank=True)
    reference_number = models.CharField(max_length=200, blank=True)
    selection_process_number = models.CharField(max_length=200, blank=True)
    pdf = models.FileField(upload_to="positions/", validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
                           blank=True)
    url_ref = models.URLField(max_length=200, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self): 3
    return self.position_title


class Applicant(models.Model):
    parent_position = models.ForeignKey(
        Position, on_delete=models.CASCADE, null=True)
    applicant_id = models.CharField(max_length=200, null=True)
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

    def __str__(self):
        return self.applicant_id


class RequirementMet(models.Model):
    parent_application = models.ForeignKey(
        Applicant, on_delete=models.CASCADE, null=True, related_name='requirementsmet')
    requirement_type = models.CharField(max_length=200)
    abbreviation = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    met = models.BooleanField()

    def __str__(self):
        return self.abbreviation


class Stream(models.Model):
    parent_application = models.ForeignKey(
        Applicant, on_delete=models.CASCADE, null=True, related_name='streams')
    stream_name = models.CharField(max_length=200)

    def __str__(self):
        return self.stream_name


class Classification(models.Model):
    parent_application = models.ForeignKey(
        Applicant, on_delete=models.CASCADE, null=True, related_name='classifications')

    classification_name = models.CharField(max_length=200)

    def __str__(self):
        return self.classification_name


class Education(models.Model):
    parent_application = models.ForeignKey(
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


class FormQuestion(models.Model):
    parent_applicant = models.ForeignKey(
        Applicant, on_delete=models.CASCADE, null=True, related_name='questions')

    question_text = models.TextField(blank=True, null=True)
    complementary_question_text = models.TextField(blank=True, null=True)
    applicant_answer = models.BooleanField(null=True)
    applicant_complementary_response = models.TextField(blank=True, null=True)
    parsed_response = models.CharField(max_length=1000, blank=True, null=True)
    analysis = models.CharField(max_length=1000, blank=True, null=True)
    tabulation = models.CharField(max_length=1000, null=True)

    def __str__(self):
        return self.question_text


class Requirement(models.Model):
    position = models.ForeignKey(
        Position, on_delete=models.CASCADE, null=True)
    requirement_type = models.CharField(max_length=200)
    abbreviation = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.position.__str__() + " - " + self.abbreviation


class ScreenDoorUser(AbstractUser):
    email_confirmed = models.BooleanField(default=False)
    positions = models.ManyToManyField(Position, blank=True)

    def confirm_email(self):
        self.email_confirmed = True


class EmailAuthenticateToken(models.Model):
    user = models.OneToOneField(
        get_user_model(), on_delete=models.CASCADE, primary_key=False)
    key = models.CharField(max_length=500, null=True)

    def create_key(self):
        initial_key = Fernet.generate_key()
        byte_values = bytes(str(self.user.email) +
                            str(datetime.datetime.now()), 'utf-8')
        encoded_bytes = Fernet(initial_key).encrypt(byte_values)
        self.key = base64.b64encode(encoded_bytes).decode('utf-8')
