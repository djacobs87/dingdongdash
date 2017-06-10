from django.http import HttpResponse
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail

import json
import random
import string

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
    customer_phone = body[u'billing_address'][u'phone']
    password = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))

    quantity = 0
    for item in body[u'line_items']:
        quantity += item['quantity']

    try:
        user = User.objects.get(email=customer_email)
    except Exception:
        user = User.objects.create_user(username=customer_email,
                                        email=customer_email,
                                        password=password)
        group = Group.objects.get(name='RequiresPasswordChange')
        user.groups.add(group)
        user.save()

        message = """
Hello!

Welcome to Ding Dong Dash.

- Your username is {} and your temporary password is {}.
- The phone number that you have registered is {}.
""".format(customer_email, password, customer_phone)

        mail_result = send_mail(message=message,
                  subject="Welcome to Ding Dong Dash!",
                  from_email="service@dingdongdash.net",
                  recipient_list=[customer_email, "service@dingdongdash.net"])
        print(mail_result)

    # Create Phone
    try:
        phone = Phone.objects.get(phone_number=customer_phone, user=user)
    except Exception:
        phone = Phone.objects.create(phone_number=customer_phone, user=user)

    # Create Button Action
    try:
        action = ButtonAction.objects.create(target_user=phone,
                                             name="Text Myself",
                                             type="message")
    except Exception:
        action = ButtonAction.objects.create(target_user=phone,
                                             name="Text Myself",
                                             type="message")

    # Create New Button(s)
    for i in range(quantity):
        sn = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
        button = Button.objects.create(name="UNASSIGNED",
                              user=user,
                              serial_number="UNASSIGNED-"+sn)

        button.single_press_actions.add(action)
        button.double_press_actions.add(action)
        button.long_press_actions.add(action)


    return HttpResponse("CREATED", status=201)


@webhook
def order_creation_webhook(request):
    return order_creation(request)
