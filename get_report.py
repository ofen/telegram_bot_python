'''
Генерирует
'''

import requests

import os
import re
import json
from urllib.parse import urlencode

# получаем список счетчиков для опроса
with open('device_list.txt', 'r') as file:
    device_list = file.read().splitlines()

# заголовки для запросов
headers = {
    'Host':'lk.vodokanal.spb.ru',
    'Connection':'keep-alive',
    'X-Requested-With':'XMLHttpRequest',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
}
# создаем клиент с поддержкой сессий
client = requests.Session()

# Авторизация
def auth():
    print('Авторизация')
    credentials = {
        'login': 'gks2kir@yandex.ru',
        'password': 'P2z$Ih0;b',
    }
    return client.post(
        url='https://lk.vodokanal.spb.ru/login',
        data=credentials
    )

# Получаем информацию по всем доступным счетчикам
def get_device_info():
    print('Сбор данных')
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

# перебираем список счетчиком
def get(current_date):
    print('Собираем отчет на %s' % current_date)
    auth()
    device_placecode = get_device_info()
    collected_data = []
    progress = 20
    for index, device in enumerate(device_list, start=1):
        if (index * 100 / len(device_list)) // progress == 1:
            print('Отчет завершен на %s%%' % progress)
            progress += 20
        # если похоже на номер то обрабатываем либо пропускаем
        if re.match(r'\d+\.\d+|\d+', device):
            placecode = device_placecode.get(device)
            # если нет placecode то нет устройства
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
                # получаем показания
                res = client.post(
                    url='https://lk.vodokanal.spb.ru/devices/getHourlyReadings/ajax',
                    headers=headers,
                    data=urlencode(payload)
                )
                result = res.json()
                # проверяем есть ли показания
                try:
                    value = result['data'][0]['value'].replace('.', ',')
                    collected_data.append(value)
                except IndexError:
                    collected_data.append('NO DATA')
        else:
            collected_data.append(device)
    print('Отчет готов')
    return collected_data