from django.contrib.auth.models import User
from django.test import TestCase

from ..models import Button, ButtonAction, Phone

from django.contrib.admin.sites import AdminSite
from .admin import ButtonAdmin, PhoneAdmin, DDDModelAdmin, OrganizationAdmin

from organizations.models import Organization, OrganizationUser, OrganizationOwner


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
        self.org_owner = OrganizationOwner.objects.create(organization=self.organization,
                                                          organization_user=self.org_user)
        self.phone = Phone.objects.create(phone_number="+19783284466", user=self.user1)
        self.button1 = Button.objects.create(serial_number="1111222233334444",
                                             organization=self.organization)
        self.button1.single_press_actions.add(
            ButtonAction.objects.create(name="Call User1", target_user=self.phone))
        self.button1.double_press_actions.add(
            ButtonAction.objects.create(name="Text User1", target_user=self.phone))

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
        self.site = AdminSite()

    def test_button_readonly_fields(self):
        non_superuser_request = MockRequest()
        non_superuser_request.user = self.user1

        ba = ButtonAdmin(Button, self.site)
        self.assertEqual(ba.get_readonly_fields(self.superuser_request), ())
        self.assertEqual(ba.get_readonly_fields(non_superuser_request),
                         ('serial_number', 'organization'))

    def test_button_queryset(self):
        non_superuser_request = MockRequest()
        non_superuser_request.user = self.user1

        ba = ButtonAdmin(Button, self.site)
        self.assertEqual(list(ba.get_queryset(self.superuser_request)), list(Button.objects.all()))
        self.assertEqual(list(ba.get_queryset(non_superuser_request)),
                         list(Button.objects.filter(organization=self.organization)))

    def test_phone_queryset(self):
        non_superuser_request = MockRequest()
        non_superuser_request.user = self.user1

        pa = PhoneAdmin(Phone, self.site)
        self.assertEqual(list(pa.get_queryset(self.superuser_request)), list(Phone.objects.all()))
        self.assertEqual(list(pa.get_queryset(non_superuser_request)),
                         list(Phone.objects.filter(user=self.user1)))

    def test_get_model_perms(self):
        non_superuser_request = MockRequest()
        non_superuser_request.user = self.user1

        dddma = DDDModelAdmin(Button, self.site)
        self.assertEqual(dddma.get_model_perms(self.superuser_request), {
            'add': True,
            'change': True,
            'delete': True
        })
        self.assertEqual(dddma.get_model_perms(non_superuser_request), {})

    def test_organization_queryset(self):
        non_superuser_request = MockRequest()
        non_superuser_request.user = self.user1

        oa = OrganizationAdmin(Organization, self.site)
        self.assertEqual(list(oa.get_queryset(self.superuser_request)),
                         list(Organization.objects.all()))
        self.assertEqual(list(oa.get_queryset(non_superuser_request)),
                         list(Organization.objects.filter(
                             owner__organization_user__user=self.user1)))
