import telebot
import aioschedule
from dotenv import load_dotenv
import asyncio
from aiodata.main import *

import pandas as pd
import requests
import datetime, time




load_dotenv()
TOKEN_BOT = os.getenv('TOKEN_BOT')

CHAT_ID= -1001721723642

bot_sync = telebot.TeleBot(token=TOKEN_BOT)

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
    name = user[2]
    username= user[3]
    is_admin = user[4]
    user_mess_count = user[5]
    reputation = user[6]
    mess = f"Самый активный пользователь в чате:  {name} @{username} \n   \n Кол-во сообщений: {user_mess_count}"
    bot_sync.send_message(CHAT_ID, mess )

async def metrics_chat():
    df1 = pd.json_normalize(get_markets2())
    TV48 = df1['volume.value'][0] / 10**df1['volume.units.currency.decimals'][0]
    df2 = pd.json_normalize(get_markets1())
    TVL24 = df1['tvl.value'][0] / 10**df1['tvl.units.currency.decimals'][0]
    TV24 = df2['volume.value'][0] / 10**df2['volume.units.currency.decimals'][0]
    data = [[str(TVL24) + ' $', str(TV24) + ' $', '+ ' + str(TV24 / TV48 * 100) + ' %' if TV24 / TV48 > 1 else '- ' + str(round((1 - TV24 / TV48) * 100, 2)) + ' %']]
    df_review = pd.DataFrame(data, columns = ['TVL', 'Total Volume', 'Total Volume %']) 
    #print(df_review)
    #mess = tabulate(str(df_review), headers='keys', tablefmt='psql') 
    mess ="""
TVL: {0}

Total Volume: {1}

Total Volume %: {2}
""".format(str(TVL24) + ' $', str(TV24) + ' $', '+ ' + str(TV24 / TV48 * 100) + ' $' if TV24 / TV48 > 1 else '-' + str(round((1 - TV24 / TV48) * 100, 2)) + ' %')
    bot_sync.send_message(CHAT_ID, mess )


async def scheduler():
    aioschedule.every().day.at("22:41").do(join)
    aioschedule.every().day.at("22:41").do(warning)
    aioschedule.every().day.at("22:41").do(most_active_user)
    aioschedule.every().day.at("22:41").do(metrics_chat)
    
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)

async def on_startup(_):
    bot_sync = telebot.TeleBot(token=TOKEN_BOT)
    asyncio.create_task(scheduler())