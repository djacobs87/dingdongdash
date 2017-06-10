from django.contrib.auth.models import User
from django.test import TestCase

from ..models import Button, ButtonAction, Phone

from django.contrib.admin.sites import AdminSite
from .admin import ButtonAdmin, PhoneAdmin, DDDModelAdmin, OrganizationAdmin, ButtonActionAdmin

from organizations.models import Organization, OrganizationUser, OrganizationOwner


class MockRequest:
    pass


class MockSuperUser:
    is_superuser = True
    is_staff = True

    def has_perm(self, perm):
        return True

    def __trunc__(self):
        return 1


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
                                             user=self.user1)

        self.button_action1 = ButtonAction.objects.create(name="Call User1",
                                                          recipient=self.user1)
        self.button1.single_press_actions.add(self.button_action1)
        self.button1.double_press_actions.add(
            ButtonAction.objects.create(name="Text User1", recipient=self.user1))

        # Other People's Stuff
        self.user2 = User.objects.create_user(username='user2',
                                              email='user1@test.com',
                                              password='abc123!@#')
        self.not_my_phone = Phone.objects.create(phone_number="+12223334444", user=self.user2)
        self.not_my_organization = Organization.objects.create(name='Not My Org')
        self.someone_elses_button = Button.objects.create(serial_number="5555666677778888",
                                                          user=self.user2)
        self.someone_elses_action = ButtonAction.objects.create(name="Not Mine",
                                                                type="call",
                                                                message="hi",
                                                                recipient=self.user2)

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
                         ('serial_number', 'user'))

    def test_button_queryset(self):
        non_superuser_request = MockRequest()
        non_superuser_request.user = self.user1

        ba = ButtonAdmin(Button, self.site)
        self.assertEqual(list(ba.get_queryset(self.superuser_request)), list(Button.objects.all()))

        users = User.objects.filter(organizations_organization__in=[self.organization])
        self.assertEqual(list(ba.get_queryset(non_superuser_request)),
                         list(Button.objects.filter(user__in=users)))

    def test_button_formfield_for_manytomany(self):
        non_superuser_request = MockRequest()
        non_superuser_request.user = self.user1

        ba = ButtonAdmin(Button, self.site)
        kwargs = {}
        single_press_dbfield = \
            self.button1.single_press_actions.instance._meta.get_field("single_press_actions")
        double_press_dbfield = \
            self.button1.single_press_actions.instance._meta.get_field("double_press_actions")
        long_press_dbfield = \
            self.button1.single_press_actions.instance._meta.get_field("long_press_actions")

        single_press_field = (ba.formfield_for_manytomany(single_press_dbfield,
                              non_superuser_request,
                              **kwargs))
        double_press_field = (ba.formfield_for_manytomany(double_press_dbfield,
                              non_superuser_request,
                              **kwargs))
        long_press_field = (ba.formfield_for_manytomany(long_press_dbfield,
                            non_superuser_request,
                            **kwargs))

        superuser_single_press_field = (ba.formfield_for_manytomany(single_press_dbfield,
                                        self.superuser_request,
                                        **kwargs))

        self.assertEqual(list(superuser_single_press_field.queryset),
                         list(ButtonAction.objects.all()))
        self.assertEqual(list(single_press_field.queryset).sort(),
                         list(ButtonAction.objects.filter(recipient=self.user1)).sort())
        self.assertEqual(list(double_press_field.queryset).sort(),
                         list(ButtonAction.objects.filter(recipient=self.user1)).sort())
        self.assertEqual(list(long_press_field.queryset).sort(),
                         list(ButtonAction.objects.filter(recipient=self.user1)).sort())

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

    def test_organization_hidden_and_readonly_fields(self):
        non_superuser_request = MockRequest()
        non_superuser_request.user = self.user1

        oa = OrganizationAdmin(Organization, self.site)
        self.assertEqual(oa.get_readonly_fields(self.superuser_request), ())
        self.assertEqual(oa.get_readonly_fields(non_superuser_request), ('slug',))

    def test_action_queryset(self):
        non_superuser_request = MockRequest()
        non_superuser_request.user = self.user1

        baa = ButtonActionAdmin(ButtonAction, self.site)
        self.assertEqual(list(baa.get_queryset(self.superuser_request)),
                         list(ButtonAction.objects.all()))
        self.assertEqual(list(baa.get_queryset(non_superuser_request)).sort(),
                         list(ButtonAction.objects.filter(recipient=self.user1)).sort())

    def test_button_action_formfield_for_foreignkey(self):
        non_superuser_request = MockRequest()
        non_superuser_request.user = self.user1

        baa = ButtonActionAdmin(ButtonAction, self.site)

        kwargs = {}
        recipient_dbfield = \
            self.button_action1._meta.get_field("recipient")
        recipient_field = baa.formfield_for_foreignkey(recipient_dbfield,
                                                       non_superuser_request,
                                                       **kwargs)

        superuser_recipient_field = baa.formfield_for_foreignkey(recipient_dbfield,
                                                                 self.superuser_request,
                                                                 **kwargs)

        self.assertEqual(list(superuser_recipient_field.queryset),
                         list(User.objects.all()))

        queryset_list = list(recipient_field.queryset)
        queryset_list.sort()
        target_list = [self.user1]
        target_list.sort()
        self.assertEqual(queryset_list, target_list)

    def test_phone_formfield_for_foreignkey(self):
        non_superuser_request = MockRequest()
        non_superuser_request.user = self.user1

        pa = PhoneAdmin(Phone, self.site)

        kwargs = {}
        user_dbfield = self.phone._meta.get_field("user")
        user_field = (pa.formfield_for_foreignkey(user_dbfield,
                      non_superuser_request,
                      **kwargs))

        superuser_user_field = (pa.formfield_for_foreignkey(user_dbfield,
                                self.superuser_request,
                                **kwargs))

        self.assertEqual(list(superuser_user_field.queryset),
                         list(User.objects.all()))

        queryset_list = list(user_field.queryset)
        queryset_list.sort()
        target_list = list(User.objects.filter(username="user1"))
        target_list.sort()
        self.assertEqual(queryset_list, target_list)
