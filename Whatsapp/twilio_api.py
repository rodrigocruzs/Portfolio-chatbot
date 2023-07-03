from twilio.rest import Client
from flask import Flask, request, jsonify

import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

account_sid = os.environ["TWILIO_SID"]
auth_token = os.environ["TWILIO_TOKEN"]
client = Client(account_sid, auth_token)

def send_message(to: str, message: str) -> None:
    '''
    Send message to a Whatsapp user.
    Parameters:
        - to(str): sender whatsapp number in this whatsapp:+919558515995 form
        - message(str): text message to send
    Returns:
        - None
    '''
    try:
        _ = client.messages.create(
            from_=os.getenv('FROM'),
            body=message,
            to=to
        )
    except Exception as e:
        print(f"Error sending message: {e}")