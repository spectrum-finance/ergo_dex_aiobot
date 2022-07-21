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
from telethon import TelegramClient, events
import json
from tqdm import tqdm

print("\n v0.1.0")
#253476728

async def get_client_id():
    myself = await client.get_me()
    print(myself.id)
    return myself.id

load_dotenv()
TOKEN_BOT = os.getenv('TOKEN_BOT')

api_id = os.getenv('client_api_id')
api_hash = os.getenv('api_hash')
#chat_id = os.getenv('CHAT_ID')
#chat_id = -758117165 #test bot analyze


CHAT_ID = os.getenv('CHAT_ID')
ergo_bot_id = 5061420716

bot_sync = telebot.TeleBot(token=TOKEN_BOT)

client = TelegramClient('session', api_id, api_hash)
client.start()



RECORD_TODAY = False



async def reload_record_boolean():
    global RECORD_TODAY
    RECORD_TODAY = False

#bot_sync.polling()
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
    Ago24DateTime = datetime.datetime.now()
    Ago48DateTime = datetime.datetime.now() - datetime.timedelta(hours = 24 * 7)
    res = requests.get("https://api.ergodex.io/v1/amm/platform/stats?from={0}&to={1}".format(int(time.mktime(Ago48DateTime.timetuple()) * 1000), 
                                                                                             int(time.mktime(Ago24DateTime.timetuple()) * 1000))).json()
    for tries in range(9):   
        try: 
            if 'volume' in res:
                 return res
            else:
                res = requests.get("https://api.ergodex.io/v1/amm/platform/stats?from={0}&to={1}".format(int(time.mktime(Ago48DateTime.timetuple()) * 1000), 
                                                                                              int(time.mktime(Ago24DateTime.timetuple()) * 1000))).json()
        except Exception:
            print(res)
            res = requests.get("https://api.ergodex.io/v1/amm/platform/stats?from={0}&to={1}".format(int(time.mktime(Ago48DateTime.timetuple()) * 1000), 
                                                                                              int(time.mktime(Ago24DateTime.timetuple()) * 1000))).json()                                                                             
    if tries == 8:
        print("Network error")
        return 0


# def get_markets2():
#     Ago24DateTime = datetime.datetime.now() - datetime.timedelta(hours = 24)
#     Ago48DateTime = Ago24DateTime - datetime.timedelta(hours = 24)
#     res = requests.get("https://api.ergodex.io/v1/amm/platform/stats?from={0}&to={1}".format(int(time.mktime(Ago48DateTime.timetuple()) * 1000), 
#                                                                                              int(time.mktime(Ago24DateTime.timetuple()) * 1000))).json()
#     for tries in range(9):    
#         try: 
#             if int(res['volume']['value'])>0:
#                 return res
#             else:
#                 res = requests.get("https://api.ergodex.io/v1/amm/platform/stats?from={0}&to={1}".format(int(time.mktime(Ago48DateTime.timetuple()) * 1000), 
#                                                                                              int(time.mktime(Ago24DateTime.timetuple()) * 1000))).json()
#         except Exception:
#             print(res)
#             res = requests.get("https://api.ergodex.io/v1/amm/platform/stats?from={0}&to={1}".format(int(time.mktime(Ago48DateTime.timetuple()) * 1000), 
#                                                                                              int(time.mktime(Ago24DateTime.timetuple()) * 1000))).json()

def get_markets3():
    Ago24DateTime = datetime.datetime.now() - datetime.timedelta(hours = 24 * 7)
    Ago48DateTime = Ago24DateTime - datetime.timedelta(hours = 24 * 7)
    res = requests.get("https://api.ergodex.io/v1/amm/platform/stats?from={0}&to={1}".format(int(time.mktime(Ago48DateTime.timetuple()) * 1000), 
                                                                                             int(time.mktime(Ago24DateTime.timetuple()) * 1000))).json()
    return res

def TVL_sunday():
    df1 = pd.json_normalize(get_markets1()) 
    TVL_sunday = df1['tvl.value'][0] / 10**df1['tvl.units.currency.decimals'][0]
    return TVL_sunday

def TVL_record():
    df1 = pd.json_normalize(get_markets1()) 
    TVL_record = df1['tvl.value'][0] / 10**df1['tvl.units.currency.decimals'][0]
    return TVL_record

