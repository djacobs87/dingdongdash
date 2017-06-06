from __future__ import unicode_literals

from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'core'
    verbose_name = 'Managing Buttons and Actions'

    def ready(self):
        from .signals import user_creation
        from django.contrib.auth.models import User
        from django.db.models.signals import post_save

        post_save.connect(user_creation, User)
