from django.http import HttpResponse
from django.contrib.sites.shortcuts import get_current_site

from shopify_webhook.decorators import webhook

import core.functions as ddd
from core.models import APILog, ButtonAction


def process_button(request):
    if(request.method != "POST"):
        return HttpResponse("Method not allowed", status=400)

    spoof = request.POST.get('spoof', False)
    site = get_current_site(request)

    try:
        result = ddd.process_button(
            battery_voltage=request.POST.get('batteryVoltage'),
            serial_number=request.POST.get('serialNumber'),
            click_type=request.POST.get('clickType'),
            spoof=spoof
        )

        response = HttpResponse(result)
    except Exception as result:
        response = HttpResponse(result, status=400)

    APILog.log(request, response, site=site.name, result=result)
    return response


def generate_action_xml_script(request, action_id):
    try:
        action = ButtonAction.objects.get(id=action_id)
        xml = "<Response><Say>%s</Say></Response>" % action.message
        return HttpResponse(xml, content_type='text/xml')
    except Exception as result:
        return HttpResponse(result, status=400)

@webhook
def order_creation_webhook(request):
    print(request)
    pass