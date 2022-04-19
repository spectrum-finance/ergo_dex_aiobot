import logging, os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.exceptions import BotBlocked
from dotenv import load_dotenv
import asyncio
from contextlib import suppress
import InlineKeyboards
from aiodata.main import *
from tabulate import tabulate

import pandas as pd
import requests
import datetime, time

import time, asyncio, datetime
import asyncio
import aioschedule

import telebot


from aiogram import types, utils
from aiogram.utils.exceptions import (MessageToEditNotFound, MessageCantBeEdited, MessageCantBeDeleted,
                                      MessageToDeleteNotFound)

from aiogram.dispatcher.webhook import AnswerCallbackQuery, AnswerInlineQuery, SendMessage
from aiogram.contrib.middlewares.logging import LoggingMiddleware


load_dotenv()
TOKEN_BOT = os.getenv('TOKEN_BOT')
CHAT_ID= -1001721723642

#logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

# Объект бота
bot_sync = telebot.TeleBot(token=TOKEN_BOT)
bot = Bot(token=TOKEN_BOT)
# Диспетчер для бота
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

@dp.errors_handler(exception=BotBlocked)
async def error_bot_blocked(update: types.Update, exception: BotBlocked):
    # Update: объект события от Telegram. Exception: объект исключения
    # Здесь можно как-то обработать блокировку, например, удалить пользователя из БД
    logging.info(f"Меня заблокировал пользователь!\nСообщение: {update}\nОшибка: {exception}")
    print(f"Меня заблокировал пользователь!\nСообщение: {update}\nОшибка: {exception}")

    # Такой хэндлер должен всегда возвращать True,
    # если дальнейшая обработка не требуется.
    return True

# Хэндлер на команду /test1
@dp.message_handler(commands="test1")
async def cmd_test1(message: types.Message):
    if message.chat.type == 'private':
        await message.reply("Test 1 private")
    elif message.chat.type == 'supergroup':
        msg  = await message.reply("Это сообщение должно отредактироваться через 5 сек")
        #msg = edit_msg(msg)
        try:
            asyncio.create_task(edit_msg(msg, "Это отредактированное сообщение удалиться через 5 сек", 5))
            asyncio.create_task(delete_message(msg, 10))
        except RuntimeError as ex:
            if "There is no current event loop in thread" in str(ex):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                asyncio.create_task(edit_msg(msg, "Это отредактированное сообщение удалиться через 5 сек", 5))
                asyncio.create_task(delete_message(msg, 10))

        await bot.answer_callback_query()
    else:
        await message.reply("Test ")

@dp.message_handler(commands="test2")
async def cmd_test2(message: types.Message):
    if message.chat.type == 'private':
        await message.reply("Test 2 private")

    elif message.chat.type == 'supergroup':
        await message.reply("Test 2 group")

@dp.message_handler(commands="admin")
async def cmd_test2(message: types.Message):
    if message.chat.type == 'private':
        if await is_admin(message.chat.id) == 1:
            await message.reply("Привет админ")
            socials = await get_all_soc()
            await message.answer('Редактирование панели социальных сетей:', reply_markup=await InlineKeyboards.get_social_admin_keyboard())

        else:
            print(message.chat.id)
            await message.reply("Ты не админ")

    elif message.chat.type == 'supergroup':
        await message.reply("This command allow just in private")



@dp.message_handler(commands="social")
async def cmd_test2(message: types.Message):
    if message.chat.type == 'private':
        await message.reply("private social command")

    elif message.chat.type == 'supergroup':
        if message.chat.id == CHAT_ID:
            await message.answer((await get_current_text_by_name("join_soc"))[1], reply_markup=await InlineKeyboards.get_social_join_keyboard())

@dp.message_handler(commands="warning")
async def cmd_test2(message: types.Message):
    if message.chat.type == 'private':
        await message.reply("private warning command")

    elif message.chat.type == 'supergroup':
        if message.chat.id == CHAT_ID:
            await message.answer((await get_current_text_by_name("warning"))[1])

