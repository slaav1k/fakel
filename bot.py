import csv
import datetime
import random
import telebot
from tok import TOKEN
from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CallbackContext, CommandHandler
from telegram.ext import CommandHandler
from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove
from translate import Translator
import requests

tb = telebot.TeleBot(TOKEN)
due = 0
flag = 0
total = 0
user = ''
s = []
reply_keyboard = [['/info']]
communication = [['/c'], ['/x'], ['/m'], ['/back']]
main_answer = [['/yes'], ['/no']]
reply_close_timer = [['/close']]
choicer = [['/1'], ['/2'], ['/3'], ['/4'], ['/main_window']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
markup_choice = ReplyKeyboardMarkup(choicer, one_time_keyboard=False, resize_keyboard=True)
markup2 = ReplyKeyboardMarkup(communication, one_time_keyboard=False)
markup3 = ReplyKeyboardMarkup(main_answer, one_time_keyboard=False)
markup4 = ReplyKeyboardMarkup(reply_close_timer, one_time_keyboard=False)


def info(update, context):
    global s
    with open("dolgi.txt", "r", encoding='utf-8') as file:
        s = file.readlines()
        print(s)
        text_info = ''
        for i in s:
            if "ДА" in i:
                text_info += i
        print(text_info)
    update.message.reply_text(f'{text_info}', reply_markup=markup2)


def x(update, context):
    global s
    with open("dolgi.txt", "r", encoding='utf-8') as file:
        s = file.readlines()
    text = update.message.text.split()
    number, dolg = text[-2], text[-1]
    print(number)
    print(dolg)
    with open("dolgi.txt", "w", encoding="utf-8") as file:
        for i in s:
            if number in i:
                i = i.split()[0:-1]
                i.append(dolg)
                i = " ".join(i)
                update.message.reply_text(f'{i}')
                file.write(i + '\n')
            else:
                file.write(i)


def c(update, context):
    global s
    with open("dolgi.txt", "r", encoding='utf-8') as file:
        s = file.readlines()
    number = update.message.text.split()[-1]
    print(number)
    for i in s:
        print(i)
        if number in i:
            update.message.reply_text(f'{i}')


def m(update, context):
    with open('example.csv', 'r', encoding="utf-8") as File:
        a = []
        reader = csv.reader(File)
        for row in reader:
            a.append(row)
    for i, sublist in enumerate(a):
        for y, element in enumerate(sublist):
            if '002.' in element:
                s = ''
                b = ''
                c = ''
                for i in a[0]:
                    b += i
                b = b.split(';')
                for i in sublist:
                    c += i
                c = c.split(';')
                for el in range(len(b)):
                    s += f'{b[el]} - {c[el]}\n'
                print(s)


def help(update, context):
    update.message.reply_text(
        "Если что-то пошло не так пропишите или нажмите /start.")


def start(update, context):
    name = update.effective_user["first_name"]
    print(name)
    update.message.reply_text(
        f"Здравствуйте, {name}. \n"
        f"/c [номер гаража] узнать статус долга \n"
        f"/x [номер гаража] [статус долга] установить(изменить) статус долга \n"
        f"/m [номер гаража] посмотреть финансовый отчет",
        reply_markup=markup
    )


def menu(update, context):
    name = update.effective_user["first_name"]
    print(name)
    update.message.reply_text(
        f"Здравствуйте, {name}. \n"
        f"/c [номер гаража] узнать статус долга \n"
        f"/x [номер гаража] [статус долга] установить(изменить) статус долга \n"
        f"/m [номер гаража] посмотреть финансовый отчет",
        reply_markup=markup
    )


def close_keyboard(update, context):
    update.message.reply_text(
        "Ok",
        reply_markup=ReplyKeyboardRemove()
    )


def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    updater.start_polling()
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("back", menu))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("x", x))
    dp.add_handler(CommandHandler("info", info))
    dp.add_handler(CommandHandler("c", c))
    dp.add_handler(CommandHandler("m", m))
    dp.add_handler(CommandHandler("no", menu))
    dp.add_handler(CommandHandler("main_window", menu))
    dp.add_handler(CommandHandler("close_keyboard", close_keyboard))
    updater.idle()  # не комититься


if __name__ == '__main__':
    main()
