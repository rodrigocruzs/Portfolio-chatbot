from flask import Flask, request

from Whatsapp.functions import user_reply
from Whatsapp.twilio_api import send_message

qa = user_reply()

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    return 'OK', 200

@app.route('/twilio', methods=['POST'])
def twilio():
    query = request.form['Body']
    sender_id = request.form['From']
    print(sender_id, query)
    # TODO
    # get the user
    # if not create
    # create chat_history from the previous conversations
    # quetion and answer
    res = qa(
        {
        'question': query,
        'chat_history': {}
        }
    )

    print(res)
    
    send_message(sender_id, res['answer'])

    return 'OK', 200