from datetime import datetime, timedelta
import json
import locale
import re
import sys
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo

xml_path = sys.argv[1]
jsonl_path = sys.argv[2]

locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')  # for parsing date string

NOTTINGHAM = ZoneInfo('Europe/London')
BANGKOK = ZoneInfo('Asia/Bangkok')
BEIJING = ZoneInfo('Asia/Shanghai')

# placeholder: skip texts without date
SKIP_LIST = []

with open('lastpost') as f:
    last_post = int(f.read())

with open(xml_path) as f:
    s = f.read()

last_day_id = -4

with open(jsonl_path, 'w') as f:
    for item in reversed(ET.ElementTree(ET.fromstring(s)).getroot().findall('./channel/item')):
        text = item.find('description').text
        pub_date = item.find('pubDate').text

        # skip empty article
        if not text:
            continue

        # publish manually
        if any(map(text.startswith, SKIP_LIST)):
            continue

        # placeholder: fix bad texts

        # construct date object
        date_obj = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %z')

        if date_obj.utcoffset() == timedelta(seconds=0):
            date_val = NOTTINGHAM
        elif date_obj.utcoffset() == timedelta(seconds=3600):
            date_val = NOTTINGHAM
        elif date_obj.utcoffset() == timedelta(seconds=25200):
            date_val = BANGKOK
        elif date_obj.utcoffset() == timedelta(seconds=28800):
            date_val = BEIJING
        else:
            raise NotImplementedError(f'Unexpected timezone in date string: {pub_date}')

        # skip year1
        if date_obj < datetime(2022, 9, 9, tzinfo=date_obj.tzinfo):
            continue

        date_val = date_obj.astimezone(date_val).strftime('%Y-%m-%d %H:%M:%S %Z')
        # fix ICT timezone abbreviation
        if date_val.endswith('+07'):
            date_val = date_val[:-3] + 'ICT'

        # extract text
        try:
            gd = re.fullmatch(r'(?P<year>\d+).(?P<month>\d+).(?P<date>\d+)[， ]?手术[， ]?(Day ?(?P<day>-?\d+)|(?P<one_year>1 Year))[,，。 ](?P<content>[\s\S]+)', text).groupdict()
        except AttributeError:
            raise ValueError(f'Invalid text: {text}')

        year = gd['year']
        month = gd['month']
        date = gd['date']

        day = gd['day']
        one_year = gd['one_year']

        content = gd['content']

        if day:
            day_id = int(day)
        elif one_year:
            day_id = 365
        else:
            assert False, 'Never reach here'

        # validate day
        if day_id != last_day_id + 1:
            raise ValueError(f'Wrong day number: expected Day {last_day_id + 1}, but got Day {day_id}')

        payload = json.dumps(f'<b>Day {day_id}</b>\n{content}\n{date_val}', ensure_ascii=False)
        if day_id > last_post:
            print(payload, file=f)

        last_day_id = day_id

with open('lastpost', 'w') as f:
    print(last_day_id, file=f, end='')
