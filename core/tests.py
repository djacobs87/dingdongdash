# from datetime import datetime, timedelta
# import pytz

from django.contrib.auth.models import User
from django.test import TestCase

from .functions import process_button
from .models import Button, ButtonAction, Phone


class FunctionalTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1',
                                              email='user1@test.com',
                                              password='abc123!@#')
        self.owner_phone = Phone.objects.create(phone_number="+19783284466", user=self.user1)
        self.button_action1 = ButtonAction.objects.create(name="Call User1",
                                                          phone=self.owner_phone)
        self.button_action2 = ButtonAction.objects.create(name="Text User1",
                                                          phone=self.owner_phone)
        self.button1 = Button.objects.create(serial_number="1111222233334444",
                                             single_press_action=self.button_action1,
                                             double_press_action=self.button_action2)
        self.battery_voltage = "1546mV"

    def tearDown(self):
        self.button_action1.delete()
        self.button_action2.delete()
        self.button1.delete()
        self.owner_phone.delete()
        self.user1.delete()

    def test_process_button_single(self):
        result = process_button(self.battery_voltage,
                                self.button1.serial_number,
                                Button.SP,
                                spoof=True)
        if not hasattr(result, 'message'):
            self.assertEqual(True, True)
            return
        self.fail()

    def test_process_button_double(self):
        result = process_button(self.battery_voltage,
                                self.button1.serial_number,
                                Button.DP,
                                spoof=True)
        if not hasattr(result, 'message'):
            self.assertEqual(True, True)
            return
        self.fail()

    def test_process_button_long(self):
        try:
            process_button(self.battery_voltage,
                           self.button1.serial_number,
                           Button.LP,
                           spoof=True)
            self.fail()
        except Exception:
            pass

    def test_process_number_no_number_found(self):
        try:
            process_button(None, "0000000000000000", Button.SP)
            self.fail()
        except Exception:
            pass

    def test_generate_to_number_throws_exception(self):
        try:
            process_button(None, None, Button.SP)
            self.fail()
        except Exception:
            pass
