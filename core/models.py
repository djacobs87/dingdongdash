from __future__ import unicode_literals
from organizations.models import Organization

from django.db import models
from django.contrib.auth.models import User

BUTTON_ACTION_CHOICES = [
    ('message', 'Send SMS Message'),
    ('call', "Make Voice Call")
]


class Phone(models.Model):
    phone_number = models.CharField(max_length=15, null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return '%s (%s)' % (self.phone_number, self.user)


class ButtonAction(models.Model):
    name = models.CharField(max_length=128, null=True)
    action = models.CharField(max_length=8, choices=BUTTON_ACTION_CHOICES, default='call')
    phone = models.ForeignKey(Phone, on_delete=models.DO_NOTHING, null=False)

    def __str__(self):
        if self.name:
            return self.name

        return self.action


class Button(models.Model):
    SP = "SINGLE"
    DP = "DOUBLE"
    LP = "LONG"

    name = models.CharField(max_length=64, null=True)
    description = models.CharField(max_length=128, null=True)
    serial_number = models.CharField(max_length=16, unique=True)
    single_press_action = models.ForeignKey(ButtonAction,
                                            on_delete=models.CASCADE,
                                            null=True,
                                            related_name="single_press_action")
    double_press_action = models.ForeignKey(ButtonAction,
                                            on_delete=models.CASCADE,
                                            null=True,
                                            related_name="double_press_action")
    long_press_action = models.ForeignKey(ButtonAction,
                                          on_delete=models.CASCADE,
                                          null=True,
                                          related_name="long_press_action")
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True)

    def __str__(self):
        if self.name:
            return self.name

        return self.serial_number
