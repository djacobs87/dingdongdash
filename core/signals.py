from django.contrib.auth.models import Group


def user_creation(sender, instance, **kwargs):
    instance.is_staff = True
    core_user_group = Group.objects.get(name="CoreUser")
    instance.groups.add(core_user_group.id)
