import os
from twilio.rest import Client
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']


client = Client(account_sid, auth_token)

message = client.messages \
    .create(
         body='This is your perfume recommendation',
         from_='+1xxxxxxxxxx',
         media_url=['https://static.luckyscent.com/images/products/511056.jpg?width=400&404=product.png'],
         to='+1xxxxxxxxxx'
     )

print(message.sid)

