import json
import requests
from urllib.parse import urlencode, quote_plus

def load_config(path):
    with open(path) as f:
        config = json.load(f)
    bot_token = config['BOT_TOKEN']
    chat_id = config['CHAT_ID']
    return bot_token, chat_id


BOT_TOKEN, CHAT_ID = load_config('config.json')

def send(text):
    prefix = f'https://api.telegram.org/{BOT_TOKEN}/sendMessage?'
    payload = {
        'chat_id': int(CHAT_ID),
        'text': text,
        'parse_mode': 'html',
    }
    url = prefix + urlencode(payload, quote_via=quote_plus)
    r = requests.get(url)
    r.raise_for_status()


with open('data.jsonl') as f:
    lines = f.readlines()
    for line in lines:
        payload = json.loads(line)
        send(payload)
