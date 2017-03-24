from __future__ import unicode_literals
from organizations.models import Organization

from django.db import models
from django.contrib.auth.models import User

BUTTON_ACTION_CHOICES = [
    ('message', 'Send SMS Message'),
    ('call', "Make Voice Call")
]

class Button(models.Model):
    serial_number = models.CharField(max_length=16, unique=True)
    single_press_action = models.CharField(max_length=8, choices=BUTTON_ACTION_CHOICES, default='call')
    double_press_action = models.CharField(max_length=8, choices=BUTTON_ACTION_CHOICES, default='message')
    long_press_action = models.CharField(max_length=8, choices=BUTTON_ACTION_CHOICES, default='call')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.serial_number

class Phone(models.Model):
    phone_number = models.CharField(max_length=15, null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return '%s (%s)' % (self.phone_number, self.user)