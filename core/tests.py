# from datetime import datetime, timedelta
# import pytz

from django.contrib.auth.models import User
from django.test import TestCase

from .functions import process_button
from .models import Button, ButtonAction, Phone

from django.contrib.admin.sites import AdminSite
from .admin import ButtonAdmin, PhoneAdmin, DDDModelAdmin

from organizations.models import Organization, OrganizationUser


class FunctionalTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1',
                                              email='user1@test.com',
                                              password='abc123!@#')
        self.phone = Phone.objects.create(phone_number="+19783284466", user=self.user1)
        self.button_action1 = ButtonAction.objects.create(name="Call User1",
                                                          phone=self.phone)

        self.button1 = Button.objects.create(serial_number="1111222233334444")
        self.button1.single_press_actions.add(
            ButtonAction.objects.create(name="Call User1", phone=self.phone))
        self.button1.double_press_actions.add(
            ButtonAction.objects.create(name="Text User1", phone=self.phone))
        self.battery_voltage = "1546mV"

    def tearDown(self):
        self.button1.delete()
        self.phone.delete()
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


class MockRequest:
    pass


class MockSuperUser:
    is_superuser = True
    is_staff = True

    def has_perm(self, perm):
        return True


class MockNonSuperUser:
    is_superuser = False
    is_staff = True

    def has_perm(self, perm):
        return True

    def __int__(self):
        return self.id


class AdminTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1',
                                              email='user1@test.com',
                                              password='abc123!@#')
        self.organization = Organization.objects.create(name="My Org")
        self.org_user = OrganizationUser.objects.create(user=self.user1,
                                                        organization=self.organization)
        self.phone = Phone.objects.create(phone_number="+19783284466", user=self.user1)
        self.button1 = Button.objects.create(serial_number="1111222233334444",
                                             organization=self.organization)
        self.button1.single_press_actions.add(
            ButtonAction.objects.create(name="Call User1", phone=self.phone))
        self.button1.double_press_actions.add(
            ButtonAction.objects.create(name="Text User1", phone=self.phone))

        # Other People's Stuff
        self.user2 = User.objects.create_user(username='user2',
                                              email='user1@test.com',
                                              password='abc123!@#')
        self.not_my_phone = Phone.objects.create(phone_number="+12223334444", user=self.user2)
        self.not_my_organization = Organization.objects.create(name='Not My Org')
        self.someone_elses_button = Button.objects.create(serial_number="5555666677778888",
                                                          organization=self.not_my_organization)

        # Prep site and request stuff
        self.superuser_request = MockRequest()
        self.superuser_request.user = MockSuperUser()
        self.superuser_request.user.id = self.user1.id
        self.non_superuser_request = MockRequest()
        self.non_superuser_request.user = MockNonSuperUser()
        self.non_superuser_request.user.id = self.user1.id

        self.site = AdminSite()

    def test_button_readonly_fields(self):
        ba = ButtonAdmin(Button, self.site)
        self.assertEqual(ba.get_readonly_fields(self.superuser_request), ())
        self.assertEqual(ba.get_readonly_fields(self.non_superuser_request),
                         ('serial_number', 'organization'))

    def test_button_queryset(self):
        ba = ButtonAdmin(Button, self.site)
        self.assertEqual(list(ba.get_queryset(self.superuser_request)), list(Button.objects.all()))
        self.assertEqual(list(ba.get_queryset(self.non_superuser_request)),
                         list(Button.objects.filter(organization=self.organization)))

    def test_phone_queryset(self):
        pa = PhoneAdmin(Phone, self.site)
        self.assertEqual(list(pa.get_queryset(self.superuser_request)), list(Phone.objects.all()))
        self.assertEqual(list(pa.get_queryset(self.non_superuser_request)),
                         list(Phone.objects.filter(user=self.user1)))

    def test_get_model_perms(self):
        dddma = DDDModelAdmin(Button, self.site)
        self.assertEqual(dddma.get_model_perms(self.superuser_request), {
            'add': True,
            'change': True,
            'delete': True
        })
        self.assertEqual(dddma.get_model_perms(self.non_superuser_request), {})
