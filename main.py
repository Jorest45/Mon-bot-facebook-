from flask import Flask, request
import requests
import os
from dotenv import load_dotenv
load_dotenv()
app = Flask(__name__)
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
def get_ai_response(message):
    url = "https://api.deepseek.com/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "Tu es un assistant intelligent, gentil et utile."},
            {"role": "user", "content": message}
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()["choices"][0]["message"]["content"]

def send_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v17.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    data = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    requests.post(url, json=data)

@app.route('/', methods=['GET'])
def verify():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Erreur de vérification", 403

@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()
    for entry in data.get("entry", []):
        for message_event in entry.get("messaging", []):
            if "message" in message_event:
                sender_id = message_event["sender"]["id"]
                user_message = message_event["message"]["text"]
                ai_reply = get_ai_response(user_message)
                send_message(sender_id, ai_reply)
    return "ok", 200

if __name__ == '__main__':
    app.run()