async def send_warning_chat():
    bot.send_message(CHAT_ID, (await get_current_text_by_name("warning"))[1])



@dp.callback_query_handler()
async def navigate(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    if callback_query.data == 'Hello':
        print(user_id)
        return AnswerCallbackQuery(
            callback_query.id,
            text=f'Hi ! {user_id}',
            show_alert=False
        )
    elif "edit_soc" in callback_query.data and await is_admin(user_id):
        
        name_soc = callback_query.data.split(" ")[1]
        mess = name_soc+"\n\n"
        info_soc = await get_soc_info_by_name(name_soc)
        print(info_soc)
        column_names = ['id', 'id_social', 'invite_text', 'url', 'img', 'time_edit']
        empty = []
        if info_soc is None:
            Message = await bot.send_message(user_id,"Данные социальной сети не заполнены")

            mess = (f"{name_soc} add_atr url [ссылка] (добавить ссылку в соцсеть)" +
                    f"{name_soc} add_atr invite_text [текст] (текст приглашения)"+
                    f"{name_soc} add_atr img (после этой команды пришлите изображение)\n"
                    )
            Message = await bot.send_message(user_id,mess)
        else:
            for i in range(0, len(info_soc)):
                #print(info_soc[i]) 
                if info_soc[i] == None:
                    empty.append(column_names[i]) 
            if len(empty) >0:
                mess+=f"В базе нет следующий полей <{name_soc}>:\n "
                list_commands = []
                for em in empty:
                    if em == "url":
                        list_commands.append(f"{name_soc} add_atr "+em+"\t[ссылка] (добавить ссылку в соцсеть)")
                    elif em == "invite_text":
                        list_commands.append(f"{name_soc} add_atr "+em+"\t[текст] (текст приглашения)")
                    elif em == "img":
                        list_commands.append(f"{name_soc} add_atr "+em+"\t (после этой команды пришлите изображение)\n")
                    else:
                        list_commands.append(f"{name_soc} add_atr "+em+f"\t (добавить атрибут {em} )")
                    mess+= "  ["+em + "]  "
                mess+="\n\n"
                for z in list_commands:
                    mess+=z+"\n"
            Message = await bot.send_message(user_id,mess)
        
        

        return AnswerCallbackQuery(
            callback_query.id,
            text=f'{name_soc}',
            show_alert=False
        )




    return AnswerCallbackQuery(callback_query.id)


@dp.message_handler()
async def send_message(msg: types.Message):
    chat_type =  msg["chat"]["type"]
    user_id = msg.from_user.id
    if chat_type == "private":
        if "add_atr" in msg.text and await is_admin(user_id):
            query = msg.text.split(" ")
            #print(query)
            if len(query)<4:
                Message = await bot.send_message(user_id, "Не верный запрос")
            name_soc = query[0]
            if query[2] == "img":
                pass
            if query[2] == "url":
                try:
                    await edit_backup_soc_by_atr(name_soc=name_soc,atr="url", value=query[3])
                except TypeError:
                    await add_first_backup_soc_by_name_soc(name_soc=name_soc)
                    await edit_backup_soc_by_atr(name_soc=name_soc,atr="url", value=query[3])
                await bot.send_message(msg.chat.id, f'DONE, current state of {name_soc} :\n\t'+ str(await get_current_backup_by_time(name_soc)))
                pass
    elif chat_type == "supergroup":
        chat_id =  msg["chat"]["id"]
        if int(chat_id) == CHAT_ID:
            await count_mess_user(user_id)
            print("Подсчитать")
        print("NON COMMAND MSG supergroup: ", msg)

    #await bot.send_message(msg.chat.id, 'hi there')



async def delete_message(message: types.Message, sleep_time: int = 0):
    try:
        await asyncio.sleep(sleep_time)
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            await asyncio.sleep(sleep_time)

    with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
        await message.delete()

async def edit_msg(message: types.Message, text, sleep_time: int = 0 ):
    try:
        await asyncio.sleep(sleep_time)
        await message.edit_text(text)
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            await asyncio.sleep(sleep_time)
            await message.edit_text(text)




def start_bot():
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)