def TV_today():
    df_TV = pd.json_normalize(get_TV_record())
    TV_today = df_TV['volume.value'][0] / 10**df_TV['volume.units.currency.decimals'][0]
    return TV_today

def get_markets_swap():
    Ago24DateTime = datetime.datetime.now()
    Ago48DateTime = datetime.datetime.now() - datetime.timedelta(hours = 24 * 7)
    res = requests.get("https://api.ergodex.io/v1/amm/swaps?from={0}&to={1}".format(int(time.mktime(Ago48DateTime.timetuple()) * 1000), 
                                                                                             int(time.mktime(Ago24DateTime.timetuple()) * 1000))).json()
    return res

def get_markets_deposits():
    Ago24DateTime = datetime.datetime.now()
    Ago48DateTime = datetime.datetime.now() - datetime.timedelta(hours = 24 * 7)
    res = requests.get("https://api.ergodex.io/v1/amm/deposits?from={0}&to={1}".format(int(time.mktime(Ago48DateTime.timetuple()) * 1000), 
                                                                                             int(time.mktime(Ago24DateTime.timetuple()) * 1000))).json()
    return res

def get_TV_record():
    Ago24DateTime = datetime.datetime.now() 
    Ago48DateTime = datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    res = requests.get("https://api.ergodex.io/v1/amm/platform/stats?from={0}&to={1}".format(int(time.mktime(Ago48DateTime.timetuple()) * 1000), 
                                                                                             int(time.mktime(Ago24DateTime.timetuple()) * 1000))).json()
    return res


def get_markets_swap_record():
    Ago24DateTime = datetime.datetime.now() 
    Ago48DateTime = datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    res = requests.get("https://api.ergodex.io/v1/amm/swaps?from={0}&to={1}".format(int(time.mktime(Ago48DateTime.timetuple()) * 1000), 
                                                                                             int(time.mktime(Ago24DateTime.timetuple()) * 1000))).json()
    return res

def get_markets_deposits_record():
    Ago24DateTime = datetime.datetime.now()
    Ago48DateTime = datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    res = requests.get("https://api.ergodex.io/v1/amm/deposits?from={0}&to={1}".format(int(time.mktime(Ago48DateTime.timetuple()) * 1000), 
                                                                                             int(time.mktime(Ago24DateTime.timetuple()) * 1000))).json()
    return res

def swap_tran():
    df_swap_record = pd.json_normalize(get_markets_swap_record())
    swap_tran = df_swap_record['maxTxValue'][0] / 10**df_swap_record['units.currency.decimals'][0]
    return swap_tran

def swap_num():
    df_swap_record = pd.json_normalize(get_markets_swap_record())
    swap_num = df_swap_record['numTxs'][0]
    return swap_num

def deposit_tran():
    df_deposits_record = pd.json_normalize(get_markets_deposits_record())
    deposit_tran = df_deposits_record['maxTxValue'][0] / 10**df_deposits_record['units.currency.decimals'][0]
    return deposit_tran

def deposit_num():
    df_deposits_record = pd.json_normalize(get_markets_deposits_record())
    deposit_num = df_deposits_record['numTxs'][0]
    return deposit_num

    
