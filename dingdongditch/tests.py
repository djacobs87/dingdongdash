from django.test import TestCase
from dingdongditch.wsgi import application


class WSGITestCase(TestCase):
    def test_wsgi_application(self):
        self.assertEquals(application.request_class.__name__, 'WSGIRequest')