def get_markets1():
    Ago24DateTime = datetime.datetime.now() - datetime.timedelta(hours = 24)
    res = requests.get("https://api.ergodex.io/v1/amm/platform/stats?from={0}".format(int(time.mktime(Ago24DateTime.timetuple()) * 1000))).json()
    return res

def get_markets2():
    Ago24DateTime = datetime.datetime.now() - datetime.timedelta(hours = 24)
    Ago48DateTime = Ago24DateTime - datetime.timedelta(hours = 24)
    res = requests.get("https://api.ergodex.io/v1/amm/platform/stats?from={0}&to={1}".format(int(time.mktime(Ago48DateTime.timetuple()) * 1000), 
                                                                                             int(time.mktime(Ago24DateTime.timetuple()) * 1000))).json()
    return res

async def warning_chat():
    text = await get_current_text_by_name("warning")
    text = text[1]
    bot_sync.send_message(CHAT_ID, text)

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
    markup = telebot.types.InlineKeyboardMarkup()
    for soc in all_current:
        markup.add(telebot.types.InlineKeyboardButton(soc[1], url = soc[3]))
    bot_sync.send_message(CHAT_ID, text ,reply_markup=markup)

    #reply_markup = await InlineKeyboards.get_social_join_keyboard()

def join_soc():
    try:
        asyncio.run(join_soc_chat())
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            asyncio.run(join_soc_chat())





async def warning():
    await warning_chat()

async def join():
    await join_soc_chat()

async def most_active_user():
    user = await get_most_active_user()
    user_id = user[1]
    user_mess_count = user[3]
    mess = " Самый активный пользователь в чате: \n    ID: "+str(user_id) +"\n Кол-во сообщений: "+str(user_mess_count)
    bot_sync.send_message(CHAT_ID, mess )

async def metrics_chat():
    df1 = pd.json_normalize(get_markets2())
    TV48 = df1['volume.value'][0] / 10**df1['volume.units.currency.decimals'][0]
    df2 = pd.json_normalize(get_markets1())
    TVL24 = df1['tvl.value'][0] / 10**df1['tvl.units.currency.decimals'][0]
    TV24 = df2['volume.value'][0] / 10**df2['volume.units.currency.decimals'][0]
    data = [[str(TVL24) + ' $', str(TV24) + ' $', '+ ' + str(TV24 / TV48 * 100) + ' $' if TV24 / TV48 > 1 else '- ' + str(round((1 - TV24 / TV48) * 100, 2)) + ' %']]
    df_review = pd.DataFrame(data, columns = ['TVL', 'Total Volume', 'Total Volume %']) 
    #print(df_review)
    mess = tabulate(str(df_review), headers='keys', tablefmt='psql') 
    mess ="""
TVL: {0}

Total Volume: {1}

Total Volume %: {2}
""".format(str(TVL24) + ' $', str(TV24) + ' $', '+ ' + str(TV24 / TV48 * 100) + ' $' if TV24 / TV48 > 1 else '-' + str(round((1 - TV24 / TV48) * 100, 2)) + ' %')
    bot_sync.send_message(CHAT_ID, mess )


async def scheduler():
    aioschedule.every().day.at("21:02").do(join)
    aioschedule.every().day.at("21:05").do(warning)
    aioschedule.every().day.at("21:10").do(most_active_user)
    aioschedule.every().day.at("21:15").do(metrics_chat)
    
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)

async def on_startup(_):
    bot_sync = telebot.TeleBot(token=TOKEN_BOT)
    asyncio.create_task(scheduler())

if __name__ == "__main__":

    # Запуск бота
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)

    