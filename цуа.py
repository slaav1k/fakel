import datetime
import random

from tok import TOKEN
from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CallbackContext, CommandHandler
from telegram.ext import CommandHandler
from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove

due = 0
reply_keyboard = [['/dice'],
                  ['/timer']]
reply_dice = [['/k1x6'], ['/k2x6'], ['/k1x20'], ['/back']]
reply_time = [['/set_time 30'], ['/set_time 60'], ['/set_time 300'], ['/back']]
reply_close_timer = [['/close']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
markup2 = ReplyKeyboardMarkup(reply_dice, one_time_keyboard=False)
markup3 = ReplyKeyboardMarkup(reply_time, one_time_keyboard=False)
markup4 = ReplyKeyboardMarkup(reply_close_timer, one_time_keyboard=False)


def remove_job_if_exists(name, context):
    """Удаляем задачу по имени.
    Возвращаем True если задача была успешно удалена."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


# Обычный обработчик, как и те, которыми мы пользовались раньше.
def set_timer(update, context):
    """Добавляем задачу в очередь"""
    chat_id = update.message.chat_id
    try:
        # args[0] должен содержать значение аргумента
        # (секунды таймера)
        global due
        due = int(context.args[0])
        if due < 0:
            update.message.reply_text(
                'Извините, не умеем возвращаться в прошлое')
            return

        # Добавляем задачу в очередь
        # и останавливаем предыдущую (если она была)
        job_removed = remove_job_if_exists(
            str(chat_id),
            context
        )
        context.job_queue.run_once(
            task,
            due,
            context=chat_id,
            name=str(chat_id)
        )
        text = f'Засек {due} секунд!'
        if job_removed:
            text += ' Старая задача удалена.'
        # Присылаем сообщение о том, что всё получилось.
        update.message.reply_text(text, reply_markup=markup4)

    except (IndexError, ValueError):
        update.message.reply_text('Использование: /set_time <секунд>')


def task(context):
    global due
    """Выводит сообщение"""
    job = context.job
    context.bot.send_message(job.context, text=f'Истекло {due} секунд!', reply_markup=markup3)


def unset_timer(update, context):
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = 'Хорошо, таймер сброшен!' if job_removed else 'Нет активного таймера.'
    update.message.reply_text(text, reply_markup=markup3)


def dice(update, context):
    update.message.reply_text('Делайте бросок.', reply_markup=markup2)


def timer(update, context):
    update.message.reply_text('На сколько засекаем?', reply_markup=markup3)


def k1x6(update, context):
    chislo = random.randint(1, 6)
    update.message.reply_text(
        f"{chislo}")


def k2x6(update, context):
    chislo = random.randint(1, 6)
    update.message.reply_text(
        f"{chislo} : {random.randint(1, 6)}")


def k1x20(update, context):
    chislo = random.randint(1, 20)
    update.message.reply_text(
        f"{chislo}")


def help(update, context):
    update.message.reply_text(
        "Я пока не умею помогать... Я только ваше эхо.")


def phone(update, context):
    update.message.reply_text("Телефон: +7(495)776-3030")


def site(update, context):
    update.message.reply_text(
        "Сайт: http://www.yandex.ru/company")


def time(update, context):
    today = datetime.datetime.today()
    update.message.reply_text(
        today.strftime("%H:%M:%S"))


def date(update, context):
    today = datetime.datetime.today()
    update.message.reply_text(
        today.strftime("%m/%d/%Y"))


def start(update, context):
    update.message.reply_text(
        "Я бот-помощник. Какая помощь вам нужна?",
        reply_markup=markup
    )


def close_keyboard(update, context):
    update.message.reply_text(
        "Ok",
        reply_markup=ReplyKeyboardRemove()
    )


def main():
    updater = Updater(TOKEN, use_context=True)

    # Получаем из него диспетчер сообщений.
    dp = updater.dispatcher

    updater.start_polling()
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("back", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("timer", timer))
    dp.add_handler(CommandHandler("date", date))
    dp.add_handler(CommandHandler("dice", dice))
    dp.add_handler(CommandHandler("k1x6", k1x6))
    dp.add_handler(CommandHandler("k2x6", k2x6))
    dp.add_handler(CommandHandler("k1x20", k1x20))
    dp.add_handler(CommandHandler("phone", phone))
    dp.add_handler(CommandHandler("site", site))
    dp.add_handler(CommandHandler("close", unset_timer))
    dp.add_handler(CommandHandler("close_keyboard", close_keyboard))
    dp.add_handler(CommandHandler("set_time", set_timer,
                                  pass_args=True,
                                  pass_job_queue=True,
                                  pass_chat_data=True))
    dp.add_handler(CommandHandler("unset", unset_timer,
                                  pass_chat_data=True))

    # Ждём завершения приложения.
    # (например, получения сигнала SIG_TERM при нажатии клавиш Ctrl+C)
    updater.idle()


# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    main()
