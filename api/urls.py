from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt
from .views import process_button, generate_action_xml_script, order_creation_webhook

urlpatterns = [
    url(r'^functions/process_button/', csrf_exempt(process_button)),
    url(r'^actions/(?P<action_id>[0-9]+)/script.xml', csrf_exempt(generate_action_xml_script)),

    # Shopify Webhooks
    url(r'^webhooks/order_creation', csrf_exempt(order_creation_webhook))
]
