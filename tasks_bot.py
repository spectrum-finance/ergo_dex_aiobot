import telebot
import aioschedule
from dotenv import load_dotenv
import asyncio
from aiodata.main import *
import os
import pandas as pd
import requests
import datetime, time
from PIL import Image
from aiogram.utils.markdown import link

LOCAL_TIMEZONE = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
print("LOCAL_TIME ",datetime.datetime.now())
print("\n v0.1.0")


load_dotenv()
TOKEN_BOT = os.getenv('TOKEN_BOT')


CHAT_ID= -1001721723642

bot_sync = telebot.TeleBot(token=TOKEN_BOT)

@bot_sync.message_handler(func=lambda m: True)
def echo_all(message):
    print(message)
    print(message.text)
	#bot.reply_to(message, message.text)

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
    text_atrs = await get_current_text_by_name("warning")
    text = text_atrs[1]
    text_img = text_atrs[3]
    bot_sync.send_message(CHAT_ID, text)


async def warning_chat_image():
    text_atrs = await get_current_text_by_name("warning")
    text = text_atrs[1]
    text_img = text_atrs[3]
    if text_img is None or text_img == "NULL":
        bot_sync.send_message(CHAT_ID, text)
    else:
        now = datetime.datetime.now()
        current_time = now.strftime("_%H_%M_%S")
        filename = f'dbimage{current_time}.jpg'
        path = f'aiodata/{filename}'
        convert_data(text_img, filename)
        print(path)
        #img.save(file)
        img = open(filename, 'rb')
        bot_sync.send_message(CHAT_ID, text )
        bot_sync.send_photo(CHAT_ID, img)
        img.close()


        os.remove(filename)


def warning():
    try:
        asyncio.run(warning_chat())
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            asyncio.run(warning_chat())

async def join_soc_chat():
    text_atrs = await get_current_text_by_name("join_soc")
    text = text_atrs[1]
    text_img = text_atrs[3]
    print("text_img", text_img)
    all_current = await get_all_current_backup_by_time_pretty()
    print(text)
    print(all_current)
    text_soc = ""
    for soc in all_current:
        #text_soc += link(soc[2], soc[3]) +"\n"
        text_soc += f'<a href="{soc[3]}">{soc[2]}</a>'  +"\n"
        #text_soc += soc[2]+"  " +soc[3]+"\n"
    common_text = text + "\n\n" + text_soc
    bot_sync.send_message( CHAT_ID, common_text, disable_web_page_preview=True, parse_mode="HTML" )


async def join_soc_chat_image():
    text_atrs = await get_current_text_by_name("join_soc")
    text = text_atrs[1]
    text_img = text_atrs[3]
    print("text_img", text_img)
    all_current = await get_all_current_backup_by_time_pretty()
    print(text)
    print(all_current)
    text_soc = ""
    for soc in all_current:
        text_soc += soc[1]+"  " +soc[3]+"\n"
    common_text = text + "\n\n" + text_soc
    if text_img is None or text_img == "NULL":
        bot_sync.send_message( CHAT_ID, common_text, disable_web_page_preview=True )
    else:
        #img = Image.open(text_img)
        #img.show()
        now = datetime.datetime.now()
        current_time = now.strftime("_%H_%M_%S")
        filename = f'dbimage{current_time}.jpg'
        path = f'aiodata/{filename}'
        convert_data(text_img, filename)
        print(path)
        #img.save(file)
        img = open(filename, 'rb')
        bot_sync.send_message( CHAT_ID, common_text )
        bot_sync.send_photo( CHAT_ID, img )
        img.close()


        os.remove(filename)


    #reply_markup = await InlineKeyboards.get_social_join_keyboard()

