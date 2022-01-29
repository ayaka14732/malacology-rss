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
BEIJING = ZoneInfo('Asia/Shanghai')

# skip texts without date
SKIP_LIST = [
    '\u628a\u6027\u522b\u6539\u56de\u5973',
    '\u4f60\u5403\u996d\u4e0d\u8bf4\u5403\u4ec0\u4e48\uff0c\u4ed6\u4eec\u8bf4\u4f60\u5fc3\u601d\u96be\u731c\u3001\u96be\u4f3a\u5019',
    '\u592a\u53ef\u6015\u4e86\uff0c\u6628\u5929\U0001f1ec\U0001f1e7\u7814\u7a76\u751f\u7fa4\u52a0\u6211\u7684\u662f\u4e2a\u65f6\u95f4\u7ba1\u7406\u5927\u5e08',
    '\u611f\u89c9\u8de8\u6027\u522b\u5403\u6fc0\u7d20\uff0c\u5c31\u50cf\u4e00\u4e2a\u4e2a\u8d4c\u6ce8\uff0c\u4e5f\u4e0d\u77e5\u9053\u7ed3\u679c\u4f1a\u662f\u5982\u4f55',
    '\x54\u503c\u6709\u70b9\u9ad8',
    '\u60c5\u7eea\u771f\u7684\u597d\u5d29\u6e83\uff0c\u7a81\u7136\u89c9\u5f97\u81ea\u5df1\u5b8c\u5168\u662f\u72ec\u81ea\u4e00\u4e2a\u4eba',
    '\u6211\u6253\u75ab\u82d7\uff0c\u767b\u8bb0\u7684\u8ba9\u6211\u5230\u4e00\u53f7'
]

with open('lastpost') as f:
    last_post = int(f.read())

with open(xml_path) as f:
    s = f.read()

last_day_id = 0

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

        # fix bad texts
        text = text \
            .replace('2021.10.10.19', '2021.10.19') \
            .replace('Day3.31 Day114', '2021.3.31 Day114') \
            .replace('\nDay332被错误写成了312，差了20天。', '') \
            .replace('3ay188', 'Day188')

        # construct date object
        date_obj = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %z')

        if date_obj.utcoffset() == timedelta(seconds=0):
            date_val = NOTTINGHAM
        elif date_obj.utcoffset() == timedelta(seconds=3600):
            date_val = NOTTINGHAM
        elif date_obj.utcoffset() == timedelta(seconds=28800):
            date_val = BEIJING
        else:
            raise NotImplementedError(f'Unexpected timezone in date string: {pub_date}')

        date_val = date_obj.astimezone(date_val).strftime('%Y-%m-%d %H:%M:%S %Z')

        # extract text
        try:
            gd = re.fullmatch(r'(?P<year>\d+).(?P<month>\d+).(?P<date>\d+)[， ]?(Day ?(?P<day>\d+)|(?P<one_year>1 Year)|Year1 ?Day ?(?P<year1_day>\d+))[,，。 ](?P<content>[\s\S]+)', text).groupdict()
        except AttributeError:
            raise ValueError(f'Invalid text: {text}')

        year = gd['year']
        month = gd['month']
        date = gd['date']

        day = gd['day']
        one_year = gd['one_year']
        year1_day = gd['year1_day']

        content = gd['content']

        if day:
            day_id = int(day)
        elif one_year:
            day_id = 365
        elif year1_day:
            day_id = 365 + int(year1_day)
        else:
            assert False, 'Never reach here'

        # fix wrong day
        if 137 <= last_day_id <= 221 and day_id == last_day_id - 9:
            day_id = last_day_id + 1
        elif 222 <= last_day_id <= 330 and day_id == last_day_id - 10:
            day_id = last_day_id + 1
        elif 331 <= last_day_id and day_id == last_day_id - 19:
            day_id = last_day_id + 1

        # validate day
        if day_id != last_day_id + 1:
            raise ValueError(f'Wrong day number: expected Day {last_day_id + 1}, but got Day {day_id}')

        payload = json.dumps(f'<b>Day {day_id}</b>\n{content}\n{date_val}', ensure_ascii=False)
        if day_id > last_post:
            print(payload, file=f)

        last_day_id = day_id

with open('lastpost', 'w') as f:
    print(last_day_id, file=f, end='')
