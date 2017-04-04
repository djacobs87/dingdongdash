from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.sites.admin import SiteAdmin

from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount, SocialApp, SocialToken
from organizations.admin import OrganizationUserAdmin, OrganizationOwnerAdmin
from organizations.models import Organization, OrganizationUser, OrganizationOwner
from schedule.models import CalendarRelation, Rule, Occurrence, Event
from schedule.admin import CalendarAdminOptions

from ..models import APILog, Button, ButtonAction, Phone


##
# Core Admin
##
class ButtonAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return ('serial_number', 'organization',)

        return super(ButtonAdmin, self).get_readonly_fields(request, obj)

    def get_queryset(self, request):
        if not request.user.is_superuser:
            organization_user = OrganizationUser.objects.filter(user=request.user)
            organizations = Organization.objects.filter(organization_users=organization_user)
            return Button.objects.filter(organization__in=organizations)

        return Button.objects.all()


admin.site.register(Button, ButtonAdmin)


class ButtonActionAdmin(admin.ModelAdmin):
    pass


admin.site.register(ButtonAction, ButtonActionAdmin)


class PhoneAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        if(request.user.is_superuser):
            return Phone.objects.all()
        return Phone.objects.filter(user=request.user)


admin.site.register(Phone, PhoneAdmin)


class APILogAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return APILog.objects.all()


admin.site.register(APILog, APILogAdmin)


##
# Removals and Modifications of Third Party Models
##

def get_default_permissions(self, request):
    return {
        'add': self.has_add_permission(request),
        'change': self.has_change_permission(request),
        'delete': self.has_delete_permission(request),
    }


# Function and Base class for all modified ModelAdmin
def get_model_perms_superuser(self, request):
    if not request.user.is_superuser:
        return {}

    return get_default_permissions(self, request)


def get_model_perms_organization_owner(self, request):
    if OrganizationOwner.objects.filter(organization_user__user=request.user).exists():
        return get_default_permissions(self, request)

    return {}


class DDDModelAdmin(admin.ModelAdmin):
    pass


DDDModelAdmin.get_model_perms = get_model_perms_superuser

CalendarAdminOptions.get_model_perms = get_model_perms_superuser
GroupAdmin.get_model_perms = get_model_perms_superuser
SiteAdmin.get_model_perms = get_model_perms_superuser


class EmailAddressInlineAdmin(admin.TabularInline):
    model = EmailAddress


UserAdmin.get_model_perms = get_model_perms_superuser
UserAdmin.inlines = [EmailAddressInlineAdmin]

admin.site.unregister(CalendarRelation)
admin.site.register(CalendarRelation, DDDModelAdmin)

admin.site.unregister(Event)
admin.site.register(Event, DDDModelAdmin)

admin.site.unregister(Rule)
admin.site.register(Rule, DDDModelAdmin)

admin.site.unregister(Occurrence)
admin.site.register(Occurrence, DDDModelAdmin)

admin.site.unregister(Organization)


class OrganizationAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return ('slug',)

        return super(OrganizationAdmin, self).get_readonly_fields(request, obj)

    def get_queryset(self, request):
        if(request.user.is_superuser):
            return Organization.objects.all()

        return Organization.objects.filter(owner__organization_user__user=request.user)


admin.site.register(Organization, OrganizationAdmin)

OrganizationAdmin.get_model_perms = get_model_perms_organization_owner
OrganizationUserAdmin.get_model_perms = get_model_perms_organization_owner
OrganizationOwnerAdmin.get_model_perms = get_model_perms_organization_owner


admin.site.unregister(SocialAccount)
admin.site.unregister(SocialApp)
admin.site.unregister(SocialToken)
admin.site.unregister(EmailAddress)