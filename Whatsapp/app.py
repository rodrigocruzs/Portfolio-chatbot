from flask import Flask, request

from functions import user_reply
from twilio_api import send_message
from threading import Thread

qa = user_reply

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def home():
    return "OK", 200


@app.route("/twilio-test", methods=["POST"])
def twilio_test():
    print(request.form["Body"])
    query = request.form["Body"]
    sender_id = request.form["From"]

    send_message(sender_id, f"you said: {query}")

    return "OK", 200


@app.route("/twilio", methods=["POST"])
def twilio():
    print(request.form["Body"])
    query = request.form["Body"]
    sender_id = request.form["From"]
    print(sender_id, query)

    def target(sender_id, query):
        res = qa(user_input=query)
        send_message(sender_id, res)

    thread = Thread(target=target, args=(sender_id, query))
    thread.start()

    return "OK", 200
