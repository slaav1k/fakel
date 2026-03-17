import asyncio
import csv
import logging
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from aiogram import Bot, Dispatcher, Router, F
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    FSInputFile,
)

import configs
from bot_secrets import TOKEN, PROXY_URL, ADMIN_PHONES

logging.basicConfig(level=getattr(logging, configs.LOG_LEVEL))

# Создаем router
router = Router()

# Память номеров телефона (chat_id → phone_number)
phone_numbers: dict[int, str] = {}

# Клавиатура
markup_phone = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Поделиться номером телефона", request_contact=True)],
        [KeyboardButton(text="Узнать свой статус")],
        [KeyboardButton(text="Привязанные номера к гаражу")],
        [KeyboardButton(text="Контакты")],
    ],
    resize_keyboard=True,
    one_time_keyboard=False,
)


# ────────────────────────────────────────────────
#   Вспомогательные функции
# ────────────────────────────────────────────────

def get_ls_boxes(phone: str) -> list[str]:
    """Возвращает список номеров гаражей/л/с по номеру телефона"""
    path = Path("numbers.csv")
    if not path.exists():
        return []

    with path.open(encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)

    found = []
    for row in rows:
        for cell in row:
            if phone in cell:
                parts = ";".join(row).split(";")
                if parts:
                    found.append(parts[0].strip())
                break
    return found


def read_row_data(search_query: str, filename: str = "example.csv") -> list[dict]:
    """
    Универсальный поиск:
    - По номеру гаража (413) → возвращает 1 результат
    - По части ФИО (Архипкин, Михаил, архип и т.д.) → может вернуть несколько результатов
    """
    path = Path(filename)
    logging.debug(f"📁 Читаем файл: {path.absolute()}")

    if not path.exists():
        logging.error(f"❌ Файл не найден: {path.absolute()}")
        return []

    try:
        with path.open(encoding="utf-8-sig") as f:
            reader = csv.reader(f, delimiter=';')
            rows = list(reader)

        if not rows:
            logging.warning("⚠️ Файл пустой")
            return []

        headers = [h.strip() for h in rows[0]]
        logging.debug(f"📋 Заголовки ({len(headers)}): {headers}")

        search_lower = search_query.lower().strip()
        results = []

        for i, row in enumerate(rows[1:], start=2):
            if not row:
                continue

            clean_row = [cell.strip() for cell in row]

            # Дополняем строку пустыми значениями, если колонок меньше
            while len(clean_row) < len(headers):
                clean_row.append("")

            # 1. Поиск по номеру гаража (колонка 0) — с очисткой
            if len(clean_row) > 0:
                garage_num = clean_row[0].strip().rstrip('.').rstrip()  # убираем точку в конце
                if search_query.strip().rstrip('.') == garage_num:
                    result = dict(zip(headers, clean_row))
                    logging.info(f"✅ Найден по номеру гаража '{search_query}' (строка {i})")
                    return [result]  # ← сразу возвращаем список с одним элементом

            # 2. Поиск по ФИО (колонка 1)
            if len(clean_row) > 1:
                fio = clean_row[1].lower()
                if search_lower in fio:
                    result = dict(zip(headers, clean_row))
                    results.append(result)
                    logging.info(f"✅ Найден по ФИО '{search_query}' → {clean_row[1]} (строка {i})")

        if results:
            logging.info(f"✅ Найдено {len(results)} совпадений по запросу '{search_query}'")
            return results

        logging.warning(f"⚠️ По запросу '{search_query}' ничего не найдено")
        return []

    except Exception as e:
        logging.exception(f"💥 Ошибка при чтении файла {filename}: {e}")
        return []


