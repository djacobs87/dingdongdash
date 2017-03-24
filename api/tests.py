from django.test import Client, TestCase
from organizations.models import Organization, OrganizationOwner, OrganizationUser

from core.models import Button, Phone
from django.contrib.auth.models import User

class PrimaryUseTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        self.owner_user = User.objects.create_user(username='owner_user',
                                                   email='user1@test.com',
                                                   password='abc123!@#')
        self.owner_user.save()
        self.owner_phone = Phone(phone_number="+19783284466", user=self.owner_user)
        self.owner_phone.save()

        self.organization = Organization(name="Test Organization")
        self.organization.save()

        self.organization_owner_user = OrganizationUser(organization=self.organization,
                                                        user=self.owner_user)
        self.organization_owner_user.save()
        self.organization_owner = OrganizationOwner(organization=self.organization,
                                                    organization_user=self.organization_owner_user)
        self.organization_owner.save()

        self.button = Button(serial_number="fooofooodoggdogg", organization=self.organization)
        self.button.save()

    def tearDown(self):
        self.button.delete()

    def test_process_button_low_battery(self):
        response = self.client.post('/api/functions/process_button/', {
            'spoof': True,
            'batteryVoltage': [u'249mV'],
            'serialNumber': [u'fooofooodoggdogg'],
            'clickType': [u'SINGLE']
        })

        self.assertEquals(response.status_code, 207)

    def test_process_button_unknown(self):
        response = self.client.post('/api/functions/process_button/', {
            'spoof': True,
            'batteryVoltage': [u'1546mV'],
            'serialNumber': [u'1111222233334444'],
            'clickType': [u'SINGLE']
        })

        self.assertEquals(response.status_code, 400)

    def test_process_button_single(self):
        response = self.client.post('/api/functions/process_button/', {
            'spoof': True,
            'batteryVoltage': [u'1546mV'],
            'serialNumber': [u'fooofooodoggdogg'],
            'clickType': [u'SINGLE']
        })

        self.assertEquals(response.status_code, 200)

    def test_process_button_double(self):
        response = self.client.post('/api/functions/process_button/', {
            'spoof': True,
            'batteryVoltage': [u'1546mV'],
            'serialNumber': [u'fooofooodoggdogg'],
            'clickType': [u'DOUBLE']
        })

        self.assertEquals(response.status_code, 200)

    def test_process_button_long(self):
        response = self.client.post('/api/functions/process_button/', {
            'spoof': True,
            'batteryVoltage': [u'1546mV'],
            'serialNumber': [u'fooofooodoggdogg'],
            'clickType': [u'LONG']
        })

        self.assertEquals(response.status_code, 200)

    def test_non_post_request(self):
        response = self.client.get('/api/functions/process_button/', {})
        self.assertEquals(response.status_code, 400)
