from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiodata.main import add_soc, is_admin, get_all_soc,  get_all_current_backup_by_time_pretty
import asyncio

Discord = InlineKeyboardButton('Discord', url='https://discord.gg/6MFFG4Fn4Y')
Twitter = InlineKeyboardButton('Twitter', url='https://twitter.com/ErgoDex')
Reddit = InlineKeyboardButton('Reddit', url='https://www.reddit.com/r/ergodex/')
Github = InlineKeyboardButton('Github', url='https://github.com/ergolabs')
Medium = InlineKeyboardButton('Medium', url='https://ergodex.medium.com/')
Hello = InlineKeyboardButton('Hello', callback_data='Hello')

social_keyboard = InlineKeyboardMarkup(
            resize_keyboard=True
            ).add(Discord, Twitter).add(Reddit, Github).add(Medium, Hello)

async def get_social_join_keyboard():
    all_current = await get_all_current_backup_by_time_pretty()
    social_join_keyboard = InlineKeyboardMarkup(
            resize_keyboard=True
            )
    for soc in all_current:
        print(soc)
        social_join_keyboard.add(InlineKeyboardButton(soc[1], url=soc[3]))
    return social_join_keyboard

async def get_social_admin_keyboard():
    social_admin_keyboard = InlineKeyboardMarkup(
            resize_keyboard=True
            )
    socials = await get_all_soc()
    for soc in socials:
        if soc[2]==1:
            text = "🟢    "+soc[1]
        else:
            text = "🔴    "+soc[1]
        print(text)
        social_admin_keyboard.add(InlineKeyboardButton(text, callback_data="edit_soc "+str(soc[1])))
    return social_admin_keyboard

if __name__ == "__main__":
    print(asyncio.run(get_social_admin_keyboard()))