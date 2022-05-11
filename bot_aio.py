import logging, os

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import BotBlocked, NetworkError

from aiogram.dispatcher.filters import Text
import aiofiles.os as aios

from dotenv import load_dotenv
import asyncio
from contextlib import suppress
import InlineKeyboards
import ReplyKeyboards
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

from aiogram.contrib.fsm_storage.memory import MemoryStorage



from tasks_bot import on_startup


load_dotenv()
TOKEN_BOT = os.getenv('TOKEN_BOT')
CHAT_ID=-1001489275471 #ErgoDEX chat com
TEST_CHAT_ID= -1001721723642 #Test Bot Analyze

#logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

# Объект бота
bot_sync = telebot.TeleBot(token=TOKEN_BOT)
bot = Bot(token=TOKEN_BOT)
# Диспетчер для бота
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

###############################
####       EXCEPTIOS       ####
###############################

@dp.errors_handler(exception=BotBlocked)
async def error_bot_blocked(update: types.Update, exception: BotBlocked):
    # Update: объект события от Telegram. Exception: объект исключения
    # Здесь можно как-то обработать блокировку, например, удалить пользователя из БД
    logging.info(f"Меня заблокировал пользователь!\nСообщение: {update}\nОшибка: {exception}")
    print(f"Меня заблокировал пользователь!\nСообщение: {update}\nОшибка: {exception}")

    # Такой хэндлер должен всегда возвращать True,
    # если дальнейшая обработка не требуется.
    return True

@dp.errors_handler(exception=NetworkError)
async def error_bot_blocked(update: types.Update, exception: NetworkError):
    # Update: объект события от Telegram. Exception: объект исключения
    # Здесь можно как-то обработать блокировку, например, удалить пользователя из БД
    logging.info(f"Network error: {update}\nОшибка: {exception}")
    print(f"Network error:\nСообщение: {update}\nОшибка: {exception}")

    # Такой хэндлер должен всегда возвращать True,
    # если дальнейшая обработка не требуется.
    return True

###############################
####                       ####
###############################

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


@dp.message_handler(commands="most_active_user")
async def cmd_most_active(message: types.Message):
    if message.chat.type == 'private':
        if await is_admin(message.chat.id) == 1:
            await message.reply("Привет админ")
            user = await get_most_active_user()
            user_id = user[1]
            name = user[2]
            username= user[3]
            is_admin_user = user[4]
            user_mess_count = user[5]
            reputation = user[6]
            mess = f"Самый активный пользователь в чате:  {name} @{username} \n   \n Кол-во сообщений: {user_mess_count}"
            await message.answer(mess)

        else:
            print(message.chat.id)
            await message.reply("Ты не админ")

    elif message.chat.type == 'supergroup':
        await message.reply("This command allow just in private")

# @dp.message_handler(commands="admin")
# async def cmd_admin(message: types.Message):
#     if message.chat.type == 'private':
#         if await is_admin(message.chat.id) == 1:
#             await message.reply("Привет админ")
#             socials = await get_all_soc()
#             await message.answer('Редактирование панели социальных сетей:', reply_markup=await InlineKeyboards.get_social_admin_keyboard())

#         else:
#             print(message.chat.id)
#             await message.reply("Ты не админ")

#     elif message.chat.type == 'supergroup':
#         await message.reply("This command allow just in private")

@dp.message_handler(commands="admin")
async def cmd_admin2(message: types.Message):
    if message.chat.type == 'private':
        if await is_admin(message.chat.id) == 1:
            await message.reply("Привет админ")
            #socials = await get_all_soc()
            await message.answer('Выберите пункты для администрирования:', reply_markup= ReplyKeyboards.admin_keyboard)

        else:
            print(message.chat.id)
            await message.reply("Ты не админ")

    elif message.chat.type == 'supergroup':
        await message.reply("This command allow just in private")

###################################
############## State ##############
###################################

class EditSocials(StatesGroup):
    name_soc = State()
    atr_edit = State()
    send_value = State()


@dp.message_handler(Text(equals="Социальные сети"))
async def admin_soc(message: types.Message):
    if message.chat.type == 'private':
        if await is_admin(message.chat.id) == 1:
            #await message.reply("Привет админ")
            #socials = await get_all_soc()
            
            await message.answer('Выберите социальную сеть:', reply_markup= await ReplyKeyboards.get_social_admin_keyboard())
            await EditSocials.name_soc.set()
            
        else:
            print(message.chat.id)
            await message.reply("Ты не админ")

