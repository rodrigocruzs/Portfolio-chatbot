from twilio.rest import Client
from flask import Flask, request, jsonify

import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

account_sid = os.environ["TWILIO_SID"]
auth_token = os.environ["TWILIO_TOKEN"]
client = Client(account_sid, auth_token)

#def send_message(to: str, message: str): #-> None:

    # try:
    #     _ = client.messages.create(
    #         from_=os.getenv('FROM'),
    #         body=message,
    #         to=to
    #     )
    # except Exception as e:
    #     print(f"Error sending message: {e}")

    # print(message.sid)

def send_message(to: str, message: str):
    user_message = client.messages.create(
            from_=os.getenv('FROM'),
            body=message,
            to='whatsapp:+5511993133890'
            )
    print(user_message.sid)