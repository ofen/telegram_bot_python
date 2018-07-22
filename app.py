import telebot
from telebot import apihelper
import time
import os

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)
# apihelper.proxy = {'https': 'socks5://127.0.0.1:9050'}

def logging(msg):
    for i in msg:
        if i.content_type == 'text':
            log_data = 'Message from %s %s: %s' % (i.from_user.first_name, i.from_user.last_name, i.text)
            print(log_data)

bot.set_update_listener(logging)

@bot.message_handler(regexp='^[Hh]ello$')
def hello(msg):
    reply_msg = 'Hello, %s!' % msg.from_user.first_name
    bot.send_message(msg.chat.id, reply_msg)

@bot.message_handler(regexp='^[Bb]ye$')
def bye(msg):
    reply_msg = 'Bye, %s!' % msg.from_user.first_name
    bot.send_message(msg.chat.id, reply_msg)

if __name__ == '__main__':
    print('Bot is active...')
    bot.infinity_polling(True)
