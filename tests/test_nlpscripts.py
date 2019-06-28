from django.test import TestCase
from django.test.client import Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from screendoor.NLP.whenextraction import extract_dates
from screendoor.NLP.howextraction import extract_how
import re

def format_text(text):
    return re.sub(r"\n(?=[A-Z])", ". ", text).replace("..", ".").replace("\n\n", ". ").replace(' - ', '-').replace('-', ' - ')

debug_when_tests = False
debug_how_tests = False

class WhenExtractionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        with open('tests/Sample NLP Text Blocks.txt', encoding='utf8') as f:
            text = f.read().split('\n\n')
            cls.block_1 = format_text(text[0])
            cls.block_2 = format_text(text[1])
            cls.block_3 = format_text(text[2])
            cls.block_4 = format_text(text[3])
            cls.block_5 = format_text(text[4])
            cls.block_6 = format_text(text[5])

    def test_block_1(self):
        dates = extract_dates(self.block_1)
        if debug_when_tests:
            print(dates)
            print ('\n\n')

        self.assertTrue(dates['since June 2014'],
                        'Some of the IM/IT projects managed at PCO ')
        self.assertTrue(dates['between March 2010 and June 2014'],
                        'At OCOL ')
        self.assertTrue(dates['March 2014'],
                        'Managed the physical move of the Library ')

    def test_block_2(self):
        dates = extract_dates(self.block_2)
        if debug_when_tests:
            print(dates)
            print('\n\n')

        self.assertTrue(dates['7/2013-4/2015'],
                        '\n1.Statistics Canada New Dissemination Model (NDM) Navigation Project - Project Leader ')
        self.assertTrue(dates['09/2012-01/2013'],
                        'Statistics Canada Census CLF3 conversion - Project Leader')

    def test_block_3(self):
        dates = extract_dates(self.block_3)
        if debug_when_tests:
            print(dates)
            print('\n\n')

        self.assertTrue(dates['December 2010 to October 2015'],
                        'Team Lead - Systems Maintenance at CNSC ')

    def test_block_4(self):
        dates = extract_dates(self.block_4)
        if debug_when_tests:
            print(dates)
            print('\n\n')

        self.assertTrue(dates[', 2011-2014'],
                        'My previous position at Courts administration services operations manager ')

    def test_block_5(self):
        dates = extract_dates(self.block_5)
        if debug_when_tests:
            print(dates)
            print('\n\n')

        self.assertTrue(dates['From December 2012 until April 2013'],
                        'as the acting manager for the Master data Management the Enterprise Portal section')
        self.assertTrue(dates['From June 2011 until November 2012 and from October 2014 until April 2015 and from October 2015 until the present'],
                        'as the BIRS\ninfrastructure and production services Project Leader BIRS acting Manager')
        self.assertTrue(dates['From March 2010 until May 2011'],
                        'as the Titan production support CSC Team Leader ')
        self.assertTrue(dates['From April 2008 until March 2010'],
                        'as the AMPS project leader ')
        self.assertTrue(dates['March 2012'],
                        'completed the CBSA staffing sub-delegation ')

    def test_block_6(self):
        dates = extract_dates(self.block_6)
        self.assertTrue(dates['since April 2008 until the present'],
                        'acquired a broad\nrange of experiences in IT application development ')
        self.assertTrue(dates['From October 2015 until the present'],
                        'as the DW COTS infrastructure team leader ')
        self.assertTrue(dates['From October 2014 until April 2015'],
                        'as the BIRS infrastructure and production support Team leader ')
        self.assertTrue(dates['From March 2010 until May 2011'],
                        'leading a multi-disciplinary technical team ')
        
        
class HowExtractionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        with open('tests/Sample NLP Text Blocks.txt', encoding='utf8') as f:
            text = f.read().split('\n\n')
            cls.block_1 = format_text(text[0])
            cls.block_2 = format_text(text[1])
            cls.block_3 = format_text(text[2])
            cls.block_4 = format_text(text[3])
            cls.block_5 = format_text(text[4])
            cls.block_6 = format_text(text[5])

    def test_block_1(self):
        experiences = extract_how(self.block_1)
        if debug_how_tests:
            print(experiences)
            print('\n\n')

        self.assertTrue("managed my team's functional testing and troubleshooting activities of the upgraded EDMS software and all interactions with the information technology(IT) programmers for two networks(Protected B and Secret)."
                    in experiences)
        self.assertTrue('informed business group representatives(stakeholders) weekly of progress through conference calls...'
                        in experiences)
        self.assertTrue('managed the deployment of the EDMS(RDIMS / eDOCS) to two new client groups(150 users)...'
                        in experiences)
        self.assertTrue('engaging key personnel in the client and IM Policy groups...'
                        in experiences)
        self.assertTrue('facilitated the department-wide implementation of the EDRMS(GCDOCS)...'
                        in experiences)
        self.assertTrue('facilitated the department-wide implementation of the EDRMS by managing the department-wide training efforts to all our offices throughout Canada...'
                        in experiences)

    def test_block_2(self):
        experiences = extract_how(self.block_2)
        if debug_how_tests:
            print(experiences)
            print('\n\n')

        self.assertTrue(
            "led the team throughout the project lifecycle including organizing and leading requirements gathering in JAD sessions, analysis, developing project plan and schedules..."
            in experiences)
        self.assertTrue(
            'ensured NDM Navigation portal was designed in such a way that it was flexible, scalable,...'
            in experiences)
        self.assertTrue(
            'Led a team of 4 developers in converting a CLF2 based website to be CLF3 compliant using ColdFusion, HTML5...'
            in experiences)
        self.assertTrue(
            'Coordinated with SSC for deployment of releases.'
            in experiences)

    def test_block_3(self):
        experiences = extract_how(self.block_3)
        if debug_how_tests:
            print(experiences)
            print('\n\n')

        self.assertTrue(
            "was responsible for all aspects relating to contracted resources..."
            in experiences)
        self.assertTrue(
            'have worked closely with the contracting team here at CNSC...'
            in experiences)
        self.assertTrue(
            'have also been involved in the contract review committee for the organization...'
            in experiences)


    def test_block_4(self):
        experiences = extract_how(self.block_4)
        if debug_how_tests:
            print(experiences)
            print('\n\n')

        self.assertTrue(
            "presented a DECK to the DCA and EXCOM recommending and advising on the feasibilities of these initiatives / Projects."
            in experiences)
        self.assertTrue(
            'presented my recommendations based on: Client requirements, Scope, Cost, Risk/ restraints, Timelines and PROS/CONS.'
            in experiences)

    def test_block_5(self):
        experiences = extract_how(self.block_5)
        if debug_how_tests:
            print(experiences)
            print('\n\n')

        self.assertTrue(
            "acquired an extensive experience in leading a technical teams..."
            in experiences)
        self.assertTrue(
            'completed the CBSA staffing sub-delegation in March 2012.'
            in experiences)
        self.assertTrue(
            'assigned technical specialists to workgroups and projects...'
            in experiences)

    def test_block_6(self):
        experiences = extract_how(self.block_6)
        if debug_how_tests:
            print(experiences)
            print('\n\n')

        self.assertTrue(
            "acquired a broad range of experiences in IT application development..."
            in experiences)
        self.assertTrue(
            ' was leading a multi-disciplinary technical team responsible for the maintenance and the production support the web based IT application Titan.'
            in experiences)

#python manage.py test