# Проверка на рекорд
def checkRecord():
    global RECORD_TODAY
    
    df2 = pd.json_normalize(get_markets1())
    TV24 = df2['volume.value'][0] / 10**df2['volume.units.currency.decimals'][0]
    
    df1 = pd.json_normalize(get_markets2())
    TVL24 = df1['tvl.value'][0] / 10**df1['tvl.units.currency.decimals'][0]

    df_swap = pd.json_normalize(get_markets_swap())
    df_deposits = pd.json_normalize(get_markets_deposits())
    
    current_values = pd.DataFrame([[TVL24,
                                    TV24,
                         df_swap['maxTxValue'][0] / 10**df_swap['units.currency.decimals'][0], 
                         df_deposits['maxTxValue'][0] / 10**df_deposits['units.currency.decimals'][0],
                         df_swap['numTxs'][0], 
                         df_deposits['numTxs'][0]
                        ]], columns = ['TVL',
                                       'Total Volume', 
                                       'Max transaction value', 
                                       'Max deposit value',
                                       'Transactions',
                                       'Deposits'
                                      ])
    
    # здесь чтение из БД - нужно доработать чтение в датафрейм из БД (еще будет TVL)
    
    records = pd.DataFrame([[1175944.93,
                             9350582.96,
                        72584.89,
                        337.71,
                        38501,
                        4805
                        ]], columns = ['TVL',
                                       'Total Volume', 
                                       'Max transaction value', 
                                       'Max deposit value',
                                       'Transactions',
                                       'Deposits'
                                      ])
    
    list_records = []
    for index, value in enumerate(current_values.iloc[0].tolist()):
        if records.iloc[0, index] < value:
            records.iloc[0, index] = value
            list_records.append(str(list(records.columns)[index]) + ': ' + str(value))
            RECORD_TODAY = True
            
    printstr = '%s \n%s' % (', '.join(list_records[:-1]), str(list_records[-1]))
    print("Record metrics: \n%s" % printstr)
        
    # Дальше, если true, меняем содержимое БД/заносим новую строку
    return records

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

async def calculate_the_lack_of_funds():
    balance = float(await get_tipper_balance())
    list_tip = await get_tip_amount_values()
    required_balance = float(sum(list_tip))
    print("balance = ",balance)
    print("required_balance = ",required_balance)
    if required_balance>balance:
        await send_mess_admins(f'''[auto tipper] not enough funds for reward \n\n
balance: {balance}\nrequired balance: {required_balance}\n\n
Add another {required_balance - balance} for a successful transaction
Or change the amount of the contest participants' remuneration in the bot settings, in the "Tipping" tab -> "tip amount" ''')




async def get_tipper_balance():
    print('into get_tipper!')
    status = "?"
    #await client.start()
    for tries in range(10):
        try:
            name = "ErgoTipperBot"
            entity = await client.get_entity(name)
            #await client.send_message("ErgoTipperBot", "/balance")
            await client.send_message(entity=entity,message="/balance")
            await asyncio.sleep(4)
            messages = await client.get_messages("ErgoTipperBot")
            last_mess = str(messages[0].text)
            print(last_mess)
            if "Your tip wallet balance is" in last_mess:
                print("balance have been got")
                balance_info = last_mess.split("\n")[4]
                try:
                    value = float(balance_info.replace("  ", " ").split(" ")[-1])
                    print(value)
                    return value
                except Exception as e:
                    print(e)

                status = 'ok'
                break
            else:
                print ("No issues?")

        except Exception:
            if tries == 5:
                    await client.send_message("ErgoTipperBot", "/balance")
            else:
                pass

async def get_tipper_wallet():
    print('into get_tipper!')
    status = "?"
    #await client.start()
    for tries in range(10):
        try:
            name = "ErgoTipperBot"
            entity = await client.get_entity(name)
            #await client.send_message("ErgoTipperBot", "/balance")
            await client.send_message(entity=entity,message="/address")
            await asyncio.sleep(3)
            messages = await client.get_messages("ErgoTipperBot")
            last_mess = str(messages[0].text)
            print(last_mess)
            if "Your tip wallet address is" in last_mess:
                print("address have been got")
                balance_info = last_mess.split("\n")[0].split(" ")[-1]
                print("/n/n/n", balance_info.split(" ")[-1])
                try:
                    value = float(balance_info.replace("  ", " ").split(" ")[-1])
                    print(value)
                except Exception as e:
                    return balance_info

                status = 'ok'
                break
            else:
                print ("No issues?")

        except Exception:
            if tries == 5:
                    await client.send_message("ErgoTipperBot", "/balance")
            else:
                pass

async def create_session_client():
    await client.start()

