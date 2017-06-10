from django.contrib.auth.models import Group

def notify_admins(func):
    def wrapper(request, *args, **kwargs):
         if request.user.groups.filter(name='RequiresPasswordChange').exists():
             request.user.groups.remove(Group.objects.get(name="RequiresPasswordChange"))
             return func(request, *args, **kwargs)

    return wrapper