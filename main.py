
from api.main import get_pretty_markets, get_markets
from threading import Thread    

from bot_aio import start_bot
from tasks import tasks_loop
#@bot.message_handler(commands=['competition'])
#def start_message(message):
#  bot.send_message(message.chat.id," Statistics fiction contest ")
thread1 = Thread(target=start_bot)
thread2 = Thread(target=tasks_loop)

thread1.start()
thread2.start()
thread1.join()
thread2.join()
