import asyncio

from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

import logging

BOT_TOKEN = '601963469:AAHpcyQPdzO9mfWaCKMaKoNawIcOBBdTvro'

logging.basicConfig(
    format='[%(asctime)s][%(levelname)s] %(name)s - %(message)s',
    level=logging.DEBUG,
    datefmt='%d.%m.%Y %H:%M:%s'
)
logger = logging.getLogger(__name__)

bot = Bot(BOT_TOKEN, proxy=BOT_PROXY)
dp = Dispatcher(bot)

tasks = []

async def notify(msg, text, timer):
    while True:
        await asyncio.sleep(timer)
        await bot.send_message(msg.chat.id, text)

@dp.message_handler(commands=['start'])
async def on_start(msg):
    await bot.send_message(msg.chat.id, 'Hello')

@dp.message_handler(commands=['notify'])
async def on_notify(msg):
    input_data = msg.text.split()
    try:
        text = str(input_data[1])
        timer = int(input_data[2])
        task = asyncio.ensure_future(notify(msg, text, timer))
        tasks.append(task)
        await bot.send_message(msg.chat.id, 'Notifying with text "%s" every %s seconds' % (text, timer))
    except Exception as e:
        await bot.send_message(msg.chat.id, 'Usage: /notify "<text>" <time in seconds>')

@dp.message_handler(commands=['stop'])
async def on_stop(msg):
    try:
        logger.info(tasks)
        tasks.pop(0).cancel()
        await bot.send_message(msg.chat.id, 'All notifications stopped')
    except IndexError:
        await bot.send_message(msg.chat.id, 'There are no notifications')

@dp.message_handler(regexp=r'^/test (".+") (\d+)$')
async def on_test(msg):
    await bot.send_message(msg.chat.id, match)

if __name__ == '__main__':
    executor.start_polling(dp)
