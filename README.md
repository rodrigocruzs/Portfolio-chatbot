# Investments Portfolio AI chatbot: chat with your investments

# Setup
0. install requirements in python env
```
python3 -m venv .portfolio; source .portfolio/bin/activate
pip3 install -r requirements.txt
```

1. Turn server on
```
flask --app Whatsapp/app run --debug --port=5009
```

2. Test it
```
curl --location 'localhost:5009/twilio' \
--form 'Body="{\"input\":\"what are the names (NOT the security_id) of the securities hold by the users\"}"' \
--form 'From="<phone number here>"'
```