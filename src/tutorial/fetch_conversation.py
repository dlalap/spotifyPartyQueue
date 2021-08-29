import os
from twilio.rest import Client

account_sid = os.environ['TWILIO_SID_LIVE']
account_auth = os.environ['TWILIO_AUTH_LIVE']
client = Client(account_sid, account_auth)

conversation = client.conversations \
                      .conversations('CH5e5111155167449dba68997a799e4ed0') \
                      .fetch()

print(conversation.chat_service_sid)