async def rewarding_users():
    top = await get_top_3_users()
    print(top)
    #client = TelegramClient('session2', api_id, api_hash)
    reward_status = []
    for winner in top:
        print(winner[1])
        tg_id = winner[1] 

        await asyncio.sleep(1)
        await client.start()
        await client.send_message("ErgoTipperBot", f"/t id=@ergodex_community,{tg_id} 1 kushti test")
        for tries in range(10):
            try:
                await asyncio.sleep(10)
                messages = await client.get_messages("ErgoTipperBot")
                last_mess = str(messages[0].text)
                #print(messages[0].text)
                if "/t id=" in last_mess or "server returned an error" in last_mess :
                    print('\n no \n')
                    print(type(messages))
                    print(json.loads(messages))
                    raise Exception()
                else :
                    print('\n server answered \n')
                    if "you do not have enough ERG in your wallet to send" in last_mess :
                        print(' but u dont have money \n')
                        tries = 20
                    else:
                        tries=-1
                    print(type(messages))
                    break
            except Exception:
                if tries == 5:
                    await client.send_message("ErgoTipperBot", f"/t id=@ergodex_community,{tg_id} 1 kushti test")
                else:
                    pass

        if tries == -1:
            reward_status.append(1)
        elif tries == 20:
            reward_status.append(2)
        else:
            reward_status.append(0)

        print("tries = ",tries)

        print(messages)
    if 0 in reward_status or 2 in reward_status:
        for i in range(3):
            if reward_status[i] == 0:
                bad_transaction = top[i]
                tg_id_bad = bad_transaction[1]
                name_bad = bad_transaction[2]
                await send_mess_admins(f'[auto tipper] transaction error for the winner: \n{name_bad} | telegram id:{tg_id_bad}')
            elif reward_status[i] == 2:
                await send_mess_admins(f'[auto tipper] There are no funds on the bots balance')
                break
        await reload_users_stats()
    else:
        await send_mess_admins('[auto tipper] All transactions have been completed successfully')
        await reload_users_stats()


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
    # print("DONE")
    # #bot_sync.polling()
    # bot_sync.send_message( CHAT_ID, r"/t id=@ergodex_community, 1335565003, 1 kushti test" )
    # bot_sync.send_message( ergo_bot_id, r"/balance" )




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



async def update_TVL():
    TVL_now = TVL_sunday()
    await update_TVL_sunday(TVL_now)

# async def showStats():
#     df1 = pd.json_normalize(get_markets1())
#     df2 = pd.json_normalize(get_markets2())
#     df3 = pd.json_normalize(get_markets3())
#     df_swap = pd.json_normalize(get_markets_swap())
#     df_deposits = pd.json_normalize(get_markets_deposits())
    
#     TVL = df1['tvl.value'][0] / 10**df1['tvl.units.currency.decimals'][0]
    
#     TV7days = df2['volume.value'][0] / 10**df2['volume.units.currency.decimals'][0]
#     TV14days = df3['volume.value'][0] / 10**df3['volume.units.currency.decimals'][0]
    
#     TVdelta = TV7days / TV14days
    
#     df_swap['maxTxValue'][0] / 10**df_swap['units.currency.decimals'][0]
#     df_swap['numTxs'][0]
    
#     df_deposits['maxTxValue'][0] / 10**df_deposits['units.currency.decimals'][0]
#     df_deposits['numTxs'][0]
    
#     data = [[TVL, TV7days, TVdelta - 1, df_swap['maxTxValue'][0] / 10**df_swap['units.currency.decimals'][0],
#            df_deposits['maxTxValue'][0] / 10**df_deposits['units.currency.decimals'][0], df_swap['numTxs'][0], 
#     df_deposits['numTxs'][0]]]
#     df_review = pd.DataFrame(data, 
#                              columns = ['TVL', 'Total Volume', 'Total Volume %', 'MaxTransV',
#                                        'MaxDepoV', 'Transactions', 'Deposits'])
    
#     mess = """
# 📊 ErgoDEX Weekly Statistics:
    
# TVL: {0}

# Total Volume: {1}

# Total Volume %: {2}
    
# Max transaction value: {3}
    
# Max deposit value: {4}
    
# Transactions: {5}
    
# Deposits: {6}
    
#     """.format('$ ' + '{0:,}'.format(int(df_review['TVL'])).replace(',', ' '), 
#                '$ ' + '{0:,}'.format(int(df_review['Total Volume'])).replace(',', ' '),
#                '+' + str(round(df_review['Total Volume %'] - 1, 2)) + ' %' if int(df_review['Total Volume %']) >= 1 else '-' + str(float(round(1 - df_review['Total Volume %'], 2))) + ' %',
#                '$ ' + '{0:,}'.format(int(df_review['MaxTransV'])).replace(',', ' '),
#                '$ ' + '{0:,}'.format(int(df_review['MaxDepoV'])).replace(',', ' '),
#                '{0:,}'.format(int(df_review['Transactions'])).replace(',', ' '),
#                '{0:,}'.format(int(df_review['Deposits'])).replace(',', ' '))

