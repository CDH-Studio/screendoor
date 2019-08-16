from django.test import TestCase, Client
from django.urls import reverse
from screendoor.models import Position, Applicant, Requirement, ScreenDoorUser
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import datetime
from screendoor.tasks import process_applications
from django.core.files.storage import FileSystemStorage

class TestPDFUpload(TestCase):
    @classmethod
    def setUp(self):
        self.c = Client()
        self.user = ScreenDoorUser.objects.create_user(
            username="good@canada.ca", 
            email="good@canada.ca",
            password="password76"
        )

        self.pdf_file = SimpleUploadedFile(
            "tests/Sample Job Poster.pdf",
            b"file_content",
            content_type="application/pdf"
        )

        self.testPosition = Position(
            position_title="Senior Program Support",
            classification="AS-05",
            reference_number="SHC19J-020046-000203",
            selection_process_number="19-NHW-CSB-IA-NCR-262953",
            date_closed= datetime(2019, 5, 21, 23, 59),
            num_positions="1",
            open_to="Employees of Health Canada working in National Capital Region (NCR)*",
            salary="$80,274 to $86,788"
        )

        self.ed1 = Requirement(
            requirement_type="Education",
            abbreviation="ED1",
            description="Successful completion of a secondary school diploma, or an acceptable combination of education, training and/or experience relevant to the position."
        )

        self.exp1 = Requirement(
            requirement_type="Experience",
            abbreviation="EXP1",
            description="Experience in managing and/or operating information management system(s)."
        )
        self.exp2 = Requirement(
            requirement_type="Experience",
            abbreviation="EXP2",
            description="Experience in capturing and validating clients' business requirements."
        )
        self.exp3 = Requirement(
            requirement_type="Experience",
            abbreviation="EXP3",
            description="Experience in developing procedures and/or program training."
        )
        self.exp4 = Requirement(
            requirement_type="Experience",
            abbreviation="EXP4",
            description="Experience in developing and maintaining stakeholder relationships with government and/or private sector."
        )

        self.aexp1 = Requirement(
            requirement_type="Asset",
            abbreviation="AEXP1",
            description="Experience in managing a program trianing plan geared at both internal and external partners."
        )
        self.aexp2 = Requirement(
            requirement_type="Asset",
            abbreviation="AEXP2",
            description="Experience in working in a health care environment."
        )
        self.aexp3 = Requirement(
            requirement_type="Asset",
            abbreviation="AEXP3",
            description="Experience in project management."
        )
        self.aexp4 = Requirement(
            requirement_type="Asset",
            abbreviation="AEXP4",
            description="Experience in managing change initiatives within an organization."
        )

        self.application_pdf_file = SimpleUploadedFile(
            "tests/Sample_Application.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        self.testPosition.save()

        self.testApplication = Applicant(
            citizenship='Canadian Citizen',
            priority=False,
            veteran_preference=False,
            french_working_ability='Advanced',
            english_working_ability='Advanced',
            first_official_language='French',
            written_exam='English',
            correspondence='English',
            interview='English',
            number_questions=24,
            number_yes_responses=13,
            percentage_correct=54,
            stream_count=2
        )

    def test_parser_against_position_info(self):
        self.c.login(username="good@canada.ca", password="password76")
        with open('tests/Sample Job Poster.pdf'.format("Sample Job Poster.pdf"), 'rb') as file:
            response = self.c.post(reverse("importposition"), {'url_ref': "", 'pdf': file})

        self.assertEqual(self.testPosition.position_title, 
            response.context['position'].position_title.strip())

        self.assertEqual(self.testPosition.classification, 
            response.context['position'].classification.strip())

        self.assertEqual(self.testPosition.reference_number, 
            response.context['position'].reference_number.strip())

        self.assertEqual(self.testPosition.selection_process_number, 
            response.context['position'].selection_process_number.strip())

        self.assertEqual(self.testPosition.date_closed, 
            response.context['position'].date_closed)

        self.assertEqual(str(self.testPosition.num_positions), 
            response.context['position'].num_positions.strip())

        self.assertEqual(self.testPosition.salary, 
            response.context['position'].salary.strip())

        self.assertEqual(self.testPosition.open_to,
            response.context['position'].open_to.strip())


    def test_parser_against_requirements(self):
        self.c.login(username="good@canada.ca", password="password76")
        with open('tests/Sample Job Poster.pdf'.format("Sample Job Poster.pdf"), 'rb') as file:
            response = self.c.post(reverse("importposition"), {'url_ref': "", 'pdf': file})

        self.assertEqual(self.ed1.requirement_type, 
            response.context['position'].requirement_set.all()[8].requirement_type.strip())
        self.assertEqual(self.ed1.abbreviation, 
            response.context['position'].requirement_set.all()[8].abbreviation.strip())
        self.assertEqual(self.ed1.description, 
            response.context['position'].requirement_set.all()[8].description.strip())

        self.assertEqual(self.exp1.requirement_type, 
            response.context['position'].requirement_set.all()[7].requirement_type.strip())
        self.assertEqual(self.exp1.abbreviation, 
            response.context['position'].requirement_set.all()[7].abbreviation.strip())
        self.assertEqual(self.exp1.description, 
            response.context['position'].requirement_set.all()[7].description.strip())

        self.assertEqual(self.exp2.requirement_type, 
            response.context['position'].requirement_set.all()[6].requirement_type.strip())
        self.assertEqual(self.exp2.abbreviation, 
            response.context['position'].requirement_set.all()[6].abbreviation.strip())
        self.assertEqual(self.exp2.description, 
            response.context['position'].requirement_set.all()[6].description.strip())

        self.assertEqual(self.exp3.requirement_type, 
            response.context['position'].requirement_set.all()[5].requirement_type.strip())
        self.assertEqual(self.exp3.abbreviation, 
            response.context['position'].requirement_set.all()[5].abbreviation.strip())
        self.assertEqual(self.exp3.description, 
            response.context['position'].requirement_set.all()[5].description.strip())

        self.assertEqual(self.exp4.requirement_type, 
            response.context['position'].requirement_set.all()[4].requirement_type.strip())
        self.assertEqual(self.exp4.abbreviation, 
            response.context['position'].requirement_set.all()[4].abbreviation.strip())
        self.assertEqual(self.exp4.description, 
            response.context['position'].requirement_set.all()[4].description.strip())

        self.assertEqual(self.aexp1.requirement_type, 
            response.context['position'].requirement_set.all()[3].requirement_type.strip())
        self.assertEqual(self.aexp1.abbreviation, 
            response.context['position'].requirement_set.all()[3].abbreviation.strip())
        self.assertEqual(self.aexp1.description, 
            response.context['position'].requirement_set.all()[3].description.strip())

        self.assertEqual(self.aexp2.requirement_type, 
            response.context['position'].requirement_set.all()[2].requirement_type.strip())
        self.assertEqual(self.aexp2.abbreviation, 
            response.context['position'].requirement_set.all()[2].abbreviation.strip())
        self.assertEqual(self.aexp2.description, 
            response.context['position'].requirement_set.all()[2].description.strip())

        self.assertEqual(self.aexp3.requirement_type, 
            response.context['position'].requirement_set.all()[1].requirement_type.strip())
        self.assertEqual(self.aexp3.abbreviation, 
            response.context['position'].requirement_set.all()[1].abbreviation.strip())
        self.assertEqual(self.aexp3.description, 
            response.context['position'].requirement_set.all()[1].description.strip())

        self.assertEqual(self.aexp4.requirement_type, 
            response.context['position'].requirement_set.all()[0].requirement_type.strip())
        self.assertEqual(self.aexp4.abbreviation, 
            response.context['position'].requirement_set.all()[0].abbreviation.strip())
        self.assertEqual(self.aexp4.description, 
            response.context['position'].requirement_set.all()[0].description.strip())


    def test_application_upload_redirects(self):
        self.c.login(username="good@canada.ca", password="password76")
        with open('tests/Sample_Application.pdf'.format("Sample_Application.pdf"), 'rb') as file:
            response = self.c.post(reverse("upload-applications"), {'upload-applications': True, 'position-id': self.testPosition.id, 'pdf': file})
            
        self.assertEqual(response.status_code, 302)   

    def test_application_processing(self):
        self.c.login(username="good@canada.ca", password="password76")
        with open('tests/Sample_Application.pdf'.format("Sample_Application.pdf"), 'rb') as file:
            file_name = FileSystemStorage().save(file.name.replace(' ', ''), file)
            file_path = FileSystemStorage().url(file_name) 
            process_applications([file_path], self.testPosition.id)

        self.assertEqual(self.testPosition.applicant_set.all()[0].citizenship.strip(), 
            self.testApplication.citizenship.strip())
        self.assertEqual(self.testPosition.applicant_set.all()[0].priority, 
            self.testApplication.priority)
        self.assertEqual(self.testPosition.applicant_set.all()[0].veteran_preference, 
            self.testApplication.veteran_preference)
        self.assertEqual(self.testPosition.applicant_set.all()[0].french_working_ability.strip(), 
            self.testApplication.french_working_ability.strip())
        self.assertEqual(self.testPosition.applicant_set.all()[0].english_working_ability.strip(), 
            self.testApplication.english_working_ability.strip())
        self.assertEqual(self.testPosition.applicant_set.all()[0].first_official_language.strip(), 
            self.testApplication.first_official_language.strip())
        self.assertEqual(self.testPosition.applicant_set.all()[0].written_exam.strip(), 
            self.testApplication.written_exam.strip())
        self.assertEqual(self.testPosition.applicant_set.all()[0].correspondence.strip(), 
            self.testApplication.correspondence.strip())
        self.assertEqual(self.testPosition.applicant_set.all()[0].interview.strip(), 
            self.testApplication.interview.strip())
        self.assertEqual(self.testPosition.applicant_set.all()[0].number_questions, 
            self.testApplication.number_questions)
        self.assertEqual(self.testPosition.applicant_set.all()[0].number_yes_responses, 
            self.testApplication.number_yes_responses)
        self.assertEqual(self.testPosition.applicant_set.all()[0].percentage_correct, 
            self.testApplication.percentage_correct)
        self.assertEqual(self.testPosition.applicant_set.all()[0].stream_count, 
            self.testApplication.stream_count)
        
#python manage.py test