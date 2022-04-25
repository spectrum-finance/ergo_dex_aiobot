from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiodata.main import add_soc, is_admin, get_all_soc,  get_all_current_backup_by_time_pretty, get_all_texts
import asyncio


admin_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
admin_buttons = ["Социальные сети","Тексты"]
admin_keyboard.add(*admin_buttons)

async def get_social_admin_keyboard():
    social_admin_keyboard = ReplyKeyboardMarkup(
            resize_keyboard=True
            )
    socials = await get_all_soc()
    for soc in socials:
        if soc[2]==1:
            text = soc[1]
        else:
            text = soc[1]
        #print(text)
        social_admin_keyboard.add(text)
    return social_admin_keyboard

async def get_text_admin_keyboard():
    text_admin_keyboard = ReplyKeyboardMarkup(
            resize_keyboard=True
            )
    texts = await get_all_texts()
    for text in texts:
        #print(text[0])
        text_admin_keyboard.add(text[0])
    return text_admin_keyboard