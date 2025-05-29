import os
import json
import requests
import openai
from telegram import Bot

# Configurations
API_EVENTS = "https://api.coingecko.com/api/v3/events"
STATE_FILE = "seen_airdrops.json"

# Telegram bot
BOT = Bot(token=os.getenv('TG_BOT_TOKEN'))
CHAT_ID = os.getenv('TG_CHAT_ID')

# OpenAI API
openai.api_key = os.getenv('OPENAI_API_KEY')

def analyze_airdrop(title, description, date, link):
    prompt = (
        f"Analyze the value of this upcoming crypto airdrop:\n"
        f"Title: {title}\n"
        f"Description: {description}\n"
        f"Date: {date}\n"
        f"Link: {link}\n"
        f"Provide a concise analysis including potential value, risks, and recommendation."
    )
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.7
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"Error analyzing: {e}"

# Load seen airdrops
if os.path.exists(STATE_FILE):
    with open(STATE_FILE, 'r') as f:
        seen = set(json.load(f))
else:
    seen = set()

# Fetch upcoming airdrops
resp = requests.get(API_EVENTS, params={'type': 'airdrop'})
data = resp.json().get('data', [])

new_ids = []
for ev in data:
    ev_id = ev.get('id')
    if ev_id not in seen:
        new_ids.append(ev_id)
        title = ev.get('title')
        description = ev.get('description', '')
        date = ev.get('start_date')
        link = ev.get('website') or ev.get('twitter_event_url') or ''
        analysis = analyze_airdrop(title, description, date, link)
        msg = (
            f"🚀 ایردراپ جدید:\n*{title}*\n"
            f"📅 شروع: {date}\n"
            f"🔗 {link}\n\n"
            f"🧠 تحلیل هوش مصنوعی:\n{analysis}"
        )
        BOT.send_message(chat_id=CHAT_ID, text=msg, parse_mode='Markdown')

# Update seen list
if new_ids:
    seen.update(new_ids)
    with open(STATE_FILE, 'w') as f:
        json.dump(list(seen), f)
