import os
from twilio.rest import Client

account_sid = os.environ['TWILIO_SID_LIVE']
auth_token = os.environ['TWILIO_AUTH_LIVE']

client = Client(account_sid, auth_token)

call = client.calls.create(
        url='http://demo.twilio.com/docs/voice.xml',
        to='+19513851558',
        from_='+19493046193'
        )

print(call.sid)
