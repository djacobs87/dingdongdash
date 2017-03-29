from django.core.exceptions import ObjectDoesNotExist

from twilio.rest import TwilioRestClient

from dingdongditch import settings
from core.models import Button


def generate_params(button_action, spoof, **kwargs):
    params = {}

    params['type'] = button_action.type

    if(spoof):
        params['account_sid'] = kwargs.get('account_sid', settings.TWILIO_TEST_ACCOUNT_SID)
        params['auth_token'] = kwargs.get('auth_token', settings.TWILIO_TEST_AUTH_TOKEN)
        params['from_number'] = settings.TWILIO_MAGIC_NUMBER_AVAILABLE
    else:
        params['account_sid'] = kwargs.get('account_sid', settings.TWILIO_ACCOUNT_SID)
        params['auth_token'] = kwargs.get('auth_token', settings.TWILIO_AUTH_TOKEN)
        params['from_number'] = kwargs.get('from_number', settings.TWILIO_FROM_NUMBER)

    params['to_number'] = button_action.phone.phone_number

    return params


def process_button(battery_voltage, serial_number, click_type, spoof=False):
    try:
        button = Button.objects.get(serial_number=serial_number)
    except Button.DoesNotExist as e:
        raise ObjectDoesNotExist(e)

    request_queue = []
    result_ledger = []

    try:
        if(click_type == "SINGLE"):
            for button_action in button.single_press_actions.all():
                request_queue.append(generate_params(button_action, spoof))
        if(click_type == "DOUBLE"):
            for button_action in button.double_press_actions.all():
                request_queue.append(generate_params(button_action, spoof))
        if(click_type == "LONG"):
            for button_action in button.long_press_actions.all():
                request_queue.append(generate_params(button_action, spoof))

        if len(request_queue) == 0:
            raise Exception("No Action Taken")

        for request in request_queue:
            type = request.pop('type')

            if type == "call":
                result_ledger.append(create_call(settings.TWILIO_DEFAULT_XML_URL, **request))
            elif type == "message":
                result_ledger.append(send_message(settings.TWILIO_DEFAULT_TEXT_MESSAGE, **request))
            else:
                raise Exception("Unsupported action type")

        result = {}
        result['ledger'] = result_ledger
        if(int(battery_voltage[:-2]) < 250):
            result['rider'] = "Low Battery!"

        return result
    except Exception as e:
        raise Exception(e)


# https://www.twilio.com/docs/api/rest/call#instance-properties
def create_call(script_url, **kwargs):
    try:
        client = TwilioRestClient(kwargs['account_sid'], kwargs['auth_token'])
        call = client.calls.create(url=script_url,
                                   to=kwargs['to_number'],
                                   from_=kwargs['from_number'],
                                   method="GET")
    except Exception as e:
        print(e)
        raise Exception(e)

    return call


# https://www.twilio.com/docs/api/rest/message#instance-properties
def send_message(body, **kwargs):
    try:
        client = TwilioRestClient(kwargs['account_sid'], kwargs['auth_token'])
        message = client.messages.create(body=body,
                                         to=kwargs['to_number'],
                                         from_=kwargs['from_number'],
                                         method="GET")
    except Exception as e:
        print(e)
        raise Exception(e)

    return message


# def register_button(request):
#     import httplib
#     import urllib
#     import hashlib
#     import hmac
#     import base64
#     import boto3
#     import json
#     from boto3.dynamodb.conditions import Key, Attr

#     ERROR_INVALID_REQUEST = { "errorMessage": "Invalid request" }

#     # def validate_hmac(body, hmac_to_verify, shared_secret):
#     #     generated_hmac =
#           base64.b64encode(hmac.new(str(shared_secret), body, hashlib.sha256).digest())
#     #     return hmac_to_verify == generated_hmac

#     # def lambda_handler(event, context):
#     # dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
#     # table = dynamodb.Table('buttonCallList')
#     # shared_secret = "8c9cfecbf0fb64960bf0bd9b07edc87fa23492d119987a9834047d5db70be786"
#     body = json.loads(event.get('body'))

#     # Validation: the provided hmac is valid.
#     hmac_to_verify = event.get('headers').get('X-Shopify-Hmac-Sha256')

#     if(validate_hmac(event.get('body'), hmac_to_verify, shared_secret) != True):
#         return { "statusCode": 500, "headers": { }, "body": "Error" }

#     for item in body.get('line_items'):
#         if item.get('sku') == "1337":
#             for i in range(0, item.get('quantity')):
#                 response = table.put_item(
#                     Item={
#                         'serialnum': "none " + str(body.get('order_number')) + " " + str(i),
#                         'name': body.get('customer').get('default_address').get('name'),
#                         'email': body.get('customer').get('email'),
#                         'phonenum':
#                           "+1" + body.get('customer').get('default_address').get('phone'),
#                         'ordernum': body.get('order_number')
#                     }
#                 )
#         break

#     return { "statusCode": 200, "headers": { }, "body": "Success" }

# dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    # table = dynamodb.Table('buttonCallList')

    # Finds an item in our table with a serial number that matches the event serial number
    # response = table.query(
    #     KeyConditionExpression=Key('serialnum').eq(event['serialNumber']),
    #     ProjectionExpression='phonenum'
    # This filters the query results to include only the phone number
    # )
