from django.test import TestCase
from django.test.client import Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from screendoor.NLP.when_extraction import extract_when
from screendoor.NLP.how_extraction import extract_how
from screendoor_app.settings import NLP_MODEL
from screendoor.NLP.helpers.format_text import post_nlp_format_input, strip_faulty_formatting, replace_acronyms_with_full_month
import re

def create_doc(text):
    orig_doc = NLP_MODEL(text)
    
    reformatted_text = post_nlp_format_input(orig_doc)
    reformatted_text = replace_acronyms_with_full_month(strip_faulty_formatting(reformatted_text))
    return NLP_MODEL(reformatted_text)


def create_tuples_of_indices(extracted_list):
    tuples = []
    for elem in extracted_list:
        tuples.append((elem[1], elem[2]))
    return tuples

class WhenExtractionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        with open('tests/Sample NLP Text Blocks.txt', encoding='utf8') as f:
            text = f.read().split('\n\n')
            cls.block_1 = extract_when(text[0], create_doc(text[0]))
            cls.block_2 = extract_when(text[1], create_doc(text[1]))
            cls.block_3 = extract_when(text[2], create_doc(text[2]))
            cls.block_4 = extract_when(text[3], create_doc(text[3]))


    def test_block_1_extracts(self):
        self.assertEqual(self.block_1[0][0],
        'since June 2014: Some of the IM/ IT projects I have managed at PCO')
        self.assertEqual(self.block_1[1][0],
        'between March 2010 and June 2014: At OCOL between March 2010 and June 2014')
        self.assertEqual(self.block_1[2][0],
        "March 2014: Managed the weeding process of the Library's paper collection")
        self.assertEqual(self.block_1[3][0],
        'March 2014: Managed the physical move of the Records Management office')
        self.assertEqual(self.block_1[4][0],
        'March 2014: Managed the physical move of the Library')
        

    def test_block_1_indices(self):
        indices = create_tuples_of_indices(self.block_1)
        self.assertEqual(indices[0], (0, 48))
        self.assertEqual(indices[1], (1369, 1409))
        self.assertEqual(indices[2], (3531, 3592))
        self.assertEqual(indices[3], (3634, 3692))
        self.assertEqual(indices[4], (3710, 3750))


    def test_block_2_extracts(self):
        self.assertEqual(self.block_2[0][0],
        'December 2010 to October 2015: Team Lead - Systems Maintenance at CNSC')
        

    def test_block_2_indices(self):
        indices = create_tuples_of_indices(self.block_2)
        self.assertEqual(indices[0], (1, 40))


    def test_block_3_extracts(self):
        self.assertEqual(self.block_3[0][0],
        '2011 - 2014: at Courts administration services (operations manager, 2011 - 2014')
        self.assertEqual(self.block_3[1][0],
        '2012: while working at CAS I')
        self.assertEqual(self.block_3[2][0],
        '2013: I presented recommendations to IT Director General')
        self.assertEqual(self.block_3[3][0],
        'February 2014: Project; approved and in pilot mode')


    def test_block_3_indices(self):
        indices = create_tuples_of_indices(self.block_3)
        self.assertEqual(indices[0], (22, 86))
        self.assertEqual(indices[1], (1150, 1172))
        self.assertEqual(indices[2], (1626, 1676))
        self.assertEqual(indices[3], (2068, 2102))   


    def test_block_4_extracts(self):
        self.assertEqual(self.block_4[0][0],
        'since April 2008 until the present: I acquired over the years')
        self.assertEqual(self.block_4[1][0],
        'From December 2012 until April 2013: as the acting manager for the Master data Management and the Enterprise Portal section')
        self.assertEqual(self.block_4[2][0],
        'From June 2011 until November 2012: infrastructure and production services Project Leader and BIRS acting Manager')
        self.assertEqual(self.block_4[3][0],
        'from October 2014 until April 2015: and from October 2015 until the present as the BIRS')
        self.assertEqual(self.block_4[4][0],
        'from October 2015 until the present: as the BIRS')
        self.assertEqual(self.block_4[5][0],
        'From March 2010 until May 2011: as the Titan production support and CSC Team Leader')
        self.assertEqual(self.block_4[6][0],
        'From April 2008 until March 2010: as the AMPS project leader')
        self.assertEqual(self.block_4[7][0],
        'March 2012: I completed the CBSA staffing sub - delegation')


    def test_block_4_indices(self):
        indices = create_tuples_of_indices(self.block_4)
        self.assertEqual(indices[0], (104, 129))
        self.assertEqual(indices[1], (357, 443))
        self.assertEqual(indices[2], (572, 649))
        self.assertEqual(indices[3], (520, 571))
        self.assertEqual(indices[4], (653, 662))  
        self.assertEqual(indices[5], (733, 784))  
        self.assertEqual(indices[6], (820, 846))  
        self.assertEqual(indices[7], (2622, 2666))  

        
class HowExtractionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        with open('tests/Sample NLP Text Blocks.txt', encoding='utf8') as f:
            text = f.read().split('\n\n')
            cls.block_1 = extract_how(text[0], create_doc(text[0]), [0, 7, 16, 17, 18])
            cls.block_2 = extract_how(text[1], create_doc(text[1]), [0])
            cls.block_3 = extract_how(text[2], create_doc(text[2]), [0, 8, 12, 15])
            cls.block_4 = extract_how(text[3], create_doc(text[3]), [0, 2, 4, 5, 7, 11, 13])


    def test_block_1_extracts(self):
        self.assertEqual(self.block_1[0][0],
        "managed my team's functional testing and troubleshooting activities of the upgraded EDMS software and all")
        self.assertEqual(self.block_1[1][0],
        'informed business group')
        self.assertEqual(self.block_1[2][0],
        'engaged business')
        self.assertEqual(self.block_1[3][0],
        'managed the deployment of the EDMS (RDIMS/  eDOCS) to two new client groups (150 users) , directing the work of my staff for all.')
        self.assertEqual(self.block_1[4][0],
        'engaging key personnel in the client')
        self.assertEqual(self.block_1[5][0],
        'facilitated the department - wide implementation of the EDRMS by managing the department - wide training efforts to all our offices')
        self.assertEqual(self.block_1[6][0],
        "managed the validation of Information Frameworks for OCOL's 17 business processes")
        self.assertEqual(self.block_1[7][0],
        'Managed the upgrade of the Library system')
        self.assertEqual(self.block_1[8][0],
        'Managed the implementation of e - copy software to facilitate ATIP processes.')
        self.assertEqual(self.block_1[9][0],
        'Lead the development, revamp and implementation of Library services (ex.)')

        
    def test_block_1_indices(self):
        indices = create_tuples_of_indices(self.block_1)
        self.assertEqual(indices[0], (230, 335))
        self.assertEqual(indices[1], (443, 466))
        self.assertEqual(indices[2], (920, 936))
        self.assertEqual(indices[3], (1069, 1195))
        self.assertEqual(indices[4], (1297, 1333))
        self.assertEqual(indices[5], (2559, 2686))
        self.assertEqual(indices[6], (2864, 2945))
        self.assertEqual(indices[7], (3170, 3211))
        self.assertEqual(indices[8], (3286, 3361))
        self.assertEqual(indices[9], (3364, 3437))


    def test_block_2_extracts(self):
        self.assertEqual(self.block_2[0][0],
        'was responsible for all')
        self.assertEqual(self.block_2[1][0],
        'have worked closely with the contracting team here at CNSC')
        

    def test_block_2_indices(self):
        indices = create_tuples_of_indices(self.block_2)
        self.assertEqual(indices[0], (101, 124))
        self.assertEqual(indices[1], (399, 457))


    def test_block_3_extracts(self):
        self.assertEqual(self.block_3[0][0],
        'report to the Director of IT (cs - 05) as being involved in 5 initiatives considered to be the')
        self.assertEqual(self.block_3[1][0],
        'presented a DECK to the DCA and EXCOM recommending and advising on the feasibilities of these initiatives/  Projects.')
        self.assertEqual(self.block_3[2][0],
        'presented my recommendations based on : Client requirements, Scope, Cost')
        self.assertEqual(self.block_3[3][0],
        'to provide a more agile and efficient service to our clients especially with IT technology and trends')
        self.assertEqual(self.block_3[4][0],
        'presented my recommendations/  presentation (including the criteria listed above) to implement this new platform. (.)')


    def test_block_3_indices(self):
        indices = create_tuples_of_indices(self.block_3)
        self.assertEqual(indices[0], (166, 258))
        self.assertEqual(indices[1], (537, 652))
        self.assertEqual(indices[2], (655, 726))
        self.assertEqual(indices[3], (936, 1037))   
        self.assertEqual(indices[4], (1955, 2070)) 


    def test_block_4_extracts(self):
        self.assertEqual(self.block_4[0][0],
        'listed below a broad range of experience in Human resource management such as planning, guiding, supervising, coordinating and')
        self.assertEqual(self.block_4[1][0],
        'acquired an extensive experience in leading a technical teams')
        self.assertEqual(self.block_4[2][0],
        'managed the work performed by the section through subordinate staff.')
        self.assertEqual(self.block_4[3][0],
        'provided technical guidance and direction to')
        self.assertEqual(self.block_4[4][0],
        'evaluated their performance and recommended training, provided counselling on career paths and')
        self.assertEqual(self.block_4[5][0],
        'analyzed human resource requirements to perform the work of the unit and made')
        self.assertEqual(self.block_4[6][0],
        'acquired knowledge working with various HR specialties in government such as')
        self.assertEqual(self.block_4[7][0],
        'completed the CBSA staffing sub - delegation in March 2012.')


    def test_block_4_indices(self):
        indices = create_tuples_of_indices(self.block_4)
        self.assertEqual(indices[0], (133, 259))
        self.assertEqual(indices[1], (868, 929))
        self.assertEqual(indices[2], (1736, 1804))
        self.assertEqual(indices[3], (1931, 1975))
        self.assertEqual(indices[4], (2007, 2101))  
        self.assertEqual(indices[5], (2142, 2219))  
        self.assertEqual(indices[6], (2338, 2414))  
        self.assertEqual(indices[7], (2624, 2681))  


#python manage.py test
