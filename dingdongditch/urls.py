from django.conf.urls import url, include
from django.contrib import admin
from organizations.backends import invitation_backend
from django.views.generic import RedirectView

urlpatterns = [
    url(r'^api/', include('api.urls')),
    url(r'^dashboard/', admin.site.urls, name="admin_view"),
    # url(r'^schedule/', include('schedule.urls')),
    # url(r'^accounts/', include('allauth.urls')),
    url(r'^organizations/', include('organizations.urls')),
    url(r'^invitations/', include(invitation_backend().get_urls()))
]
