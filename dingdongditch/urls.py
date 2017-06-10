from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth.views import password_change_done, \
    password_reset_done, password_reset_complete
from django.http import HttpResponseRedirect

from organizations.backends import invitation_backend
from core.decorators import notify_admins

urlpatterns = [
    url(r'^$', lambda r: HttpResponseRedirect('dashboard/')),
    url(r'^api/', include('api.urls')),
    url(r'^dashboard/password_change/done/$', remove_from_pw_change_group(password_change_done)),
    url(r'^dashboard/password_reset/done/$', remove_from_pw_change_group(password_reset_done)),
    url(r'^dashboard/reset/done/$', remove_from_pw_change_group(password_reset_complete)),
    url(r'^dashboard/', admin.site.urls, name="admin_view"),
    url(r'^schedule/', include('schedule.urls')),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^organizations/', include('organizations.urls')),
    url(r'^invitations/', include(invitation_backend().get_urls())),
    url(r'^hijack/', include('hijack.urls'))
]
