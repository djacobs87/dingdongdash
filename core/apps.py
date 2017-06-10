from __future__ import unicode_literals

from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'core'
    verbose_name = 'Core'

    def ready(self):
        from django.contrib.auth.models import User
        from django.db.models.signals import post_save
        from .signals import user_creation

        post_save.connect(user_creation, User)
