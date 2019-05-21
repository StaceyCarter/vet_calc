from twilio.rest import Client
import requests
import os

account_sid = os.environ.get('TWILIO_SID')
auth_token = os.environ.get('TWILIO_TOKEN')

client = Client(account_sid, auth_token)

def send_message(instructions, phone='+14153413561'):
    message = client.messages \
                    .create(
                         body=instructions,
                         from_='+16509426392',
                         to=phone
                     )

    print(message.sid)
