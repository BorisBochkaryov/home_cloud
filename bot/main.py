# -*- coding: utf-8 -*-
import config, telebot
import server
from telebot import types
import requests
import io

bot = telebot.TeleBot(config.token)

# команда /start
@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "Может хотите добавить ключ командой \"/key КЛЮЧ_ОТ_ВАШЕГО_HOME\"?")

@bot.message_handler(commands=["help"])
def help(message):
    help_str = '''Данный бот предназначен для вазможности сохранять все ваши личные файлы на "домашнем облаке".
    Для того чтобы начать работу вам необходимо отправить боту ключ, который выдан установленной на "домашнем облаке" программой.
    Сделать это можно с помощью команды /key YOUR_KEY.
    Отправив боту любой файл, он передаст его серверу для сохранения "домашнему облаку" в рабочей папке.
    Скачать необходимый файл из рабочей папки можно командой /getfile FILE_NAME.'''
    bot.send_message(message.chat.id,help_str)

@bot.message_handler(commands=["list"])
def list(message):
    list_files = serverHome.getList(message.chat.id)
    bot.send_message(message.chat.id,list_files)

@bot.message_handler(commands=["kinfo"])
def kinfo(message):
    k_inf = serverHome.getKernalInf(message.chat.id)
    bot.send_message(message.chat.id,k_inf)

# команда /key КЛЮЧ
@bot.message_handler(commands=["key"])
def key(message):
    [_, key] = message.text.split(" ")
    print(message.chat.id, " key = ", key)
    result = serverHome.saveKey(str.encode(key), message.chat.id)
    if result == "ok":
        bot.send_message(message.chat.id, "Ключ принят")
    else:
        bot.send_message(message.chat.id, "Ключ не принят")

# команда /getfile ИМЯ_ФАЙЛА
@bot.message_handler(commands=["getfile"])
def getf(message):
    [_, fileName] = message.text.split(" ")
    binFile = serverHome.getFile(fileName, message.chat.id)
    document = io.BytesIO(binFile)
    document.name = fileName
    files = {'document' : document}
    data = {'chat_id' : message.chat.id}
    r = requests.post('https://api.telegram.org/bot{0}/sendDocument'.format(config.token), files = files, data = data)
    print('Отправка файла:', r.status_code, r.reason, r.content)

# обычный текст
@bot.message_handler(content_types=["text"])
def sendmessage(message):
    if message.text == "Добавить ключ":
        print("OK   ",message.text)
        bot.send_message(message.chat.id, "Необходимо отправить ключ, который зарегистрирован на стороне Home")
    else:
        bot.send_message(message.chat.id, "Для получения справки необходимо отправить команду /help")
        # клавиатура с меню
        # keys = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        # keys.add("Добавить ключ")
        # bot.send_message(message.chat.id, "Ваш выбор?", reply_markup=keys)

# прием файлов
@bot.message_handler(content_types=["document"])
def sendfile(message):
    file_info = bot.get_file(message.document.file_id)
    file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(config.token, file_info.file_path))
    # file.content - binary файла
    serverHome.sendFile(message.chat.id, file.content, message.document.file_name, message.document.file_size)

if __name__ == '__main__':
    # запуск сервера
    serverHome = server.Server()
    # запуск бота
    bot.polling(none_stop=True)