def generate_status_image(status: str, debt: str) -> Path:
    """Генерирует картинку со статусом"""
    text_image = ""
    bg_color = "white"

    if status == "Долга нет":
        text_image = "DOLGA NET"
        bg_color = "green"
    elif status == "Должен за 2026":
        text_image = f"DOLGEN ZA\n2026\nDOLG=\n={debt}"
        bg_color = "yellow"
    elif status == "Должен за 2025-2026":
        text_image = f"DOLGEN ZA\n2025\nI 2026\nDOLG=\n={debt}"
        bg_color = "orange"
    else:
        text_image = f"ZLOCSTNIY\nDOLGNIK\nDOLG=\n={debt}"
        bg_color = "red"

    image = Image.new("RGB", (800, 800), color=bg_color)
    draw = ImageDraw.Draw(image)

    # Путь к шрифту - для Windows используйте другой путь или стандартный шрифт
    # font_path = "C:/Windows/Fonts/arial.ttf"  # для Windows
    font_path = "/home/ubuntu/.local/lib/python3.6/site-packages/werkzeug/debug/shared/ubuntu.ttf"  # для Linux

    try:
        font = ImageFont.truetype(font_path, 140)
    except Exception:
        font = ImageFont.load_default()

    draw.text((10, 30), text_image, fill="black", font=font)

    out_path = Path("temp_status.png")
    image.save(out_path, "PNG")
    return out_path


# ────────────────────────────────────────────────
#   Хендлеры
# ────────────────────────────────────────────────