@dp.message_handler(Text(equals="Тексты"))
async def admin_text(message: types.Message):
    if message.chat.type == 'private':
        if await is_admin(message.chat.id) == 1:
            #await message.reply("Привет админ")
            #socials = await get_all_soc()
            
            await message.answer('Выберите текст:', reply_markup= await ReplyKeyboards.get_text_admin_keyboard())
            await EditTexts.name_text.set()
            
        else:
            print(message.chat.id)
            await message.reply("Ты не админ")

#Социальные сети

@dp.message_handler(state=EditSocials.name_soc)
async def get_name_soc(message: types.Message, state: FSMContext):
    available_soc_names = []
    for soc in await get_all_soc():
        text = soc[1]
        available_soc_names.append(text)
    if message.text not in available_soc_names:
        await message.answer("Пожалуйста, выберите социальную сеть, используя клавиатуру ниже.")
        return
    await state.update_data(name_soc=message.text)

    info_soc = list(await get_soc_info_by_name(message.text))
    column_names = ['id', 'id_social', 'invite_text', 'url', 'img', 'time_edit']
    if not info_soc[4] is None:
        info_soc[4] = "img uploaded"
    info_soc_mess= f"[{message.text}]info:\n\n {column_names[2]}  :  {info_soc[2]} \n {column_names[3]}  :  {info_soc[3]} \n {column_names[4]}  :  {info_soc[4]}"
    await message.answer(info_soc_mess)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for size in ["invite_text","url","img"]:
        keyboard.add(size)
    # Для последовательных шагов можно не указывать название состояния, обходясь next()
    await message.answer("Теперь выберите атрибут для редактирования: \n\nПерервать ввод можно командой /cancel", reply_markup=keyboard)
    await EditSocials.next()



@dp.message_handler(state=EditSocials.atr_edit)
async def get_atr(message: types.Message, state: FSMContext):
    if message.text not in ["invite_text","url","img"]:
        await message.answer("Пожалуйста, выберите атрибут, используя клавиатуру ниже.")
        return
    await state.update_data(atr_edit=message.text)
    
    # Для последовательных шагов можно не указывать название состояния, обходясь next()
    await message.answer("Введите новое значение атрибута: \n\nПрервать ввод /cancel", reply_markup=types.ReplyKeyboardRemove())
    await EditSocials.next()



@dp.message_handler(state=EditSocials.send_value)
async def get_value(message: types.Message, state: FSMContext):
    #print(1)
    if message.text in [""," ","."]:
        await message.answer("Пожалуйста, введите не пустой значение атрибута")
        return
    await state.update_data(send_value=message.text)
    data = await state.get_data()
    await message.answer(f"Название соц сети: {data['name_soc']}\n"
                         f"атрибут: {data['atr_edit']}\n"
                         f"значение: {data['send_value']}\n")
    
    await edit_backup_soc_by_atr(data['name_soc'], data['atr_edit'], data['send_value'])

    info_soc = await get_soc_info_by_name(data['name_soc'])
    column_names = ['id', 'id_social', 'invite_text', 'url', 'img', 'time_edit']
    info_soc_mess= f"[{data['name_soc']}]edited data:\n\n {column_names[2]}  :  {info_soc[2]} \n {column_names[3]}  :  {info_soc[3]} \n {column_names[4]}  :  {info_soc[4]}"
    await message.answer(info_soc_mess)
    
    await state.finish()

@dp.message_handler(state=EditSocials.send_value, content_types=['photo'])
async def get_value(message: types.Message, state: FSMContext):
    #print(1)
    if message.text in [""," ","."]:
        await message.answer("Пожалуйста, введите не пустой значение атрибута")
        return
    await state.update_data(send_value=message.text)
    data = await state.get_data()
    try:
        now = datetime.datetime.now()
        current_time = now.strftime("_%H_%M_%S")
        file = f'value{current_time}.jpg'
        path = f'aiodata/{file}'
        await message.photo[-1].download(path)
        await insertBLOBsoc(data['name_soc'], path)
        print(message.photo)
    except Exception as e:
        print(e)


    await message.answer(f"Название соц сети: {data['name_soc']}\n"
                         f"атрибут: {data['atr_edit']}\n"
                         )

    info_soc = await get_soc_info_by_name(data['name_soc'])
    column_names = ['id', 'id_social', 'invite_text', 'url', 'img', 'time_edit']
    info_soc_mess= f"[{data['name_soc']}]edited data:\n\n {column_names[2]}  :  {info_soc[2]} \n {column_names[3]}  :  {info_soc[3]} \n "
    await message.answer(info_soc_mess)
    
    await state.finish()

