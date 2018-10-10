"""Tests for the website"""
from django.contrib.auth.models import User
from django.test import TestCase, Client    # pylint: disable=unused-import
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as ec
import json


class AssignmentTest(TestCase):
    """tests if crews are correctly assigned to flights"""
    fixtures = ['plane', 'captain', 'captain2', 'flight']

    def test_assignment(self):
        """tests if current flight captain is available (shouldn't)"""
        response = self.client.get('http://localhost:8000/api/get_crews/1')
        captains = json.loads(response.content.decode("utf-8"))

        self.assertEqual(response.status_code, 200)
        for capt in captains:
            self.assertNotEqual(capt['id'], 1)


class SeleniumTests(StaticLiveServerTestCase):
    """tests using selenium"""
    fixtures = ['plane', 'captain', 'captain2', 'flight']

    @classmethod
    def setUpClass(cls):
        """prepares test"""
        super().setUpClass()
        User.objects.create_user(username='user', password='user')
        cls.driver1 = WebDriver()
        cls.driver2 = WebDriver()
        cls.drivers = [cls.driver1, cls.driver2]
        # cls.driver1.implicitly_wait(10)
        # cls.driver2.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        """cleans up after test"""
        cls.driver1.quit()
        cls.driver2.quit()
        super().tearDownClass()

    def test(self):
        """test simultaneous usage"""
        for d in self.drivers:
            d.get(self.live_server_url)
            username_field = d.find_element_by_id('username')
            username_field.send_keys('user')
            password_field = d.find_element_by_id('password')
            password_field.send_keys('user')
            d.find_element_by_id('login').click()
            WebDriverWait(d, 10).until(
                ec.presence_of_element_located((By.ID, 'logout')))
            d.find_element_by_id('see-crews').click()
            WebDriverWait(d, 10).until(
                ec.presence_of_element_located((By.ID, 'date-field')))
            date_field = d.find_element_by_id('date-field')
            date_field.send_keys('2018-06-18')
            d.implicitly_wait(2)
            d.find_element_by_id('search-button').click()
            WebDriverWait(d, 10).until(
                ec.presence_of_element_located((By.CLASS_NAME, 'modify-button')))
            d.find_elements_by_class_name('modify-button')[0].click()
            WebDriverWait(d, 10).until(
                ec.presence_of_element_located((By.ID, 'button')))

        self.driver1.find_element_by_id('button').click()
        self.driver2.find_element_by_id('button').click()

        for d in self.drivers:
            WebDriverWait(d, 3).until(ec.alert_is_present())

        alert1 = self.driver1.switch_to.alert
        alert2 = self.driver2.switch_to.alert
        self.assertNotEqual(alert1, alert2)
