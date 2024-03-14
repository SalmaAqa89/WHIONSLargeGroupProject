from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, UnexpectedAlertPresentException
import time

class SpeechRecognitionTest(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        options = ChromeOptions()
        options.add_argument("--headless")  # Run headless Chrome; remove if you want to see the browser window
        cls.selenium = Chrome(options=options)  # Use 'options' instead of 'chrome_options'
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_speech_recognition(self):
        # Navigate to the sign-up page and fill out the form
        self.selenium.get(f'{self.live_server_url}/sign_up/')
        self.selenium.find_element(By.NAME, "first_name").send_keys('Jane')
        self.selenium.find_element(By.NAME, "last_name").send_keys('Doe')
        self.selenium.find_element(By.NAME, "username").send_keys('@janedoe')
        self.selenium.find_element(By.NAME, "email").send_keys('janedoe@example.org')
        self.selenium.find_element(By.NAME, "new_password").send_keys('Password123')
        self.selenium.find_element(By.NAME, "password_confirmation").send_keys('Password123', Keys.RETURN)

        
        self.selenium.get(f'{self.live_server_url}/create_entry/')

  
        toggle_button = WebDriverWait(self.selenium, 10).until(
                        EC.element_to_be_clickable((By.ID, "toggle-record-btn"))
                        )

        self.selenium.execute_script("arguments[0].scrollIntoView(true);", toggle_button)

        self.selenium.execute_script("arguments[0].click();", toggle_button)
        
        try:
            WebDriverWait(self.selenium, 3).until(EC.alert_is_present())
            alert = self.selenium.switch_to.alert
            alert.accept()  
            print("Alert dismissed")
        except TimeoutException:
            print("No alert appeared")

        
        time.sleep(1)

        
        toggle_button = self.selenium.find_element(By.ID, "toggle-record-btn")

       
        button_color = toggle_button.value_of_css_property('background-color')
        expected_colors = ["rgb(255, 0, 0)", "rgba(255, 0, 0, 1)"] 
        self.assertIn(button_color, expected_colors, f"Expected button to be one of {expected_colors}, got {button_color}")
