import socket

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import override_settings, tag
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
from datetime import datetime
from screendoor.models import Position, Applicant, Requirement, ScreenDoorUser, FormAnswer, Note
from selenium.webdriver.common.action_chains import ActionChains
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import SimpleUploadedFile

# running this function gets the control flow to the positions view
def login(selenium, url, username, password):
    selenium.get(url)
    #delay = 2  # seconds
    #time.sleep(delay)    
    username_input = selenium.find_element_by_name("email")
    username_input.send_keys(username)
    password_input = selenium.find_element_by_name("password")
    password_input.send_keys(password)
    selenium.find_element_by_xpath('//input[@value="Login"]').click()


@override_settings(ALLOWED_HOSTS=['*'])  # Disable ALLOW_HOSTS
class BaseTestCase(StaticLiveServerTestCase):
    host = '0.0.0.0'  # Bind to 0.0.0.0 to allow external access

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Set host to externally accessible web server address
        cls.host = socket.gethostbyname(socket.gethostname())

        # Instantiate the remote WebDriver
        cls.selenium = webdriver.Remote(
            command_executor='http://selenium:4444/wd/hub',
            desired_capabilities=DesiredCapabilities.CHROME,
        )
        cls.selenium.implicitly_wait(5)

    def setUp(self):
        self.user = ScreenDoorUser.objects.create_user(
            username="good@canada.ca", email="good@canada.ca",
            password="password1",
            email_confirmed=True)
        self.unconfirmedUser = ScreenDoorUser.objects.create_user(
            username="unconfirmed@canada.ca", email="unconfirmed@canada.ca",
            password="password2",
            email_confirmed=False)
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
        self.user.save()
        self.testPosition.save()
        self.testPosition.position_users.add(self.user)

        self.pdf_file = SimpleUploadedFile(
            "tests/Sample Job Poster.pdf",
            b"file_content",
            content_type="application/pdf"
        )


    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    # Assert that the error message shows properly
    def test_faulty_login_attempt_shows_error(self):
        login(self.selenium, self.live_server_url, 
            'unconfirmed@canada.ca', 'password2')
        body_text = self.selenium.find_element_by_tag_name('body').text
        self.assertIn('Email address for user not confirmed.', body_text)


    # Assert that the login button leads to the /positions template
    def test_login_button(self):
        login(self.selenium, self.live_server_url, 
            'good@canada.ca', 'password1')
        body_text = self.selenium.find_element_by_tag_name('body').text
        self.assertIn('View Positions', body_text)


    # Assert that the create account button leads to the create account template
    def test_create_account_button(self):
        self.selenium.get(self.live_server_url)  
        self.selenium.find_element_by_id('register-button').click()
        body_text = self.selenium.find_element_by_tag_name('body').text
        self.assertIn('Create Account', body_text)


    # Assert that the logout button leads to the logged out template
    def test_logout_button(self):
        login(self.selenium, self.live_server_url, 
        'good@canada.ca', 'password1')  
        self.selenium.find_element_by_id('logout-button').click()
        body_text = self.selenium.find_element_by_tag_name('body').text
        self.assertIn('Login', body_text)


    # Assert that the create new position button leads to the create position template
    def test_intended_create_position_workflow(self):
        login(self.selenium, self.live_server_url, 
        'good@canada.ca', 'password1')  
        
        # Go to create position template and check if the submit button is hidden
        self.selenium.find_element_by_id('create-new-position-button').click()
        self.assertIn('hide', 
            self.selenium.find_element_by_id('position_submit_button').get_attribute("class"))

        # Click "pdf" button
        actions = ActionChains(self.selenium)
        actions.move_to_element(self.selenium.find_element_by_id('radio_pdf')).click().perform()

        # Validate that submit is visible
        self.assertNotIn('hide', 
            self.selenium.find_element_by_id('position_submit_button').get_attribute("class"))

        # Submit a pdf
        with open('tests/Sample Job Poster.pdf'.format("Sample Job Poster.pdf"), 'rb') as file:
            file_name = FileSystemStorage().save(file.name.replace(' ', ''), file)
            file_path = FileSystemStorage().url(file_name) 
            pdf_input = self.selenium.find_element_by_id('pdf_input')
            pdf_input.send_keys(file_path)
            submit_button = self.selenium.find_element_by_id('position_submit_button')
            submit_button.click()

            # Wait for the file to upload, then check if it worked
            time.sleep(3)
            self.assertIn('We think this is the position. Can you take a look and make sure it is correct?', 
                self.selenium.find_element_by_tag_name('body').text)
            self.assertIn('Senior Program Support', 
                self.selenium.find_element_by_class_name('edit').text)

            # Edit position's title
            self.selenium.find_element_by_id('edit-button').click()
            
            self.assertNotIn('Senior Program Support', 
                self.selenium.find_element_by_class_name('edit').text)

            self.selenium.find_elements_by_name('position-title')[2].send_keys("ing test")
            
            # Save edits and return to main page
            self.selenium.find_element_by_id('ok-button').click()
            self.selenium.find_element_by_id('save-button').click()
            self.assertIn('Senior Program Supporting test', 
                self.selenium.find_element_by_tag_name('body').text)
    
#p self.selenium.find_elements_by_name('position-title')[2].get_attribute("class")
#python manage.py test