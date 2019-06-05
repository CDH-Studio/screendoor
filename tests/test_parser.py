from django.test import TestCase, Client
from django.urls import reverse
from screendoor.models import Position, Requirement, ScreenDoorUser
from django.core.files.uploadedfile import SimpleUploadedFile

class YourTestClass(TestCase):
    @classmethod
    def setUp(self):
        self.c = Client()
        self.user = ScreenDoorUser.objects.create_user(
            username="good@canada.ca", email="good@canada.ca",
            password="password76")
        self.pdf_file = SimpleUploadedFile("tests/Sample Job Poster.pdf",
                                               b"file_content",
                                               content_type="application/pdf")
        self.testPosition = Position(position_title="Senior Program Support",
                                     classification="AS-05",
                                     reference_number="SHC19J-020046-00020",
                                     selection_process_number="19-NHW-CSB-IA-NCR-262953",
                                     date_closed="May 21, 2019",
                                     num_positions="1",
                                     open_to="Employees of Health Canada working in National Capital Region (NCR)*",
                                     salary_min=80274,
                                     salary_max=86788,
                                     description="Health Canada - Corporate Services Branch - Specialized Health Services Directorate Ottawa (Ontario) AS-05 Acting, Assignment, Deployment, Indeterminate, Secondment, Specified period"
                                     )
        self.ed1 = Requirement(requirement_type="Education",
                          abbreviation="ED1",
                          description="Successful completion of a secondary school diploma, or an acceptable combination of education, training and/or experience relevant to the position.")
        self.exp1 = Requirement(requirement_type="Experience",
                           abbreviation="EXP1",
                           description="Experience in managing and/or operating information management system(s)")
        self.exp2 = Requirement(requirement_type="Experience",
                           abbreviation="EXP2",
                           description="Experience in capturing and validating clients&#39; business requirements")
        self.exp3 = Requirement(requirement_type="Experience",
                           abbreviation="EXP3",
                           description="Experience in developing procedures and/or program training")
        self.exp4 = Requirement(requirement_type="Experience",
                           abbreviation="EXP4",
                           description="Experience in developing and maintaining stakeholder relationships with government and/or private sector.")
        self.aexp1 = Requirement(requirement_type="Asset",
                            abbreviation="AEXP1",
                            description="ASSET  Experience in managing a program trianing plan geared at both internal and external partners")
        self.aexp2 = Requirement(requirement_type="Asset",
                            abbreviation="AEXP2",
                            description="Experience in working in a health care environment")
        self.aexp3 = Requirement(requirement_type="Asset",
                            abbreviation="AEXP3",
                            description="Experience in project management")
        self.aexp4 = Requirement(requirement_type="Asset",
                            abbreviation="AEXP3",
                            description="Experience in managing change initiatives within an organization.")

    def validate_parser_against_premade_fields(self):
        self.c.login(username="good@canada.ca", password="password76")
        with open('tests/Sample Job Poster.pdf'.format("Sample Job Poster.pdf"), 'rb') as file:
            response = self.c.post(reverse("importposition"), {'url_ref': "", 'pdf': file})

        html_response = response.content.decode()
        self.assertTrue(self.testPosition.position_title in html_response)

        self.assertTrue(self.testPosition.classification in html_response)

        self.assertTrue(self.testPosition.reference_number in html_response)

        self.assertTrue(self.testPosition.selection_process_number in html_response)

        self.assertTrue(self.testPosition.date_closed in html_response)

        self.assertTrue(str(self.testPosition.num_positions) in html_response)

        self.assertTrue(str(self.testPosition.salary_min) in html_response)

        self.assertTrue(str(self.testPosition.salary_max) in html_response)

        self.assertTrue(self.testPosition.open_to in html_response)

        self.assertTrue(self.testPosition.description in html_response)

        self.assertTrue(self.ed1.description in html_response)

        self.assertTrue(self.exp1.description in html_response)

        self.assertTrue(self.exp2.description in html_response)

        self.assertTrue(self.exp3.description in html_response)

        self.assertTrue(self.exp4.description in html_response)

        self.assertTrue(self.aexp1.description in html_response)

        self.assertTrue(self.aexp2.description in html_response)

        self.assertTrue(self.aexp3.description in html_response)

        self.assertTrue(self.aexp3.description in html_response)
