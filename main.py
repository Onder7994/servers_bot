import telebot
from telebot import types
from logger import Logging
from api import basicApiCall, servers, account
import os
import datetime

current_date = datetime.datetime.now().date()

BOT_TOKEN = os.environ.get("BOT_TOKEN")
VDSINA_API_TOKEN = os.environ.get("VDSINA_API_TOKEN")
LOG_FILE = f"/var/log/{current_date}_vdsina_bot.txt"

bot = telebot.TeleBot(BOT_TOKEN)
logger = Logging("vdsina_bot", LOG_FILE)
api_instance = basicApiCall(VDSINA_API_TOKEN, logger)
servers_api = servers(api_instance.hoster_token, api_instance.logger)
account_api = account(api_instance.hoster_token, api_instance.logger)

@bot.message_handler(commands=["start"])
def start(msg):
    markup_inline = types.InlineKeyboardMarkup(row_width=2)
    balance_button = types.InlineKeyboardButton("Проверить баланс", callback_data="balance_status")
    account_button = types.InlineKeyboardButton("Прогноз отключения", callback_data="account_data")
    servers_params_button = types.InlineKeyboardButton("Мои сервера", callback_data="servers_params")
    servers_stats_button = types.InlineKeyboardButton("Мониторинг серверов", callback_data="servers_stats")
    help_button = types.InlineKeyboardButton("Помощь", callback_data="help")
    markup_inline.add(balance_button, account_button, servers_params_button, servers_stats_button, help_button)
    if msg.text == "/start":
        bot.send_message(msg.chat.id, "Информационный серверный бот", reply_markup=markup_inline)

@bot.callback_query_handler(func=lambda call:True)
def callback(call):
    if call.message:
        if call.data == "help":
            bot.send_message(call.message.chat.id, "Для началы работы с ботом напишите /start")
        elif call.data == "balance_status":
            message = account_api.get_balance()
            bot.send_message(call.message.chat.id, message)
            logger.info("Запрос статуса в чате: %s", call.message.chat.id)
        elif call.data == "account_data":
            message = account_api.get_forecast()
            bot.send_message(call.message.chat.id, message)
            logger.info("Запрос прогноза отключения в чате: %s", call.message.chat.id)
        elif call.data == "servers_params":
            servers = servers_api.get_servers_name()
            if servers is not None:
                servers_str = ' | '.join(servers)
                msg = bot.send_message(call.message.chat.id, servers_str)
                msg = bot.send_message(call.message.chat.id, "Введите имя сервера: ")
                bot.register_next_step_handler(msg, get_servers_params, servers)
            else:
                msg = bot.send_message(call.message.chat.id, "Пустой массив servers")
        elif call.data == "servers_stats":
            servers = servers_api.get_servers_name()
            if servers is not None:
                servers_str = ' | '.join(servers)
                msg = bot.send_message(call.message.chat.id, servers_str)
                msg = bot.send_message(call.message.chat.id, "Введите имя сервера: ")
                bot.register_next_step_handler(msg, get_servers_monitoring, servers_str, call.message.chat.id)
            else:
                msg = bot.send_message(call.message.chat.id, "Пустой массив servers")

@bot.message_handler(content_types=["text"])
def message_handler(m):
    bot.send_message(m.chat.id, "Неверная команда")

def get_servers_params(msg, servers):
    if msg.text in servers:
        message = servers_api.get_server_params(msg.text)
        bot.send_message(msg.chat.id, message)
        logger.info("Запрос параметров сервера: %s, в чате: %s", msg.text, msg.chat.id)
    else:
        bot.send_message(msg.chat.id, "Выбранный сервер не существует")
        logger.warning("Введено неправильное имя сервера: %s, в чате: %s", msg.text, msg.chat.id)

def get_servers_monitoring(msg, servers, chat_id):
    if msg.text in servers:
        images_path = servers_api.get_server_monitoring(msg.text)
        if images_path is not None:
            for image in images_path:
                with open(image, 'rb') as img:
                    bot.send_photo(chat_id, img)
            logger.info("Запрос мониторинга сервера: %s", msg.text)
        else:
            bot.send_message(chat_id, "Не удалось отправить графики")
    else:
        bot.send_message(msg.chat.id, "Выбранный сервер не существует")
        logger.warning("Введено неправильное имя сервера: %s, в чате: %s", msg.text, msg.chat.id)

def main():
    bot.polling(none_stop=True, interval=0)

if __name__ == "__main__":
    main()
