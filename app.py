from flask import Flask, request, jsonify
import requests
import os
import re
from groq import Groq

app = Flask(__name__)

# ENV - Secret
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "karthick123")
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)
BOT_NAME = "Karthick World"

def send_text(to, message):
    url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
    data = {"messaging_product": "whatsapp", "to": to, "text": {"body": message}}
    requests.post(url, headers=headers, json=data)

def send_image(to, image_url, caption=""):
    url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
    data = {"messaging_product": "whatsapp", "to": to, "type": "image", "image": {"link": image_url, "caption": caption}}
    requests.post(url, headers=headers, json=data)

def ask_groq(text):
    system = "You are Karthick World Bot. Owner is Karthick Sir from Parukkal. If user asks owner, creator, who made you, un owner yaar, say: My Owner is Karthick Sir from Parukkal. Reply in SAME language as user. Solve maths, answer any question."
    res = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": system}, {"role": "user", "content": text}],
        max_tokens=600
    )
    return res.choices[0].message.content

@app.route('/webhook', methods=['GET'])
def verify():
    if request.args.get('hub.verify_token') == VERIFY_TOKEN:
        return request.args.get('hub.challenge')
    return "fail", 403

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    try:
        value = data['entry'][0]['changes'][0]['value']
        if 'messages' not in value:
            return jsonify(ok=True), 200
        msg = value['messages'][0]
        from_num = msg['from']

        if msg['type'] == 'text':
            user_text = msg['text']['body']
            low = user_text.lower()

            # Hi Rule
            if re.match(r'^(hi|hii|hello|hai|வணக்கம்|vanakkam|hey|hlo)', low):
                send_text(from_num, "Hello, உங்களுக்கு என்ன உதவி வேண்டும்? 😊")
                return jsonify(ok=True), 200

            # Owner Rule
            if any(w in low for w in ["owner", "creator", "who made you", "ஓனர்", "உன்னை யார்"]):
                send_text(from_num, "My Owner is Karthick Sir from Parukkal 😎")
                return jsonify(ok=True), 200

            # Image Rule - Any Brand
            if any(w in low for w in ["image", "create", "generate", "brand", "logo", "poster", "design", "imagine"]):
                send_text(from_num, "Image create panren bro... 1 sec ⏳🎨")
                prompt = user_text
                img_url = f"https://image.pollinations.ai/prompt/{prompt}?width=1024&height=1024&model=flux&nologo=true"
                send_image(from_num, img_url, f"Done! {prompt} - Karthick World Bot")
                return jsonify(ok=True), 200

            # Maths + Any Question
            send_text(from_num, ask_groq(user_text))

        elif msg['type'] == 'image':
            send_text(from_num, "Photo pathuten bro! Analysing... 🔍")
            caption = msg['image'].get('caption', 'Explain this photo')
            send_text(from_num, ask_groq(f"User sent photo. Caption: {caption}. Explain photo. Reply same language."))

    except Exception as e:
        print(e)
    return jsonify(ok=True), 200

@app.route('/')
def home():
    return "Karthick World Bot Running!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
