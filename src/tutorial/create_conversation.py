import os
from twilio.rest import Client

account_sid = os.environ['TWILIO_SID_LIVE']
account_auth = os.environ['TWILIO_AUTH_LIVE']
client = Client(account_sid, account_auth)

conversation = client.conversations \
                     .conversations \
                     .create(friendly_name='My first conversation')
 
print(f'Conversation SID: {conversation.sid}')