#     bot_sync.send_message(CHAT_ID, mess)

async def get_last_week_TVL():
    tvl = await get_TVL_sunday()
    return tvl

async def showStats():
    df1 = pd.json_normalize(get_markets1())
    df2 = pd.json_normalize(get_markets2())
    df3 = pd.json_normalize(get_markets3())
    df_swap = pd.json_normalize(get_markets_swap())
    df_deposits = pd.json_normalize(get_markets_deposits())
    
    TVL = df1['tvl.value'][0] / 10**df1['tvl.units.currency.decimals'][0]
    
    TV7days = df2['volume.value'][0] / 10**df2['volume.units.currency.decimals'][0]
    TV14days = df3['volume.value'][0] / 10**df3['volume.units.currency.decimals'][0]

    
    TVdelta = TV7days / TV14days - 1
    
    df_swap['maxTxValue'][0] / 10**df_swap['units.currency.decimals'][0]
    df_swap['numTxs'][0]
    
    df_deposits['maxTxValue'][0] / 10**df_deposits['units.currency.decimals'][0]
    df_deposits['numTxs'][0]
    
    data = [[TVL, TV7days, TVdelta, df_swap['maxTxValue'][0] / 10**df_swap['units.currency.decimals'][0],
           df_deposits['maxTxValue'][0] / 10**df_deposits['units.currency.decimals'][0], df_swap['numTxs'][0], 
    df_deposits['numTxs'][0]]]
    df_review = pd.DataFrame(data, 
                             columns = ['TVL', 'Total Volume', 'Total Volume %', 'MaxTransV',
                                       'MaxDepoV', 'Transactions', 'Deposits'])
    last_week_TVL = await get_last_week_TVL()
    print(last_week_TVL)
    mess = """
📊 ErgoDEX Weekly Statistics:

TVL: {0}
TVL dynamics: {7}
TVL dynamics %: {8}
Total Volume: {1}
Total Volume %: {2}
Max transaction value: {3}
Max deposit value: {4}
Transactions: {5}
Deposits: {6}
    """.format('$ ' + '{0:,}'.format(int(df_review['TVL'])).replace(',', ' '), 
               '$ ' + '{0:,}'.format(int(df_review['Total Volume'])).replace(',', ' '),
               '+' + str(float(round(df_review['Total Volume %'] * 100, 2))) + ' %' if float(df_review['Total Volume %']) >= 0 else str(float(round(df_review['Total Volume %'] * 100, 2))) + ' %',
               '$ ' + '{0:,}'.format(int(df_review['MaxTransV'])).replace(',', ' '),
               '$ ' + '{0:,}'.format(int(df_review['MaxDepoV'])).replace(',', ' '),
               '{0:,}'.format(int(df_review['Transactions'])).replace(',', ' '),
               '{0:,}'.format(int(df_review['Deposits'])).replace(',', ' '),
               '$ ' + '{0:,}'.format(int(df_review['TVL'] - last_week_TVL)).replace(',', ' '),
               '+' + str(float(round(df_review['TVL'] / last_week_TVL * 100 - 100, 2))) + ' %' if float(df_review['TVL'] / last_week_TVL - 1) >= 0 else str(float(round(df_review['TVL'] / last_week_TVL * 100 - 100, 2))) + ' %'
              )
    bot_sync.send_message(CHAT_ID, mess)

async def spam():
    await client.send_message("Test_bot_analyze", "mess")



