from django.http import HttpRequest
from django.test import TestCase, Client

from screendoor.forms import CreatePositionForm
from screendoor.models import Position, Requirement
from screendoor.parseposter import parse_upload


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

    def setUp(self):

        c = Client()
        with open('SampleJobPoster.doc') as fp:
            c.post('/createnewposition/', {'name': 'fred', 'attachment': fp})

        request = HttpRequest


        create_position_form = CreatePositionForm(request.POST, request.FILES)
        requestedPosition = create_position_form.save()
        parsedPosition = parse_upload(requestedPosition)


        pass

    def test_false_is_false(self):
        print("Method: test_false_is_false.")
        self.assertFalse(False)

    def test_false_is_true(self):
        print("Method: test_false_is_true.")
        self.assertTrue(False)

    def test_one_plus_one_equals_two(self):
        print("Method: test_one_plus_one_equals_two.")
        self.assertEqual(1 + 1, 2)