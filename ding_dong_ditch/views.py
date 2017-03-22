from django.http import HttpResponse
from twilio.rest import TwilioRestClient
import boto3
import json
from boto3.dynamodb.conditions import Key, Attr

def make_call(request):
    print(request)
    account_sid = ""
    auth_token  = ""
    client = TwilioRestClient(account_sid, auth_token)

    # dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    # table = dynamodb.Table('buttonCallList')

    # Finds an item in our table with a serial number that matches the event serial number
    # response = table.query(
    #     KeyConditionExpression=Key('serialnum').eq(event['serialNumber']),
    #     ProjectionExpression='phonenum'		# This filters the query results to include only the phone number
    # )

    call = client.calls.create(url="",
        to="",
        from_="",
        method="GET")

    return HttpResponse("Call successful")