#Тексты
#State

class EditTexts(StatesGroup):
    name_text = State()
    atr_edit = State()
    send_value = State()

@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()

    await message.reply('Cancelled.', reply_markup=types.ReplyKeyboardRemove())

@dp.message_handler(state=EditTexts.name_text)
async def get_name_text(message: types.Message, state: FSMContext):
    available_text_names = []
    texts = await get_all_texts()
    for text in texts:
        available_text_names.append(text[0])
    if message.text not in available_text_names:
        await message.answer("Пожалуйста, выберите социальную сеть, используя клавиатуру ниже.")
        return
    await state.update_data(name_text=message.text)
    info_text = list(await get_current_text_by_name(message.text))
    column_names = ['id', 'text', 'name', 'img', 'time_edit']
    if not info_text[3] is None:
        info_text[3] = "img uploaded"

    info_text_mess= f"[{message.text}]info:\n\n {column_names[1]}  :  {info_text[1]} \n {column_names[2]}  :  {info_text[2]} \n {column_names[3]}  :  {info_text[3]}"
    await message.answer(info_text_mess)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    for i in ["text","img"]:
        keyboard.add(i)
    # Для последовательных шагов можно не указывать название состояния, обходясь next()
    await message.answer("Теперь выберите атрибут для редактирования: \n\nПерервать ввод можно командой /cancel", reply_markup=keyboard)
    await EditTexts.next()


@dp.message_handler(state=EditTexts.atr_edit)
async def get_atr(message: types.Message, state: FSMContext):
    if message.text not in ["text","img"]:
        await message.answer("Пожалуйста, выберите атрибут, используя клавиатуру ниже.")
        return
    await state.update_data(atr_edit=message.text)
    await message.answer("Введите новое значение атрибута: \n\nПрервать ввод /cancel", reply_markup=types.ReplyKeyboardRemove())
    await EditTexts.next()

@dp.message_handler(state=EditTexts.send_value)
async def get_value(message: types.Message, state: FSMContext):
    if message.text in [""," ","."]:
        await message.answer("Пожалуйста, введите не пустой значение атрибута")
        return
    await state.update_data(send_value=message.text)
    data = await state.get_data()
    await message.answer(f"Название текста: {data['name_text']}\n"
                         f"атрибут: {data['atr_edit']}\n"
                         f"значение: {data['send_value']}\n")
    await edit_text_by_atr(data['name_text'], data['atr_edit'], data['send_value'])

    info_text = list(await get_current_text_by_name(data['name_text']))
    column_names = ['id', 'text', 'name', 'img', 'time_edit']
    if not info_text[3] is None:
        info_text[3] = "img uploaded"

    info_text_mess= f"[{data['name_text']}] info:\n\n {column_names[1]}  :  {info_text[1]} \n {column_names[2]}  :  {info_text[2]} \n {column_names[3]}  :  {info_text[3]}"
    await message.answer(info_text_mess)

    await state.finish()

@dp.message_handler(state=EditTexts.send_value, content_types=['photo'])
async def get_value(message: types.Message, state: FSMContext):
    if message.text in [""," ","."]:
        await message.answer("Пожалуйста, введите не пустой значение атрибута")
        return
    await state.update_data(send_value=message.text)
    data = await state.get_data()
    try:
        now = datetime.datetime.now()
        current_time = now.strftime("_%H_%M_%S")
        file = f'value{current_time}.jpg'
        path = f'aiodata/{file}'
        await message.photo[-1].download(path)
        await insertBLOBtext(data['name_text'], path)
        await delete_local_file(path)
        print(message.photo)
    except Exception as e:
        print(e)

    await state.finish()

async def delete_local_file(file_to_del):
    await aios.remove(file_to_del)
    print("deleted: "+file_to_del)



#@dp.message_handler(state=EditSocials.atr_edit)






###################################
########### commands   ############
###################################


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


# in chat buttons callbacks
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

# handler for all simple msgs
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

            if "reply_to_message" in msg:
                user_reply_id = msg["from"]["id"]
                user_source_id = msg["reply_to_message"]["from"]["id"]

                if user_reply_id != user_source_id: 
                    if msg.text == '+' or '++' or '+++':
                        print("+1 rep ")
                    else:
                        print("+0.1 rep ")
                    print( msg["reply_to_message"])
                else:
                    print("user reply ur own message")

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

    