from __future__ import unicode_literals
from organizations.models import Organization

from django.db import models
from django.contrib.auth.models import User

BUTTON_ACTION_CHOICES = [
    ('message', 'Send SMS Message'),
    ('call', "Make Voice Call")
]


class Phone(models.Model):
    phone_number = models.CharField(max_length=15)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")

    def __unicode__(self):
        return '%s (%s)' % (self.phone_number, self.user)


class ButtonAction(models.Model):
    name = models.CharField(max_length=128)
    type = models.CharField(max_length=8, choices=BUTTON_ACTION_CHOICES, default='call')
    phone = models.ForeignKey(Phone, on_delete=models.DO_NOTHING, related_name="phone")
    message = models.TextField()

    def __unicode__(self):
        if self.name:
            return self.name

        return self.action


class Button(models.Model):
    SP = "SINGLE"
    DP = "DOUBLE"
    LP = "LONG"

    name = models.CharField(max_length=64)
    description = models.CharField(max_length=128)
    serial_number = models.CharField(max_length=16, unique=True)
    single_press_actions = models.ManyToManyField(ButtonAction,
                                                  related_name="single_press_actions")
    double_press_actions = models.ManyToManyField(ButtonAction,
                                                  related_name="double_press_actions")
    long_press_actions = models.ManyToManyField(ButtonAction,
                                                related_name="long_press_actions")
    organization = models.ForeignKey(Organization,
                                     on_delete=models.CASCADE,
                                     blank=True,
                                     null=True,
                                     related_name="organization")

    def __unicode__(self):
        if self.name:
            return self.name

        return self.serial_number
