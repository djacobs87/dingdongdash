from django.contrib.auth.models import User, Group
from django.test import TestCase

from .functions import process_button
from .models import Button, ButtonAction, Phone


class FunctionalTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1',
                                              email='user1@test.com',
                                              password='abc123!@#')
        self.phone = Phone.objects.create(phone_number="+19783284466", user=self.user1)
        self.button_action1 = ButtonAction.objects.create(name="Call User1",
                                                          recipient=self.user1)

        self.button1 = Button.objects.create(serial_number="1111222233334444", user=self.user1)
        self.button1.single_press_actions.add(self.button_action1)
        self.button1.double_press_actions.add(
            ButtonAction.objects.create(name="Text User1", recipient=self.user1))
        self.battery_voltage = "1546mV"

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


class UserCreationTestCase(TestCase):
    def test_create_user_core_user_and_staff(self):
        new_user = User.objects.create_user(email="test@test.com",
                                            username="test_user",
                                            password="xxxyyy123")

        self.assertEquals(new_user.is_staff, True)
        self.assertEquals(list(new_user.groups.all()),
                          list(Group.objects.filter(name="CoreUser")))

        new_user.delete()


class ModelRepresentationTestCase(TestCase):
    def test_button_unicode(self):
        new_user = User.objects.create_user(email="test@test.com",
                                            username="test_user",
                                            password="xxxyyy123")
        button = Button.objects.create(serial_number="1111222233334444", user=new_user)
        self.assertEqual(unicode(button), "1111222233334444")
        button.name = "Test Name"
        self.assertEqual(unicode(button), "Test Name")
        button.delete()

    def test_button_action_unicode(self):
        user = User.objects.create_user(username='user1',
                                        email='user1@test.com',
                                        password='abc123!@#')
        phone = Phone.objects.create(phone_number="+12223334444", user=user)
        button_action = ButtonAction.objects.create(type="call", recipient=user)
        self.assertEqual(unicode(button_action), "call")
        button_action.name = "Test Action"
        self.assertEqual(unicode(button_action), "Test Action")
        button_action.delete()
        phone.delete()
        user.delete()

    def test_phone_unicode(self):
        user = User.objects.create_user(username='user1',
                                        email='user1@test.com',
                                        password='abc123!@#')
        phone = Phone.objects.create(phone_number="+12223334444", user=user)
        self.assertEqual(unicode(phone), "+12223334444 (user1)")
