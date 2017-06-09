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
    password = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))

    quantity = 0
    for item in body['line_items']:
        quantity += item['quantity']

    try:
        user = User.objects.get(email=customer_email)
    except Exception as e:
        user = User.objects.create_user(username=customer_email,
                                        email=customer_email,
                                        password=password)
        group = Group.objects.get(name='RequiresPasswordChange')
        user.groups.add(group)
        user.save()
        # Send Email with Login Info to users
        message = 'Hello, your username is '+customer_email+' and your temporary password is "'+password+'". The phone number that you have registered is '+customer_phone
        print(message)
        # email = EmailMessage(message, to=[customer_email])
        # email.send()

    # Create Phone
    phone = Phone.objects.create(phone_number=customer_phone, user=user)

    # Create Button Action
    action = ButtonAction.objects.create(target_user = phone,
                                        name = "Text John Smith",
                                        type = "message")

    # Create New Buttons
    for i in range(quantity):
        serial_number = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
        button = Button.objects.create(name="UNASSIGNED",
                                       user=user,
                                       serial_number="UNASSIGNED-"+serial_number)

    return HttpResponse("CREATED", status=201)


@webhook
def order_creation_webhook(request):
    return order_creation(request)
