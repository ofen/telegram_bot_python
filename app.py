from telegram.ext import Updater, CommandHandler, run_async
import telegram

import time
import os
import io
import logging
import random

import get_report
import get_news

greet = ['Привет', 'Здрасте', 'Чего надо?', 'Что пожелаете?', 'Говори']

BOT_TOKEN = '601963469:AAHpcyQPdzO9mfWaCKMaKoNawIcOBBdTvro'

logging.basicConfig(
    format='[%(asctime)s][%(levelname)s] %(name)s - %(message)s',
    level=logging.DEBUG,
    datefmt='%d.%m.%Y %H:%M:%s'
)
logger = logging.getLogger(__name__)

updater = Updater(token=BOT_TOKEN)
dispatcher = updater.dispatcher

def get_datetime():
    return time.strftime('%d.%m.%Y %H:%M:%S')

def get_date():
    return time.strftime('%d.%m.%Y')

def date_validate(date):
    try:
        time.strptime(date, '%d.%m.%Y')
        return True
    except ValueError:
        return False

def on_start(bot, updater):
    return bot.send_message(updater.message.chat.id, random.choice(greet))

def on_test(bot, updater):
    return bot.send_message(updater.message.chat.id, 'Все системы в норме!')

@run_async
def on_getreport(bot, updater, args):
    try:
        date = args[0]
        if date_validate(date) == False:
            return bot.send_message(updater.message.chat.id, 'Некорректная дата')
    except IndexError:
        date = get_date()
    response = 'Собираем отчет на %s' % date
    bot.send_message(updater.message.chat.id, response)
    data = get_report.get(date)
    file = io.BytesIO('\n'.join(data).encode())
    file.name = 'Report_%s.txt' % date
    return bot.send_document(updater.message.chat.id, document=file)

@run_async
def on_getnews(bot, updater):
    news = get_news.get()
    if len(news) > 0:
        for i in news:
            bot.send_message(updater.message.chat.id, i)
            time.sleep(1)
    else:
        return bot.send_message(updater.message.chat.id, 'На сегодня новостей нет')

dispatcher.add_handler(CommandHandler('start', on_start))
dispatcher.add_handler(CommandHandler('test', on_test))
dispatcher.add_handler(CommandHandler('getreport', on_getreport, pass_args=True))
dispatcher.add_handler(CommandHandler('getnews', on_getnews))

updater.start_polling()