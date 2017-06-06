from django.http import HttpResponse
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage

import json

from shopify_webhook.decorators import webhook
from django.contrib.auth.models import User, Group


import core.functions as ddd
from core.models import APILog, ButtonAction, Button, Phone


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


def order_creation(request):

    body = json.loads(request.body)
    customerEmail = body[u'email']
    customerPhone = body[u'phone']
    # Create User with default password
        # note for later: user should be forced to change password
    user = User.objects.create_user(username=customerEmail,
                                    email=customerEmail,
                                    password='password')
    # Add to Group
    group = Group.objects.get(name='RequiresPasswordChange')
    user.groups.add(group)
    user.save()

    # Create Phone
    phone = Phone.objects.create(phone_number=[customerPhone], user=user)

    # Create Button Action
    action = ButtonAction.objects.create(target_user = phone,
                                        name = "Text John Smith",
                                        type = "message")

    # Create New Button
    button = Button.objects.create(name = "UNASSIGNED")

    # Send Email with Login Info to users
    email = EmailMessage('Hello, your username is "User" and your password is "password"', to=[customerEmail])
    email.send()

    return HttpResponse("NOT IMPLEMENTED", status=201)


@webhook
def order_creation_webhook(request):
    return order_creation(request)
