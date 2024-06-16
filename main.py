import csv
import telebot
from PIL import Image, ImageDraw, ImageFont
from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import CommandHandler
from telegram.ext import Updater, MessageHandler, Filters

from tok import TOKEN

tb = telebot.TeleBot(TOKEN)

phone_numbers = {}

markup_phone = ReplyKeyboardMarkup(
    [
        [KeyboardButton("Поделиться номером телефона", request_contact=True)],
        [KeyboardButton("Узнать свой статус")],
        [KeyboardButton('Привязанные номера к гаражу')],
        [KeyboardButton('Контакты')]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)


def __get_ls_boxes(number_phone):
    number = number_phone
    with open('numbers.csv', 'r', encoding="utf-8") as File:
        a = []
        reader = csv.reader(File)
        for row in reader:
            a.append(row)
    ls_boxes = []
    for i, sublist in enumerate(a):
        for y, element in enumerate(sublist):
            if number in element:
                c = ''
                for i in sublist:
                    c += i
                c = c.split(';')
                ls_boxes.append(c[0])
    return ls_boxes


def message_handler(update, context):
    text = update.message.text
    if text == "Узнать свой статус":
        chat_id = update.message.chat_id
        if chat_id in phone_numbers and len("79109052030") == len(phone_numbers[chat_id]):
            phone_num = phone_numbers[chat_id]
            ls_boxes = __get_ls_boxes(phone_num)

            if len(ls_boxes) > 0:
                for number in ls_boxes:
                    with open('example.csv', 'r', encoding="utf-8") as File:
                        a = []
                        reader = csv.reader(File)
                        for row in reader:
                            a.append(row)
                    for i, sublist in enumerate(a):
                        for y, element in enumerate(sublist):
                            if number in element:
                                s = ''
                                b = ''
                                c = ''
                                for i in a[0]:
                                    b += i
                                b = b.split(';')
                                for i in sublist:
                                    c += i
                                c = c.split(';')
                                ostatok_dolga = ''
                                status_dolgnika = ''
                                for el in range(len(b)):
                                    if b[el] == 'Остаток долга':
                                        ostatok_dolga = c[el]
                                    if b[el] == 'Должник':
                                        status_dolgnika = c[el]
                                    s += f'{b[el]} - {c[el]}\n'
                                print(s)
                                print(status_dolgnika + " " + ostatok_dolga)
                                text_image = ''
                                color_text = 'white'
                                if status_dolgnika == 'Долга нет':
                                    text_image = 'DOLGA NET'
                                    color_text = 'green'
                                elif status_dolgnika == 'Должен за 2024':
                                    text_image = f"DOLGEN ZA\n2024\nDOLG=\n={ostatok_dolga}"
                                    color_text = 'yellow'
                                elif status_dolgnika == 'Должен за 2023-2024':
                                    text_image = f"DOLGEN ZA\n2023\nI 2024\nDOLG=\n={ostatok_dolga}"
                                    color_text = 'orange'
                                else:
                                    text_image = f"ZLOCSTNIY\nDOLGNIK\nDOLG=\n={ostatok_dolga}"
                                    color_text = 'red'

                                image = Image.new('RGB', (800, 800), color=color_text)
                                draw = ImageDraw.Draw(image)
                                p_font = "/home/ubuntu/.local/lib/python3.6/site-packages/werkzeug/debug/shared/ubuntu.ttf"
                                font = ImageFont.truetype(p_font, 140)
                                # font = ImageFont.load_default()
                                draw.text((10, 30), text_image, fill='black', font=font)
                                update.message.reply_text(f'{s}')
                                tb.send_photo(update.message.chat_id, image)
            else:
                update.message.reply_text(f'Номер телефона не найден в базе. Обратитесь к администрации. @slaav1k',
                                          reply_markup=markup_phone)
        else:
            update.message.reply_text(f'Поделитесь Вашим номером телефона', reply_markup=markup_phone)
    elif text == 'Привязанные номера к гаражу':
        chat_id = update.message.chat_id

        if chat_id in phone_numbers and len("79109052030") == len(phone_numbers[chat_id]):
            phone_num = phone_numbers[chat_id]
            ls_boxes = __get_ls_boxes(phone_num)

            if len(ls_boxes) > 0:
                for number in ls_boxes:
                    with open('numbers.csv', 'r', encoding="utf-8") as File:
                        a = []
                        reader = csv.reader(File)
                        for row in reader:
                            a.append(row)
                    for i, sublist in enumerate(a):
                        for y, element in enumerate(sublist):
                            if number in element:
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
                                update.message.reply_text(f'{s}')
            else:
                update.message.reply_text(f'Номер телефона не найден в базе. Обратитесь к администрации. @slaav1k',
                                          reply_markup=markup_phone)
        else:
            update.message.reply_text(f'Поделитесь Вашим номером телефона', reply_markup=markup_phone)
    elif text == "Контакты":
        update.message.reply_text(
            f'ГСК ФАКЕЛ\nРязань, Южный Промузел, 19\nПредседатель Архипкин Михаил Вячеславович\nТелефон +79109061411 +79511013775\nАдминистрация бота @slaav1k',
            reply_markup=markup_phone)
    else:
        update.message.reply_text("Неизвестная команда", reply_markup=markup_phone)


def m(update, context):
    chat_id = update.message.chat_id
    if chat_id in phone_numbers and (phone_numbers[chat_id] == "79106114058" or phone_numbers[chat_id] == "79109061411"):
        number = update.message.text.split()[-1]
        with open('example.csv', 'r', encoding="utf-8") as File:
            a = []
            reader = csv.reader(File)
            for row in reader:
                a.append(row)
        for i, sublist in enumerate(a):
            for y, element in enumerate(sublist):
                if number in element:
                    s = ''
                    b = ''
                    c = ''
                    for i in a[0]:
                        b += i
                    b = b.split(';')
                    for i in sublist:
                        c += i
                    c = c.split(';')
                    ostatok_dolga = ''
                    status_dolgnika = ''
                    for el in range(len(b)):
                        if b[el] == 'Остаток долга':
                            ostatok_dolga = c[el]
                        if b[el] == 'Должник':
                            status_dolgnika = c[el]
                        s += f'{b[el]} - {c[el]}\n'
                    print(s)
                    print(status_dolgnika + " " + ostatok_dolga)
                    text_image = ''
                    color_text = 'white'
                    if status_dolgnika == 'Долга нет':
                        text_image = 'DOLGA NET'
                        color_text = 'green'
                    elif status_dolgnika == 'Должен за 2024':
                        text_image = f"DOLGEN ZA\n2024\nDOLG=\n={ostatok_dolga}"
                        color_text = 'yellow'
                    elif status_dolgnika == 'Должен за 2023-2024':
                        text_image = f"DOLGEN ZA\n2023\nI 2024\nDOLG=\n={ostatok_dolga}"
                        color_text = 'orange'
                    else:
                        text_image = f"ZLOCSTNIY\nDOLGNIK\nDOLG=\n={ostatok_dolga}"
                        color_text = 'red'

                    image = Image.new('RGB', (800, 800), color=color_text)
                    draw = ImageDraw.Draw(image)
                    p_font = "/home/ubuntu/.local/lib/python3.6/site-packages/werkzeug/debug/shared/ubuntu.ttf"
                    font = ImageFont.truetype(p_font, 140)
                    # font = ImageFont.load_default()
                    draw.text((10, 30), text_image, fill='black', font=font)
                    update.message.reply_text(f'{s}')
                    tb.send_photo(update.message.chat_id, image)
    else:
        update.message.reply_text(f'Поделитесь Вашим номером телефона', reply_markup=markup_phone)


def f(update, context):
    chat_id = update.message.chat_id
    if phone_numbers[chat_id] == "79106114058" or phone_numbers[chat_id] == "79109061411":
        number = update.message.text.split()[-1]
        with open('numbers.csv', 'r', encoding="utf-8") as File:
            a = []
            reader = csv.reader(File)
            for row in reader:
                a.append(row)
        for i, sublist in enumerate(a):
            for y, element in enumerate(sublist):
                if number in element:
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
                    update.message.reply_text(f'{s}')
    else:
        update.message.reply_text(f'Поделитесь Вашим номером телефона', reply_markup=markup_phone)


def help(update, context):
    update.message.reply_text(
        "Если что-то пошло не так пропишите /start.", reply_markup=markup_phone)


def start(update, context):
    name = update.effective_user["first_name"]
    print(name)
    update.message.reply_text(
        f"Здравствуйте, {name}. \n"
        f"\nЧтоб увидеть информацию о своих гаражах, сперва поделитесь номером телфона\n\n"
        f'ГСК ФАКЕЛ\nРязань, Южный Промузел, 19\nПредседатель Архипкин Михаил Вячеславович\nТелефон +79109061411 +79511013775\nАдминистрация бота @slaav1k',
        reply_markup=markup_phone)


def phone_number_handler(update, context):
    chat_id = update.message.chat_id
    phone_number = update.message.contact.phone_number
    if phone_number[0] == "+":
        phone_number = phone_number[1:]
    phone_numbers[chat_id] = phone_number
    print(f"Номер телефона для чата {chat_id}: {phone_number}")
    update.message.reply_text(f"Спасибо за предоставленный номер телефона: {phone_number}", reply_markup=markup_phone)
    print(phone_numbers)


def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    updater.start_polling()
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("m", m))
    dp.add_handler(CommandHandler("f", f))
    dp.add_handler(MessageHandler(Filters.contact, phone_number_handler))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, message_handler))

    updater.idle()  # не комититься


if __name__ == '__main__':
    main()
