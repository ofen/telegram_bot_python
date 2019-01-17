from telegram.ext import Updater, CommandHandler, MessageHandler, run_async
import telegram

import time
import os
import io
import logging
import random

import get_report
import get_news

# Logging
logging.basicConfig(
    format='[%(asctime)s][%(levelname)s] %(name)s - %(message)s',
    level=logging.DEBUG,
    datefmt='%d.%m.%Y-%H:%M:%s'
)
logger = logging.getLogger(__name__)
# Returns current date and time in format hh:mm:ss-dd.mm.yyyy
def get_datetime():
    return time.strftime('%d.%m.%Y-%H:%M:%S')
# Returns current date in format dd.mm.yyyy
def get_date():
    return time.strftime('%d.%m.%Y')
# Returns true if inpute date in format dd.mm.yyyy
def date_validate(date):
    try:
        time.strptime(date, '%d.%m.%Y')
        return True
    except ValueError:
        return False
# Greeting
def get_greeting():
    greet = [
        'Hello',
        'Hi',
        'What?',
        'Speak',
        'What you need?',
        'Good day to you',
        'How can i help you?',
    ]
    return random.choice(greet);

# State management
state = {}

def get_state(updater):
    return state.get(updater.message.chat.id)

def update_state(updater, user_state):
    state[updater.message.chat.id] = user_state
    return

# On /start
def on_start(bot, updater):
    on_text(bot, updater)
    return bot.send_message(updater.message.chat.id, get_greeting())

# On /me
def on_me(bot, updater):
    on_text(bot, updater)
    return bot.send_message(updater.message.chat.id, 'Your ID: %s' % updater.message.chat.id)

# On /test
def on_test(bot, updater):
    on_text(bot, updater)
    return bot.send_message(updater.message.chat.id, 'All systems green')

# On /getreport
@run_async
def on_getreport(bot, updater, args):
    state = get_state(updater)
    if state is 'report':
        return bot.send_message(updater.message.chat.id, 'In progress...')
    try:
        date = args[0]
        if date_validate(date) == False:
            return bot.send_message(updater.message.chat.id, 'Incorrect date')
    except IndexError:
        date = get_date()
    update_state(updater, 'report')
    response = 'Getting report on %s' % date
    bot.send_message(updater.message.chat.id, response)
    data = get_report.get(date)
    file = io.BytesIO('\n'.join(data).encode())
    file.name = 'Report_%s.txt' % date
    update_state(updater, None)
    return bot.send_document(updater.message.chat.id, document=file)

# On /getnews
@run_async
def on_getnews(bot, updater):
    news = get_news.get()
    if len(news) > 0:
        for link in news:
            bot.send_message(updater.message.chat.id, link)
            time.sleep(1)
    else:
        return bot.send_message(updater.message.chat.id, 'No news today')

if __name__ == '__main__':
    # Bot initialization
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    updater = Updater(token=BOT_TOKEN)
    dp = updater.dispatcher
    # Registering handlers
    dp.add_handler(CommandHandler('start', on_start))
    dp.add_handler(CommandHandler('me', on_me))
    dp.add_handler(CommandHandler('test', on_test))
    dp.add_handler(CommandHandler('getreport', on_getreport, pass_args=True))
    dp.add_handler(CommandHandler('getnews', on_getnews))
    # Start
    updater.start_polling()
    updater.idle()