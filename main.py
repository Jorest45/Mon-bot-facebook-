from flask import Flask, request
import requests
import os
import logging
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor

# Charger les variables d'environnement
load_dotenv()

app = Flask(__name__)

# Config logs
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Variables environnement
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# ThreadPool pour traiter plusieurs messages en même temps
executor = ThreadPoolExecutor(max_workers=10)

# --------- Fonction : Appel API DeepSeek ---------
def get_ai_response(message):
    url = "https://api.deepseek.com/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "Tu es un assistant Messenger intelligent et utile."},
            {"role": "user", "content": message}
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=15)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.Timeout:
        return "Le serveur met trop de temps à répondre. Réessaie plus tard."
    except requests.exceptions.RequestException as e:
        logging.error(f"Erreur DeepSeek: {e}")
        return "Je rencontre un problème technique, réessaie plus tard."

# --------- Fonction : Envoi message sur Facebook ---------
def send_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v17.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    data = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    try:
        resp = requests.post(url, json=data, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        logging.error(f"Erreur envoi message Facebook: {e}")

# --------- Traitement d'un message reçu ---------
def process_message(sender_id, user_message):
    reply = get_ai_response(user_message)
    send_message(sender_id, reply)

# --------- Route : Vérification du webhook ---------
@app.route('/', methods=['GET'])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        logging.info("Webhook vérifié avec succès ✅")
        return challenge
    logging.warning("Échec de vérification du webhook ❌")
    return "Erreur de vérification", 403

# --------- Route : Réception des messages ---------
@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()

    if not data:
        return "Aucune donnée reçue", 400

    for entry in data.get("entry", []):
        for message_event in entry.get("messaging", []):
            if "message" in message_event:
                sender_id = message_event["sender"]["id"]
                user_message = message_event["message"].get("text")

                if user_message:
                    executor.submit(process_message, sender_id, user_message)

    return "ok", 200

# --------- Lancement local ---------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
