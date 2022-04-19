import time, asyncio
import schedule
from api.main import get_markets
from bot import send_warning_chat
from dotenv import load_dotenv
from aiodata.main import get_current_text_by_name, get_current_text_by_name, get_all_current_backup_by_time_pretty
import InlineKeyboards

import telebot
import os
from dotenv import load_dotenv
from better_profanity import profanity
from telebot import types
from api.main import get_pretty_markets, get_markets
import asyncio

load_dotenv()
TOKEN_BOT = os.getenv('TOKEN_BOT')
CHAT_ID= -1001721723642

bot = telebot.TeleBot(token=TOKEN_BOT)

async def warning_chat():
    text = await get_current_text_by_name("warning")
    text = text[1]
    bot.send_message(CHAT_ID, text)

def warning():
    try:
        asyncio.run(warning_chat())
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            asyncio.run(warning_chat())

async def join_soc_chat():
    text = (await get_current_text_by_name("join_soc"))[1]
    all_current = await get_all_current_backup_by_time_pretty()
    print(text)
    print(all_current)
    markup = types.InlineKeyboardMarkup()
    for soc in all_current:
        markup.add(types.InlineKeyboardButton(soc[1], url = soc[3]))
    bot.send_message(CHAT_ID, text ,reply_markup=markup)

    #reply_markup = await InlineKeyboards.get_social_join_keyboard()

def join_soc():
    try:
        asyncio.run(join_soc_chat())
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            asyncio.run(join_soc_chat())

def printthree():
    print(3)

def tasks_loop():

    schedule.every(10).seconds.do(join_soc)
    schedule.every(12).seconds.do(warning)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    #bot.send_message(CHAT_ID, 'Hi! I\'m a Bot!')
    #asyncio.run(warning_chat())
    tasks_loop()