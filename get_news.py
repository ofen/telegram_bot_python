import urllib.request
from xml.etree import ElementTree
import re

replace = {
    '&laquo;': '«',
    '&raquo;': '»',
    '&ndash;': '–',
    '&nbsp;': ' ',
    '&mdash;': '—',
    '&#769;': '',
    '&quot;': '"',
    '&#352;': '',
    '\n': '',
}

keywords = [
    '\bжкх\b',
    '\bжкс\b',
    '\bук\b',
    'жилком',
    'управляющия',
    'жилищн',
]

def keywords_filter(str):
    filter = re.compile('|'.join(keywords), flags=re.IGNORECASE)
    if re.search(filter, str):
        return True
    else:
        return False

def get_feed():
    rss = urllib.request.urlopen('https://www.fontanka.ru/fontanka.rss').read().decode('cp1251')
    for key, value in replace.items():
        rss = rss.replace(key, value)
    return rss

def get():
    data = list()
    rss = get_feed()
    parsed_data = ElementTree.fromstring(rss)
    for item in parsed_data[0].iter('item'):
        data.append({param.tag: param.text for param in item})

    return [item['link'] for item in data if keywords_filter(item['description'])]
