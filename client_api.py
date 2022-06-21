from time import sleep
from dotenv import load_dotenv
import os
import asyncio
from telethon import TelegramClient, events
import json

load_dotenv()

api_id = os.getenv('client_api_id')
api_hash = os.getenv('api_hash')
#chat_id = os.getenv('CHAT_ID')
chat_id = -758117165 #test bot analyze

#client = TelegramClient('session_name', api_id, api_hash)


async def tip_for_user(tg_id,value):
    # отправляет запрос на пополнение счёта. 5 раз проверяет (с ожидание по 4 сек = 20сек) подтвердилась ли транзакция
    # Если нет, то на 5-ый раз повторяет попытку транзакции

    # Есть риск ошибочной двойной транзакции. Особенно если в боте 
    client = TelegramClient('session2', api_id, api_hash)
    await client.start()
    await client.send_message(f'ErgoTipperBot", "/t id=@ergodex_community,{tg_id} {value} kushti test')
    for tries in range(10):
        try:
            await asyncio.sleep(4)
            messages = await client.get_messages("ErgoTipperBot")
            print(messages[0].text)
            if "/t id=" in str(messages[0].text):
                print('\n no \n')
                print(type(messages))
                print(json.loads(messages))
                raise Exception()
            else :
                print('\n yes \n')
                print(type(messages))
                tries=-1
                break
        except Exception:
            if tries == 5:
                await client.send_message("ErgoTipperBot", "/t id=@ergodex_community,1335565003 1 kushti test")
            else:
                pass
    print("tries = ",tries)
    if tries == -1:
        return 1
    else:
        return 0

async def get_bot_balance(tg_id,value):
    async def tip_for_user(tg_id,value):
    # отправляет запрос на пополнение счёта. 5 раз проверяет (с ожидание по 4 сек = 20сек) подтвердилась ли транзакция
    # Если нет, то на 5-ый раз повторяет попытку транзакции

    # Есть риск ошибочной двойной транзакции. Особенно если в боте 
    client = TelegramClient('session2', api_id, api_hash)
    await client.start()
    await client.send_message(f'ErgoTipperBot", "/t id=@ergodex_community,{tg_id} {value} kushti test')
    for tries in range(10):
        try:
            await asyncio.sleep(4)
            messages = await client.get_messages("ErgoTipperBot")
            print(messages[0].text)
            if "/t id=" in str(messages[0].text):
                print('\n no \n')
                print(type(messages))
                print(json.loads(messages))
                raise Exception()
            else :
                print('\n yes \n')
                print(type(messages))
                tries=-1
                break
        except Exception:
            if tries == 5:
                await client.send_message("ErgoTipperBot", "/balance")
            else:
                pass
    print("tries = ",tries)
    if tries == -1:
        return 1
    else:
        return 0

async def get_bot_mess():
    messages = await client.get_messages(1335565003)
    print(messages)

if __name__ == "__main__":
    asyncio.run(tip_for_user(tg_id="1335565003",value=1))
    #asyncio.sleep(3)
    #asyncio.run(get_bot_mess())
    #asyncio.run(send_tips(tg_id="1335565003", amount=1))
    #send_tips_sync(tg_id="1335565003", amount=1)


#client.start()
# async def send_tips(tg_id, amount):
#     async with client:
#          client.loop.run_until_complete(client.send_message(5061420716, f"//t id=@ergodex_community,{tg_id} {amount} kushti test" ))
# #     client.loop.run_until_complete(main())
        

# async def main():
#     pass
#     # Getting information about yourself
#     #await client.send_message(5061420716, r"/t id=@ergodex_community,1335565003 1 kushti test" )
#     # me = await client.get_me()

#     # # "me" is a user object. You can pretty-print
#     # # any Telegram object with the "stringify" method:
#     # print(me.stringify())

#     # # When you print something, you see a representation of it.
#     # # You can access all attributes of Telegram objects with
#     # # the dot operator. For example, to get the username:
#     # username = me.username
#     # print(username)
#     # print(me.phone)

#     # # You can print all the dialogs/conversations that you are part of:
#     # async for dialog in client.iter_dialogs():
#     #     print(dialog.name, 'has ID', dialog.id)

#     # # You can send messages to yourself...
#     # await client.send_message('me', 'Hello, myself!')
#     # # ...to some chat ID
    
#     # # ...to your contacts
#     # #await client.send_message('+34600123123', 'Hello, friend!')
#     # # ...or even to any username
#     # #await client.send_message('MaximFN', 'Testing Telethon!')

#     # # You can, of course, use markdown in your messages:
#     # message = await client.send_message(
#     #     'me',
#     #     'This message has **bold**, `code`, __italics__ and '
#     #     'a [nice website](https://example.com)!',
#     #     link_preview=False
#     # )

#     # # Sending a message returns the sent message object, which you can use
#     # print(message.raw_text)

#     # # You can reply to messages directly if you have a message object
#     # await message.reply('Cool!')

#     # # Or send files, songs, documents, albums...
#     # await client.send_file('me', '/home/me/Pictures/holidays.jpg')

#     # # You can print the message history of any chat:
#     # async for message in client.iter_messages('me'):
#     #     print(message.id, message.text)

#     #     # You can download media from messages, too!
#     #     # The method will return the path where the file was saved.
#     #     if message.photo:
#     #         path = await message.download_media()
#     #         print('File saved to', path)  # printed after download is done

# # with client:
# #     client.loop.run_until_complete(main())

# async def send_and_check_transaction(tg_id, amount):

#     messages = client.get_message_history(tg_id)
#     print(messages)


# def send_tips_sync(tg_id, amount):
#     with client:
#         client.loop.run_until_complete(send_and_check_transaction(tg_id, amount))
        #client.loop.run_until_complete(client.send_message(5061420716, f"/t id=@ergodex_community,{tg_id} {amount} kushti test" ))

# @client.on(events.NewMessage(chats=('ErgoTipperBot')))
# async def normal_handler(event):
# #    print(event.message)
#     print(event.message.to_dict()['message'])

