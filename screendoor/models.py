import base64
import datetime
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from cryptography.fernet import Fernet


class FormQuestion(models.Model):
    question_text = models.CharField(max_length=200)
    complementary_question_text = models.CharField(max_length=200)
    applicant_answer = models.BooleanField()
    applicant_complementary_response = models.CharField(
        max_length=200, blank=True)
    parsed_response = models.CharField(max_length=200, blank=True)
    analysis = models.CharField(max_length=200, blank=True)
    tabulation = models.CharField(max_length=200)

    def __str__(self):
        return self.questio_text


class RequirementMet(models.Model):
    requirement_type = models.CharField(max_length=200)
    abbreviation = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    met = models.BooleanField()

    def __str__(self):
        return self.abbreviation


class Stream(models.Model):
    stream_name = models.CharField(max_length=200)

    def __str__(self):
        return self.stream_name


class Classification(models.Model):
    classification_name = models.CharField(max_length=200)

    def __str__(self):
        return self.classification_name


class Education(models.Model):
    academic_level = models.CharField(max_length=200)
    area_of_study = models.CharField(max_length=200)
    specialization = models.CharField(max_length=200)
    program_length = models.PositiveIntegerField()
    num_years_completed = models.PositiveIntegerField()
    institution = models.CharField(max_length=200)
    graduation_date = models.CharField(max_length=200)

    def __str__(self):
        return self.area_of_study


class Applicant(models.Model):
    name = models.CharField(max_length=200)
    date_of_birth = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=200)
    email = models.EmailField()
    pri = models.PositiveIntegerField()
    citizenship = models.CharField(max_length=200)
    priority = models.BooleanField()
    address = models.CharField(max_length=200)
    veteran_preference = models.BooleanField()

    LANGUAGE_CHOICES = [
        ('FR', 'French'),
        ('EN', 'English')
    ]

    LANGUAGE_PROFICIENCY_CHOICES = [
        ('NA', 'None'),
        ('BEG', 'Beginner'),
        ('INT', 'Intermediate'),
        ('ADV', 'Advanced')
    ]
    french_working_ability = models.CharField(
        choices=LANGUAGE_PROFICIENCY_CHOICES, max_length=200)
    english_working_ability = models.CharField(
        choices=LANGUAGE_PROFICIENCY_CHOICES, max_length=200)
    first_official_language = models.CharField(
        choices=LANGUAGE_CHOICES, max_length=200)
    written_exam = models.CharField(choices=LANGUAGE_CHOICES, max_length=200)
    correspondence = models.CharField(choices=LANGUAGE_CHOICES, max_length=200)
    interview = models.CharField(choices=LANGUAGE_CHOICES, max_length=200)

    requirements_met = models.ManyToManyField(
        RequirementMet, symmetrical=False)
    streams_selected = models.ManyToManyField(Stream, symmetrical=False)
    classifications_selected = models.ManyToManyField(
        Classification, symmetrical=False)
    educations = models.ManyToManyField(Education, symmetrical=False)

    questions = models.ManyToManyField(
        FormQuestion, symmetrical=False, blank=True)
    pdf = models.FileField()
    ranking = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class Position(models.Model):
    applications = models.ManyToManyField(
        Applicant, symmetrical=False, blank=True)
    position_title = models.CharField(max_length=200, blank=True)
    date_closed = models.DateField(null=True, blank=True)
    num_positions = models.PositiveIntegerField(null=True, blank=True)
    salary_min = models.DecimalField(
        decimal_places=2, max_digits=10, null=True, blank=True)
    salary_max = models.DecimalField(
        decimal_places=2, max_digits=10, null=True, blank=True)
    classification = models.CharField(max_length=200, blank=True)
    department = models.CharField(max_length=200, blank=True)
    location = models.CharField(max_length=200, blank=True)
    open_to = models.CharField(max_length=200, blank=True)
    reference_number = models.CharField(max_length=200, blank=True)
    selection_process_number = models.CharField(max_length=200, blank=True)
    pdf = models.FileField(upload_to="positions/", validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
                           blank=True)
    url_ref = models.URLField(max_length=200, blank=True)

    def __str__(self):
        return self.position_title


class Requirement(models.Model):
    position = models.ForeignKey(
        Position, on_delete=models.SET_NULL, null=True)
    requirement_type = models.CharField(max_length=200)
    abbreviation = models.CharField(max_length=200)
    description = models.CharField(max_length=200)

    def __str__(self):
        return self.abbreviation


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
