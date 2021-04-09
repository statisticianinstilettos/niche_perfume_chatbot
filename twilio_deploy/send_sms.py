import os
from twilio.rest import Client
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']


client = Client(account_sid, auth_token)

message = client.messages \
                .create(
                     body="Claire is testing shit. Wow so fast Twilio! This was sent after properly setting environment variables. nice coding!",
                     from_='+1xxxxxxx',
                     to='++1xxxxxxx'
                 )

print(message.sid)

