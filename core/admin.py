from django.contrib import admin
from .models import Button, Phone

class ButtonAdmin(admin.ModelAdmin):
    pass
admin.site.register(Button, ButtonAdmin)

class PhoneAdmin(admin.ModelAdmin):
    pass
admin.site.register(Phone, PhoneAdmin)