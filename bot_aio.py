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

from tasks_bot import on_startup


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
        name = str(msg["from"]["first_name"]) + " " + str(msg["from"]["last_name"])
        username = str(msg["from"]["username"])
        if int(chat_id) == CHAT_ID:
            await count_mess_user(user_id, name, username)
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


if __name__ == "__main__":
    # Запуск бота
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)

    