from datetime import datetime, timedelta
import pytz

from django.contrib.auth.models import User
from django.test import TestCase

from organizations.models import Organization, OrganizationOwner, OrganizationUser
from schedule.models import Calendar, Event

from .functions import *
from .models import Button, Phone


class FunctionalTestCase(TestCase):
    def setUp(self):
        self.owner_user = User.objects.create_user(username='owner_user',
                                                   email='user1@test.com',
                                                   password='abc123!@#')
        self.owner_user.save()
        self.staff_user1 = User.objects.create_user(username='staff_user1',
                                                   email='user1@test.com',
                                                   password='abc123!@#')
        self.staff_user1.save()
        self.staff_user2 = User.objects.create_user(username='staff_user2',
                                                   email='user1@test.com',
                                                   password='abc123!@#')
        self.staff_user2.save()

        self.owner_phone = Phone(phone_number="+19783284466", user=self.owner_user)
        self.owner_phone.save()
        self.phone1 = Phone(phone_number="+19783284477", user=self.staff_user1)
        self.phone1.save()

        self.organization = Organization(name="Test Organization")
        self.organization.save()

        self.organization_owner_user = OrganizationUser(organization=self.organization,
                                                        user=self.owner_user)
        self.organization_owner_user.save()
        self.organization_owner = OrganizationOwner(organization=self.organization,
                                                    organization_user=self.organization_owner_user)
        self.organization_owner.save()
        self.organization_user1 = OrganizationUser(organization=self.organization,
                                                   user=self.staff_user1)
        self.organization_user1.save()
        self.organization_user2 = OrganizationUser(organization=self.organization,
                                                   user=self.staff_user2)
        self.organization_user2.save()

        self.button1 = Button(serial_number="G030JF053091HCMS", organization=self.organization)
        self.button1.save()
        self.button2 = Button(serial_number="G030JF05541734XN", organization=self.organization)
        self.button2.save()

        self.calendar = Calendar(name="Test Calendar", slug="test-calendar")
        self.calendar.save()

    def cleanUp(self):
        self.owner_user.delete()
        self.staff_user1.delete()
        self.staff_user2.delete()
        self.button1.delete()
        self.button2.delete()
        self.organization.delete()
        self.phone1.delete()
        self.owner_phone.delete()
        self.organization_owner.delete()
        self.organization_owner_user.delete()
        self.organization_user1.delete()
        self.organization_user2.delete()

    def test_generate_to_number_no_number_found(self):
        try:
            number = generate_to_number("1111222233334444", "+19783284499")
            self.fail()
        except Exception as e:
            pass

    def test_generate_to_number_user_one(self):
        an_hour_ago = datetime.now() - timedelta(hours = 1)
        an_hour_from_now = datetime.now() + timedelta(hours = 1)

        staff_event = Event(start=pytz.utc.localize(an_hour_ago),
                            end=pytz.utc.localize(an_hour_from_now),
                            creator=self.staff_user1)
        staff_event.save()

        number = generate_to_number("G030JF053091HCMS", "+19783284499")
        staff_event.delete()

        self.assertEqual(number, "+19783284477")

    def test_generate_to_number_user_two_fallback(self):
        try:
            an_hour_ago = datetime.now() - timedelta(hours = 1)
            an_hour_from_now = datetime.now() + timedelta(hours = 1)

            staff_event = Event(start=pytz.utc.localize(an_hour_ago),
                                end=pytz.utc.localize(an_hour_from_now),
                                creator=self.staff_user2)
            staff_event.save()

            number = generate_to_number("G030JF053091HCMS", "+19783284499")
            self.fail()
        except Exception as e:
            staff_event.delete()
            pass

    def test_generate_to_number_throws_exception(self):
        try:
            number = generate_to_number(None, "+19783284466")
            self.fail()
        except Exception as e:
            pass