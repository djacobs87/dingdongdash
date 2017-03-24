from django.conf.urls import url, include
from django.views.decorators.csrf import csrf_exempt
from views import process_button

urlpatterns = [
    url(r'^functions/process_button/', csrf_exempt(process_button))
]