async def join_soc_chat_buttons():
    text_atrs = await get_current_text_by_name("join_soc")
    text = text_atrs[1]
    text_img = text_atrs[3]
    print("text_img", text_img)
    all_current = await get_all_current_backup_by_time_pretty()
    print(text)
    print(all_current)
    markup = telebot.types.InlineKeyboardMarkup()
    for soc in all_current:
        markup.add(telebot.types.InlineKeyboardButton(soc[1], url = soc[3]))
    if text_img is None or text_img == "NULL":
        bot_sync.send_message(CHAT_ID, text ,reply_markup=markup)
    else:
        #img = Image.open(text_img)
        #img.show()
        now = datetime.datetime.now()
        current_time = now.strftime("_%H_%M_%S")
        filename = f'dbimage{current_time}.jpg'
        path = f'aiodata/{filename}'
        convert_data(text_img, filename)
        print(path)
        #img.save(file)
        img = open(filename, 'rb')
        bot_sync.send_message(CHAT_ID, text ,reply_markup=markup)
        bot_sync.send_photo(CHAT_ID, img)
        img.close()
        os.remove(filename)


def join_soc():
    try:
        asyncio.run(join_soc_chat())
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            asyncio.run(join_soc_chat())

async def rewarding_users():
    #bot_sync.send_message( CHAT_ID, common_text, disable_web_page_preview=True, parse_mode="HTML" )       
    # TODO
    # Сделать функцию рассылки админам информации
    # Проверить баланс бота, если не хватает для вознаграждения, попросить пополнить
    # Функция get_top_3_users()
    # Отсеить тех, у кого счёт 0
    # Функция, сообщающая о выигрыше, предупреждающая, что счёт пополнится в течение 2-х минут.
    # В админке есть доступ к балансу бота, сумме вознаграждений !3-ёх победителей.
    # Функция вознаграждаения пользователей. Работает с tipper-bot. На вход получает CHAT_ID, список словарей [USERS_ID: count,] 
    # После вознаграждения обновляет значение баланса, если вновь не хватает, уведомляет о нехватке


    # `1` тестируем общение между ботами
    # --> ругается, когда с двух устройств используется один токен
    # aiogram.utils.exceptions.TerminatedByOtherGetUpdates: Terminated by other getupdates request; make sure that only one bot instance is running
    print("DONE")
    bot_sync.send_message( CHAT_ID, r"/t id=@ergodex_community, 1335565003, 1 kushti test" )




    pass

async def send_mess_admins(text):
    admins = await admins_list()
    for admin in admins:
        try:
            print(admin)
            admin_id = admin[1]
            bot_sync.send_message( admin_id, text )
        except telebot.apihelper.ApiTelegramException:
            print("Telegram API was unsuccessful for admin:", admin )
        except Exception:
            pass
    pass



async def warning():
    await warning_chat()

async def join():
    await join_soc_chat()

async def reward():
    await rewarding_users()

async def most_active_user():
    user = await get_most_active_user()
    user_id = user[1]
    name = user[2]
    username= user[3]
    is_admin = user[4]
    user_mess_count = user[5]
    reputation = user[6]
    mess = f"The most active user in chat:  {name} @{username} \n   \n Number of messages: {user_mess_count}"
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
    ## aioschedule.every().day.at("9:14").do(join) # через день в 18:00 ТОЛЬКО ЭТО
    aioschedule.every().monday.at("16:00").do(join)
    aioschedule.every().wednesday.at("16:00").do(join)
    aioschedule.every().friday.at("16:00").do(join)
    aioschedule.every().sunday.at("16:00").do(join)
    ## test
    ## aioschedule.every().minute.do(join)
    ##
    aioschedule.every().day.at("17:00").do(warning)
    #aioschedule.every().minute.do(send_mess_admins("Тестовая рассылка админам"))

    ## aioschedule.every().day.at("02:24").do(most_active_user)
    ## aioschedule.every().day.at("02:24").do(metrics_chat)

    ## TODO
    ## Вознаграждение каждое воскресенье в 18:00
    ## 
    
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)

async def on_startup(_):
    bot_sync = telebot.TeleBot(token=TOKEN_BOT)
    asyncio.create_task(scheduler())


if __name__ == "__main__":
    asyncio.run(send_mess_admins("Тестовая рассылка сообщений админам #2"))
    