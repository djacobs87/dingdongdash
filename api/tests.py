import mock
import os

from django.db import transaction
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.test import Client, TestCase

from core.models import Button, ButtonAction, Phone
from .views import order_creation


class ProcessButtonTestCase(TestCase):
    def setUp(self):
        Site.objects.create(domain="testserver")

        self.client = Client()

        self.user1 = User.objects.create_user(username='User1',
                                              email='user1@test.com',
                                              password='abc123!@#')
        self.phone = Phone.objects.create(phone_number="+19783284466", user=self.user1)
        self.button = Button.objects.create(serial_number="fooofooodoggdogg")
        self.button.single_press_actions.add(
            ButtonAction.objects.create(type="call",
                                        name="Call User1",
                                        target_user=self.phone,
                                        message="Testing 123"))
        self.button.double_press_actions.add(
             ButtonAction.objects.create(type="message",
                                         name="Text User1",
                                         target_user=self.phone,
                                         message="Testing 123"))

    def tearDown(self):
        self.button.delete()

    def test_process_button_low_battery(self):
        response = self.client.post('/api/functions/process_button/', {
            'spoof': True,
            'batteryVoltage': [u'249mV'],
            'serialNumber': [u'fooofooodoggdogg'],
            'clickType': [u'SINGLE']
        })

        self.assertEquals(response.status_code, 200)

    def test_process_button_unknown(self):
        try:
            with transaction.atomic():
                self.client.post('/api/functions/process_button/', {
                    'spoof': True,
                    'batteryVoltage': [u'1546mV'],
                    'serialNumber': [u'1111222233334444'],
                    'clickType': [u'SINGLE']
                })
        except Exception:
            self.assertEquals(True, True)
            return

        self.fail()

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
        try:
            with transaction.atomic():
                self.client.post('/api/functions/process_button/', {
                    'spoof': True,
                    'batteryVoltage': [u'1546mV'],
                    'serialNumber': [u'fooofooodoggdogg'],
                    'clickType': [u'LONG']
                })
        except Exception:
            self.assertEquals(True, True)
            return

        self.fail()

    def test_non_post_request(self):
        response = self.client.get('/api/functions/process_button/', {})
        self.assertEquals(response.status_code, 400)


class GenerateXMLScriptTestCase(TestCase):
    def test_script_generation(self):
        user1 = User.objects.create_user(username='User1',
                                         email='user1@test.com',
                                         password='abc123!@#')
        phone = Phone.objects.create(phone_number="+19783284466", user=user1)
        button_action = ButtonAction.objects.create(message="this is a test", target_user=phone)
        response = self.client.get('/api/actions/%s/script.xml' % button_action.id)
        self.assertEquals(response.status_code, 200)

    def test_script_generation_error(self):
        response = self.client.get('/api/actions/99999/script.xml')
        self.assertEquals(response.status_code, 400)


class ShopifyWebhookTestCase(TestCase):
    def test_order_creation_webhook(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        mock_request = mock.Mock()

        mock_request.META = {
            'X_SHOPIFY_TEST': 'true',
            'X_SHOPIFY_TOPIC': 'orders/paid',
            'X_NEWRELIC_ID': 'VQQUUFNS',
            'X_FORWARDED_PROTO': 'https',
            'X_SHOPIFY_HMAC_SHA256': '/A4sSNHE4Mbh7liKS5mEr7tFfVsawfHVO9sGCXh7MYQ=',
            'X_SHOPIFY_ORDER_ID': '820982911946154508',
            'HOST': 'ding-dong-ditch-aphelionz.c9users.io',
            'ACCEPT': '*/*',
            'X_SHOPIFY_SHOP_DOMAIN': 'mrh-io.myshopify.com',
            'CONNECTION': 'keep-alive',
            'USER_AGENT': 'Ruby',
            'X_REGION': 'usw',
            'X_FORWARDED_PORT': '443',
            'X_FORWARDED_FOR': '23.227.37.107',
            'ACCEPT_ENCODING': 'gzip;q=1.0,deflate;q=0.6,identity;q=0.3'
        }

        with open(dir_path + '/fixtures/shopify_order_creation.json', 'rb') as f:
            mock_request.body = f.read()
            response = order_creation(mock_request)

            # Test to see appearance of new user
            # Test new user forced to change pass
            # Test to see appearance of new button
            # Test Email Sent

            self.assertEqual(response.status_code, 201)
