import json
import os
import requests
from urllib.parse import urlencode, quote_plus

BOT_TOKEN = os.environ['BOT_TOKEN']
CHAT_ID = os.environ['CHAT_ID']

last_day = 394

def send(text):
    prefix = 'https://api.telegram.org/{BOT_TOKEN}/sendMessage?'
    payload = {
        'chat_id': int(CHAT_ID),
        'text': text,
        'parse_mode': 'html',
    }
    url = prefix + urlencode(payload, quote_via=quote_plus)
    r = requests.get(url)
    r.raise_for_status()


with open('data.jsonl') as f:
    lines = f.readlines()[last_day:]
    for line in lines:
        payload = json.loads(line)
        send(payload)