async def record_metrics_update():
    global RECORD_TODAY
    records_history = await get_records_metrics()
    # mess = "metrics: \n"
    # for key in records:
    #     mess+=key.replace("_"," ")+":  "+ str(records[key]) +"\n"
    # print(mess)
    
    
    current_values = pd.DataFrame([[TVL_record(),
                                TV_today(),
                                swap_tran(),
                                deposit_tran(),
                                swap_num(), 
                                deposit_num()
                               ]], columns = ['TVL',
                                              'Total Volume', 
                                              'Max transaction value', 
                                              'Max deposit value',
                                              'Transactions',
                                              'Deposits'
                                      ])
    
    # здесь чтение из БД - нужно доработать чтение в датафрейм из БД (еще будет TVL)
    
    # records = pd.DataFrame([[1175944.93,
    #                          9350582.96,
    #                     72584.89,
    #                     337.71,
    #                     38501,
    #                     4805
    #                     ]], columns = ['TVL',
    #                                    'Total Volume', 
    #                                    'Max transaction value', 
    #                                    'Max deposit value',
    #                                    'Transactions',
    #                                    'Deposits'
    #                                   ])
    for key in records_history:
        records_history[key] = [records_history[key]] 

    records = pd.DataFrame.from_dict(records_history)

    # records = pd.DataFrame.from_dict(records_history, orient='index',
    #                    columns=['TVL',
    #                                    'Total Volume', 
    #                                    'Max transaction value', 
    #                                    'Max deposit value',
    #                                    'Transactions',
    #                                    'Deposits'])

    print(records)

    

    list_records = []

    for index, value in enumerate(current_values.iloc[0].tolist()):
        if records.iloc[0, index] < value:

            records.iloc[0, index] = value
            extra_dollar = ""
            name_column = str(list(records.columns)[index])

            if name_column in ["TVL","Total_Volume","Max_transaction_value","Max_deposit_value"]:
                extra_dollar = " $"

            mess_record = name_column.replace("_"," ") + ': ' + '{0:,}'.format(int(value)).replace(',', ' ') + extra_dollar

            if RECORD_TODAY == False:
                text = f"🥳 We have a new record!\n\n{mess_record}"
                bot_sync.send_message(CHAT_ID, text)
            await change_metrics_record({str(list(records.columns)[index]):value})
            #list_records.append(str(list(records.columns)[index]) + ': ' + str(value))
            RECORD_TODAY = True
            
    #printstr = '%s \n%s' % (', '.join(list_records[:-1]), str(list_records[-1]))
    #print("Record metrics: \n%s" % printstr)
        
    # Дальше, если true, меняем содержимое БД/заносим новую строку
    return records

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
    # нужно для того чтобы выводило максимум один рекорд в день
    aioschedule.every().day.at("23:01").do(reload_record_boolean)

    aioschedule.every().monday.at("18:00").do(join)
    aioschedule.every().wednesday.at("18:00").do(join)
    aioschedule.every().friday.at("18:00").do(join)
    aioschedule.every().sunday.at("18:00").do(join)

    aioschedule.every().day.at("23:00").do(warning)
    ## test

    #Вознаграждение 3 топ пользователей. Обнуляет счётсчик сообщений в чате. Пока что каждое воскресенье в 20:00 по серверу - 21:00 по мск
    # Пока что тестим
    # aioschedule.every().sunday.at("20:00").do(rewarding_users)
    aioschedule.every().thursday.at("17:40").do(rewarding_users)
    #aioschedule.every().minute.do(get_tipper_balance)

    # Вычисляем,достаточно ли средств для вознаграждений 
    #aioschedule.every().sunday.at("19:00").do(calculate_the_lack_of_funds)
    #aioschedule.every().saturday.at("19:00").do(calculate_the_lack_of_funds)
    #aioschedule.every().sunday.at("20:10").do(calculate_the_lack_of_funds)
    ## Вывод рекордов
    # aioschedule.every().minute.do(record_metrics_update)
    aioschedule.every(10).minutes.do(record_metrics_update)
    #test
    #aioschedule.every(10).seconds.do(record_metrics_update)
    #  спам
    #aioschedule.every().second.do(spam)

    ## Вывод статистики по мск 18-00
    #aioschedule.every().minute.do(showStats)
    aioschedule.every().sunday.at("17:00").do(showStats)

    #Обновление TVL_sunday (по мск 18-01)
    aioschedule.every().sunday.at("17:01").do(update_TVL)
    #aioschedule.every(10).seconds.do(showStats)

    ##
    
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
    #asyncio.run(send_mess_admins("Тестовая рассылка сообщений админам #2"))
    #print(asyncio.run(rewarding_users()))
    pass
    