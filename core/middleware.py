# myproject/accounts/middleware.py

from django.http import HttpResponseRedirect

import re

class PasswordChangeMiddleware:
    def process_request(self, request):
        if request.user.is_authenticated() and \
            re.match(r'^/dashboard/?', request.path) and \
            not re.match(r'^/dashboard/password_change/?', request.path):

            if request.user.groups.filter(name='RequiresPasswordChange').exists():
                return HttpResponseRedirect('/dashboard/password_change/')