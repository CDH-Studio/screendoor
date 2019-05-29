from django.test import TestCase, Client
from django.urls import reverse
from screendoor.models import Position


class YourTestClass(TestCase):
    @classmethod
    def setUpTestData(cls):

        testPosition = Position
        testPosition.salary_min = 80274
        testPosition.salary_max = 86788
        testPosition.classification = "AS-05"
        testPosition.description = "Health Canada - Corporate Services Branch - Specialized Health Services Directorate Ottawa (Ontario) AS-05 Acting, Assignment, Deployment, Indeterminate, Secondment, Specified period"
        testPosition.open_to = "Employees of Health Canada working in National Capital Region (NCR)*"
        testPosition.reference_number = "SHC19J-020046-000203"
        testPosition.selection_process_number = "19-NHW-CSB-IA-NCR-262953"

        pass

    def test_parser(self):

        c = Client()
        with open('tests/Sample Job Poster.pdf'.format("Sample Job Poster.pdf"), 'rb') as file:
            response = c.post(reverse("importposition"), {'url_ref': "", 'pdf': file})

        html_response = response.content.decode()

        self.assertTrue(html_response.__contains__("name: Senior Program Support"))

        self.assertTrue(html_response.__contains__("date closed: May 21, 2019"))

        self.assertTrue(html_response.__contains__("num position: 1"))

        self.assertTrue(html_response.__contains__("salary: $80274 to $86788"))

        self.assertTrue(html_response.__contains__("classification: AS-05"))

        self.assertTrue(html_response.__contains__("description: Health Canada - Corporate Services Branch"))

        self.assertTrue(html_response.__contains__("<p>open to:  Employees of Health Canada working in National Capital"))

        self.assertTrue(html_response.__contains__("<p>reference number: SHC19J-020046-000203</p>"))

        self.assertTrue(html_response.__contains__("<p>selection process number: 19-NHW-CSB-IA-NCR-262953</p>"))

        # TODO need to find out how to test education/assets/experience
        pass
