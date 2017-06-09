from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.utils import timezone

from organizations.models import Organization


class Phone(models.Model):
    phone_number = models.CharField(max_length=15)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")

    def __unicode__(self):
        return '%s (%s)' % (self.phone_number, self.user)


BUTTON_ACTION_CHOICES = [
    ('message', 'Send SMS Message'),
    ('call', "Make Voice Call"),
    ('email', "Send Email")
]


class ButtonAction(models.Model):
    name = models.CharField(max_length=128)
    type = models.CharField(max_length=8, choices=BUTTON_ACTION_CHOICES, default='call')
    target_user = models.ForeignKey(Phone, on_delete=models.CASCADE, related_name="phone")
    message = models.TextField()

    class Meta:
        verbose_name = 'Action'
        verbose_name_plural = 'Actions'

    def __unicode__(self):
        if self.name:
            return self.name

        return self.type


class Button(models.Model):
    SP = "SINGLE"
    DP = "DOUBLE"
    LP = "LONG"

    name = models.CharField(max_length=64)
    description = models.CharField(max_length=128)
    serial_number = models.CharField(max_length=16, unique=True)
    user = models.ForeignKey(User,on_delete=models.DO_NOTHING, related_name="button_user")
    single_press_actions = models.ManyToManyField(ButtonAction,
                                                  related_name="single_press_actions")
    double_press_actions = models.ManyToManyField(ButtonAction,
                                                  related_name="double_press_actions")
    long_press_actions = models.ManyToManyField(ButtonAction,
                                                related_name="long_press_actions")

    def __unicode__(self):
        if self.name:
            return self.name

        return self.serial_number


class APILog(models.Model):
    datetime = models.DateTimeField()
    request = JSONField()
    response = JSONField()
    meta = JSONField()

    class Meta:
        verbose_name = 'API Log'
        verbose_name_plural = 'API Logs'

    def __unicode__(self):
        path = self.request.get('path', '')
        serial_number = self.request.get('POST', {}).get('serialNumber', '')
        return "%s %s %s" % (str(self.datetime), path, serial_number)

    @staticmethod
    def log(request, response, **kwargs):
        APILog.objects.create(datetime=timezone.now(),
                              request={
                                  "scheme": request.scheme,
                                  "POST": request.POST,
                                  "path": request.path
                              },
                              response={
                                  "status": response.status_code,
                                  "content": response.content
                              },
                              meta=kwargs)
