import os
import re
import json
from urllib.parse import urlencode
from app import logger

import requests

# Getting device list from file
with open('device_list.txt', 'r') as file:
    device_list = file.read().splitlines()

# Request headers
headers = {
    'Host':'lk.vodokanal.spb.ru',
    'Connection':'keep-alive',
    'X-Requested-With':'XMLHttpRequest',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
}
# Session client
client = requests.Session()

# Credentials
credentials = {
    'login': os.getenv('VODOKANAL_LOGIN'),
    'password': os.getenv('VODOKANAL_PASSWD'),
}

# Authorization
def auth():
    return client.post(
        url='https://lk.vodokanal.spb.ru/login',
        data=credentials
    )

# Getting info about devices
def get_device_info():
    payload = {
        'api_version': '2',
        'jsonData': json.dumps({
            'cntr_type_id': [],
            'cntr_obj_id': [],
            'cntr_dev_id': [],
            'dstart': '',
            'dstop': '',
        })
    }
    res = client.post(
        url='https://lk.vodokanal.spb.ru/devices/searchDevicesNemo/ajax',
        headers=headers,
        data=urlencode(payload)
    )
    device_info = res.json()
    device_placecode = {}
    for i in device_info.get('data'):
        device = i['device']
        placecode = i['placecode']
        device_placecode.update({device: placecode})
    return device_placecode

# Process data
def get(current_date):
    logger.info('Geeting report on %s' % current_date)
    auth()
    device_placecode = get_device_info()
    collected_data = []
    progress = 20
    for index, device in enumerate(device_list, start=1):
        if (index * 100 / len(device_list)) // progress == 1:
            logger.info('Report complete at %s%%' % progress)
            progress += 20
        # If device number is valid then process
        if re.match(r'\d+\.\d+|\d+', device):
            placecode = device_placecode.get(device)
            # If device number has no placecode then no such device
            if placecode is None:
                collected_data.append('NO DEVICE')
            else:
                payload = {
                    'api_version': '2',
                    'jsonData': json.dumps({
                        'placecode': placecode,
                        'dstart': current_date,
                        'dstop': current_date,
                    })
                }
                # Requesting data
                res = client.post(
                    url='https://lk.vodokanal.spb.ru/devices/getHourlyReadings/ajax',
                    headers=headers,
                    data=urlencode(payload)
                )
                result = res.json()
                # Checking data
                try:
                    value = result['data'][0]['value'].replace('.', ',')
                    collected_data.append(value)
                except IndexError:
                    collected_data.append('NO DATA')
        else:
            collected_data.append(device)
    logger.info('Report ready')
    return collected_data