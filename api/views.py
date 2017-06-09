from django.http import HttpResponse
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage

import random, string
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
    customer_email = body[u'email']
    customer_phone = body['billing_address'][u'phone']
    # Create User with default password
        # note for later: user should be forced to change password
    
    password = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
    user = User.objects.create_user(username=customer_email,
                                    email=customer_email,
                                    password=password)
    # Add to Group
    group = Group.objects.get(name='RequiresPasswordChange')
    user.groups.add(group)
    user.save()

    # Create Phone
    phone = Phone.objects.create(phone_number=customer_phone, user=user)

    # Create Button Action
    action = ButtonAction.objects.create(target_user = phone,
                                        name = "Text John Smith",
                                        type = "message")
    # Create New Button
    button = Button.objects.create(name = "UNASSIGNED")

    # Send Email with Login Info to users
    message = 'Hello, your username is '+customer_email+' and your temporary password is "'+password+'". The phone number that you have registered is '+customer_phone
    email = EmailMessage(message, to=[customer_email])
    email.send()

    print(message)
    return HttpResponse("CREATED", status=201)


@webhook
def order_creation_webhook(request):
    return order_creation(request)
