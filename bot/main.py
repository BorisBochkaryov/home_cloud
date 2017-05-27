# -*- coding: utf-8 -*-
import config, telebot
import server
from telebot import types
import requests

bot = telebot.TeleBot(config.token)

# команда /start
@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "Может хотети добавить ключ командой \"/key КЛЮЧ_ОТ_ВАШЕГО_HOME\"?")

# команда /key
@bot.message_handler(commands=["key"])
def key(message):
    [_, key] = message.text.split(" ")
    print(message.chat.id, " key = ", key)
    result = serverHome.saveKey(str.encode(key), message.chat.id)
    if result == "ok":
        bot.send_message(message.chat.id, "Ключ принят")
    else:
        bot.send_message(message.chat.id, "Ключ не принят")

@bot.message_handler(commands=["getfile"])
def getf(message):
    [_, fileName] = message.text.split(" ")
    binFile = serverHome.getFile(fileName, message.chat.id)
    bot.send_document(message.chat.id, binFile, caption=fileName)

# обычный текст
@bot.message_handler(content_types=["text"])
def sendmessage(message):
    if message.text == "Добавить ключ":
        print("OK   ",message.text)
        bot.send_message(message.chat.id, "Необходимо отправить ключ, который зарегистрирован на стороне Home")
    else:
        # клавиатура с меню
        keys = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        keys.add("Добавить ключ")
        bot.send_message(message.chat.id, "Ваш выбор?", reply_markup=keys)

# прием файлов
@bot.message_handler(content_types=["document"])
def sendfile(message):
    file_info = bot.get_file(message.document.file_id)
    file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(config.token, file_info.file_path))
    # file.content - binary файла
    print(message.document.file_size)
    serverHome.sendFile(message.chat.id, file.content, message.document.file_name, message.document.file_size)

if __name__ == '__main__':
    # запуск сервера
    serverHome = server.Server()
    # запуск бота
    bot.polling(none_stop=True)
