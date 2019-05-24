from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator


class FormQuestion(models.Model):
    questionText = models.CharField(max_length=200)
    complementaryQuestionText = models.CharField(max_length=200)
    applicantAnswer = models.BooleanField()
    applicantComplementaryResponse = models.CharField(max_length=200, blank=True)
    parsedResponse = models.CharField(max_length=200, blank=True)
    analysis = models.CharField(max_length=200, blank=True)
    tabulation = models.CharField(max_length=200)

    def __str__(self):
        return self.questionText


class RequirementMet(models.Model):
    requirementType = models.CharField(max_length=200)
    abbreviation = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    met = models.BooleanField()

    def __str__(self):
        return self.abbreviation


class Stream(models.Model):
    streamName = models.CharField(max_length=200)

    def __str__(self):
        return self.streamName


class Classification(models.Model):
    classificationName = models.CharField(max_length=200)

    def __str__(self):
        return self.classificationName


class Education(models.Model):
    academicLevel = models.CharField(max_length=200)
    areaOfStudy = models.CharField(max_length=200)
    specialization = models.CharField(max_length=200)
    programLength = models.PositiveIntegerField()
    numYearsCompleted = models.PositiveIntegerField()
    institution = models.CharField(max_length=200)
    graduationDate = models.CharField(max_length=200)

    def __str__(self):
        return self.areaOfStudy


class Applicant(models.Model):
    name = models.CharField(max_length=200)
    dateOfBirth = models.CharField(max_length=200)
    phoneNumber = models.CharField(max_length=200)
    email = models.EmailField()
    pri = models.PositiveIntegerField()
    citizenShip = models.CharField(max_length=200)
    priority = models.BooleanField()
    address = models.CharField(max_length=200)
    veteranPreference = models.BooleanField()

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
    frenchWorkingAbility = models.CharField(choices=LANGUAGE_PROFICIENCY_CHOICES, max_length=200)
    englishWorkingAbility = models.CharField(choices=LANGUAGE_PROFICIENCY_CHOICES, max_length=200)
    firstOfficialLanguage = models.CharField(choices=LANGUAGE_CHOICES, max_length=200)
    writtenExam = models.CharField(choices=LANGUAGE_CHOICES, max_length=200)
    correspondence = models.CharField(choices=LANGUAGE_CHOICES, max_length=200)
    interview = models.CharField(choices=LANGUAGE_CHOICES, max_length=200)

    requirementsMet = models.ManyToManyField(RequirementMet, symmetrical=False)
    streamsSelected = models.ManyToManyField(Stream, symmetrical=False)
    classificationsSelected = models.ManyToManyField(Classification, symmetrical=False)
    educations = models.ManyToManyField(Education, symmetrical=False)

    questions = models.ManyToManyField(FormQuestion, symmetrical=False, blank=True)
    pdf = models.FileField()
    ranking = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class Position(models.Model):
    applications = models.ManyToManyField(Applicant, symmetrical=False, blank=True)
    positionTitle = models.CharField(max_length=200, blank=True)
    dateClosed = models.DateField(null=True, blank=True)
    numPositions = models.PositiveIntegerField(null=True, blank=True)
    SalaryMin = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    salaryMax = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    classification = models.CharField(max_length=200, blank=True)
    department = models.CharField(max_length=200, blank=True)
    Location = models.CharField(max_length=200, blank=True)
    OpenTo = models.CharField(max_length=200, blank=True)
    referenceNumber = models.CharField(max_length=200, blank=True)
    selectionProcessNumber = models.CharField(max_length=200, blank=True)
    pdf = models.FileField(upload_to="positions/", validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
                           blank=True)
    urlRef = models.URLField(max_length=200, blank=True)

    def __str__(self):
        return self.positionTitle


class Requirement(models.Model):
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True)
    requirementType = models.CharField(max_length=200)
    abbreviation = models.CharField(max_length=200)
    description = models.CharField(max_length=200)

    def __str__(self):
        return self.abbreviation


class ScreenDoorUser(AbstractUser):
    positions = models.ManyToManyField(Position, blank=True)
