from telethon.tl.functions.messages import GetInlineBotResultsRequest
from telethon import TelegramClient, events
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()

api_id = os.getenv('client_api_id')
api_hash = os.getenv('api_hash')
#chat_id = os.getenv('CHAT_ID')
chat_id = -758117165 #test bot analyze

client = TelegramClient('session2', api_id, api_hash)
client.start()

# async def request_bot(tg_id, amount):
#     for tries in range(10):
#         try:
#             bot_results = await client(GetInlineBotResultsRequest(
#                 bot = "@ergotipperbot",
#                 peer = "@ergotipperbot",
#                 query =  f"/t id=@ergodex_community,{tg_id} {amount} kushti test",
#                 offset=""
#             ))
#             print(bot_results)
#         except Exception as e:
#             print (e)
#             await asyncio.sleep(0.5)


if __name__ == "__main__":
    client.loop.run_until_complete(client.send_message(5061420716, f"/t id=@ergodex_community,{tg_id} {amount} kushti test" )
    #print(asyncio.run( client.get_entity('ErgoTipperBot')))
    #asyncio.run(request_bot(tg_id="1335565003", amount=1))
    # res = asyncio.run(client(GetInlineBotResultsRequest(
    #             "@ergotipperbot",
    #             "ErgoTipperBot",
    #             f"/t id=@ergodex_community,1335565003 1 kushti test",
    #             ""
    #         )))
    # print(res)