@router.message(Command("start"))
async def cmd_start(message: Message):
    name = message.from_user.first_name or "пользователь"
    await message.answer(
        f"Здравствуйте, {name}!\n\n"
        "Чтобы увидеть информацию о своих гаражах, поделитесь номером телефона\n\n"
        "ГСК ФАКЕЛ\nРязань, Южный Промузел, 19\n"
        "Председатель Архипкин Михаил Вячеславович\n"
        "Телефон +79109061411 +79511013775\n"
        "Администрация бота @slaav1k",
        reply_markup=markup_phone,
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer("Если что-то пошло не так — пропишите /start", reply_markup=markup_phone)


@router.message(F.contact)
async def handle_contact(message: Message):
    if not message.contact or not message.contact.phone_number:
        await message.answer("Не удалось получить номер телефона", reply_markup=markup_phone)
        return

    phone = message.contact.phone_number
    if phone.startswith("+"):
        phone = phone[1:]

    phone_numbers[message.chat.id] = phone
    logging.info(f"✅ Сохранен номер '{phone}'")
    logging.info(f"✅ Сохранен номер '{phone_numbers}'")
    await message.answer(f"Спасибо! Ваш номер сохранён: {phone}", reply_markup=markup_phone)


@router.message(F.text == "Узнать свой статус")
async def status_handler(message: Message):
    chat_id = message.chat.id
    if chat_id not in phone_numbers:
        await message.answer("Поделитесь номером телефона", reply_markup=markup_phone)
        return

    phone = phone_numbers[chat_id]
    if len(phone) != 11:
        await message.answer("Некорректный формат номера", reply_markup=markup_phone)
        return

    boxes = get_ls_boxes(phone)
    if not boxes:
        await message.answer(
            "Номер телефона не найден в базе. Обратитесь к администрации. @slaav1k",
            reply_markup=markup_phone,
        )
        return

    for box in boxes:
        data_list = read_row_data(box)  # ← теперь list

        if not data_list:
            await message.answer(f"Не удалось найти данные по гаражу {box}")
            continue

        # Берём первый (и единственный) элемент, т.к. ищем по номеру гаража
        data = data_list[0]

        text = "\n".join(f"{k} — {v}" for k, v in data.items())
        status = data.get("Должник", "Неизвестно")
        debt = data.get("Остаток долга", "—")
        garage_number = data.get("Гараж", data.get("№", box))

        await message.answer(text)

        img_path = generate_status_image(status, debt)
        await message.answer_photo(
            photo=FSInputFile(img_path),
            caption=f"Статус по гаражу {garage_number}"
        )


@router.message(F.text == "Привязанные номера к гаражу")
async def linked_phones_handler(message: Message):
    chat_id = message.chat.id
    if chat_id not in phone_numbers:
        await message.answer("Поделитесь номером телефона", reply_markup=markup_phone)
        return

    phone = phone_numbers[chat_id]
    boxes = get_ls_boxes(phone)

    if not boxes:
        await message.answer(
            "Номер телефона не найден в базе. Обратитесь к администрации. @slaav1k",
            reply_markup=markup_phone,
        )
        return

    for box in boxes:
        with open("numbers.csv", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)

            for i, sublist in enumerate(rows):
                for y, element in enumerate(sublist):
                    if box in element:
                        s = ''
                        b = ''
                        c = ''
                        for i in rows[0]:
                            b += i
                        b = b.split(';')
                        for i in sublist:
                            c += i
                        c = c.split(';')
                        for el in range(len(b)):
                            s += f'{b[el]} - {c[el]}\n'
                        print(s)
                        await message.answer(s, reply_markup=markup_phone)
                        return


@router.message(F.text == "Контакты")
async def contacts_handler(message: Message):
    await message.answer(
        "ГСК ФАКЕЛ\nРязань, Южный Промузел, 19\n"
        "Председатель Архипкин Михаил Вячеславович\n"
        "Телефон +79109061411 +79511013775\n"
        "Администрация бота @slaav1k",
        reply_markup=markup_phone,
    )


@router.message(Command("m"))
async def cmd_m(message: Message):
    chat_id = message.chat.id
    if chat_id not in phone_numbers or phone_numbers[chat_id] not in ADMIN_PHONES:
        await message.answer("Доступ запрещён", reply_markup=markup_phone)
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer(
            "Использование:\n"
            "/m 413\n"
            "/m Архипкин\n"
            "/m Михаил",
            reply_markup=markup_phone
        )
        return

    query = parts[1].strip()

    # Получаем список результатов
    data_list = read_row_data(query)

    if not data_list:
        await message.answer(f"❌ Ничего не найдено по запросу: «{query}»")
        return

    # Если нашли несколько результатов (обычно при поиске по фамилии)
    if len(data_list) > 1:
        await message.answer(f"🔍 Найдено {len(data_list)} гаражей по запросу «{query}»:")

    # Обрабатываем каждый результат
    for data in data_list:
        # Формируем текст
        text = "\n".join(f"{k} — {v}" for k, v in data.items())

        status = data.get("Должник", "Неизвестно")
        debt = data.get("Остаток долга", "—")
        garage_number = data.get("Гараж", data.get("№", "—"))

        await message.answer(text)

        # Генерируем и отправляем картинку
        img_path = generate_status_image(status, debt)
        await message.answer_photo(
            photo=FSInputFile(img_path),
            caption=f"Статус по гаражу {garage_number}"
        )


@router.message(Command("f"))
async def cmd_f(message: Message):
    chat_id = message.chat.id
    if chat_id not in phone_numbers or phone_numbers[chat_id] not in ADMIN_PHONES:
        await message.answer("Доступ запрещён", reply_markup=markup_phone)
        return

    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("Укажите номер после /f")
        return

    number = parts[-1]

    with open("numbers.csv", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)

        if not rows:
            await message.answer("❌ Файл пуст", reply_markup=markup_phone)
            return

        for i, sublist in enumerate(rows):
            for y, element in enumerate(sublist):
                if number in element:
                    s = ''
                    b = ''
                    c = ''
                    for i in rows[0]:
                        b += i
                    b = b.split(';')
                    for i in sublist:
                        c += i
                    c = c.split(';')
                    for el in range(len(b)):
                        s += f'{b[el]} - {c[el]}\n'
                    print(s)
                    await message.answer(s, reply_markup=markup_phone)
                    return

    await message.answer("Не найдено")


@router.message()
async def unknown_message(message: Message):
    await message.answer("Неизвестная команда", reply_markup=markup_phone)


# ────────────────────────────────────────────────
#   Главная функция
# ────────────────────────────────────────────────

async def main():
    session = AiohttpSession(
        proxy=PROXY_URL,
        timeout=60,
    )

    bot = Bot(token=TOKEN, session=session)

    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    dp.include_router(router)

    try:
        print("🚀 Бот запущен и работает через прокси!")
        print(f"📱 Прокси: {PROXY_URL}")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()
        print("👋 Бот остановлен")


if __name__ == "__main__":
    asyncio.run(main())
