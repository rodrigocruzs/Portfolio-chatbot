from flask import Flask, request

from functions import user_reply
from twilio_api import send_message

qa = user_reply

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def home():
    return "OK", 200


@app.route("/twilio", methods=["POST"])
def twilio():
    print(request.form["Body"])
    query = request.form["Body"]
    sender_id = request.form["From"]
    print(sender_id, query)

    res = qa(user_input=query)  # Pass the query as the 'user_input' argument

    # res = qa(
    #    {
    #   'question': query,
    #  'chat_history': {}
    # }
    # )

    #print(res)

    send_message(sender_id, res)

    return "OK", 200
