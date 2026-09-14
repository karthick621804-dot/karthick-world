import os
import requests
from flask import Flask, request

app = Flask(__name__)

GROQ_KEY = os.environ.get("GROQ_API_KEY")
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_ID = os.environ.get("PHONE_NUMBER_ID")

@app.route('/')
def home():
    return "KARTHICK WORLD BOT IS LIVE!"

@app.route('/webhook', methods=['GET'])
def verify():
    if request.args.get("hub.verify_token") == os.environ.get("VERIFY_TOKEN"):
        return request.args.get("hub.challenge")
    return "Verification failed"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    try:
        if data['object'] == 'whatsapp_business_account':
            for entry in data['entry']:
                for change in entry['changes']:
                    if 'messages' in change['value']:
                        msg = change['value']['messages'][0]['text']['body']
                        from_no = change['value']['messages'][0]['from']

                        # GROQ AI CALL - Direct API
                        ai_url = "https://api.groq.com/openai/v1/chat/completions"
                        headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
                        payload = {
                            "model": "llama3-8b-8192",
                            "messages": [{"role": "user", "content": msg}]
                        }
                        res = requests.post(ai_url, headers=headers, json=payload).json()
                        reply = res['choices'][0]['message']['content']

                        # Send WhatsApp Reply
                        wa_url = f"https://graph.facebook.com/v20.0/{PHONE_ID}/messages"
                        wa_headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
                        wa_payload = {"messaging_product": "whatsapp", "to": from_no, "text": {"body": reply}}
                        requests.post(wa_url, headers=wa_headers, json=wa_payload)
    except Exception as e:
        print(e)
    return "ok", 200

if __name__ == '__main__':
    app.run()
