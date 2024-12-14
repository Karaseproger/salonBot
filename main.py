import json
import telebot
from telebot import types
import re

bot = telebot.TeleBot("7773881896:AAExm_dQkhep5XSRBBnREntGMQF_snOM7l0")

# Загрузка переводов
with open("translations.json", "r", encoding="utf-8") as f:
    translations = json.load(f)

# Доступные языки
LANGUAGES = {
    "Русский": "ru",
    "Қазақша": "каз"
}

# Админы
adminKirill = {5411263922}
adminAyazgan = {1051472692}

# Хранение данных пользователей
user_languages = {}
user_data = {}
available_times = []  # Доступные временные окна (заполняется админами)

# Состояния пользователя
USER_STATES = {
    'WAITING_FOR_NAME': 'waiting_for_name',
    'WAITING_FOR_PHONE': 'waiting_for_phone',
    'WAITING_FOR_SERVICE': 'waiting_for_service',
    'WAITING_FOR_SUBSERVICE': 'waiting_for_subservice',
    'WAITING_FOR_OPTIONS': 'waiting_for_options',
    'WAITING_FOR_MASTER': 'waiting_for_master',
    'WAITING_FOR_TIME': 'waiting_for_time',
    'DONE': 'done'
}

# Услуги и их подкатегории
services = {
    'Ногти': ['Маникюр', 'Коррекция', 'Наращивание'],
    'Ресницы': ['Наращивание', 'Ламинирование'],
    'Волосы': ['Стрижка', 'Окрашивание', 'Укладка'],
    'Шугаринг': ['Зона лица', 'Зона тела']
}

# Дополнительные параметры для всех услуг
service_options = {
    'Ремонт': ['Да', 'Нет'],
    'Снятие': ['Да', 'Нет'],
    'Уровень дизайна': ['Сложный', 'Средний', 'Лёгкий']
}

# Список мастеров и их описаний
masters = {
    'Кирилл': "Кирилл — опытный мастер маникюра с 5-летним стажем. Специализируется на сложных дизайнах.",
    'Аяжан': "Айазган — мастер ресниц и волос с 7-летним стажем. Подходит для всех типов работ."
}

masterss ={"Кирилл.", "Аяжан."}


def get_translation(lang_code, key):
    """Получить перевод строки."""
    return translations.get(lang_code, translations["ru"]).get(key, f"[{key}]")


def is_valid_phone(phone_number):
    """Проверка валидности номера телефона."""
    pattern = r'^\+7\d{10}$'
    return re.match(pattern, phone_number) is not None


@bot.message_handler(commands=["start"])
def start(message):
    """Начало работы бота."""
    chat_id = message.chat.id
    user_languages[chat_id] = "ru"
    user_data[chat_id] = {}

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.row(*LANGUAGES.keys())

    bot.send_message(chat_id, get_translation("ru", "choose_language"), reply_markup=markup)


@bot.message_handler(func=lambda msg: msg.text in LANGUAGES.keys())
def set_language(message):
    """Выбор языка."""
    chat_id = message.chat.id
    selected_lang = LANGUAGES[message.text]
    user_languages[chat_id] = selected_lang

    # Приветственное сообщение с кнопками "Записаться" и "Информация о мастерах"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.row(get_translation(selected_lang, "book_appointment"), get_translation(selected_lang, "about_masters"))
    bot.send_message(chat_id, get_translation(selected_lang, "greeting"), reply_markup=markup)


@bot.message_handler(func=lambda msg: msg.text == get_translation(user_languages.get(msg.chat.id, "ru"), "about_masters"))
def about_masters(message):
    """Информация о мастерах."""
    chat_id = message.chat.id
    lang_code = user_languages.get(chat_id, "ru")

    # Отправляем список мастеров
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = [types.KeyboardButton(master) for master in masters.keys()]
    markup.add(*buttons)
    bot.send_message(chat_id, get_translation(lang_code, "choose_master_info"), reply_markup=markup)


@bot.message_handler(func=lambda msg: msg.text in masters.keys())
def master_info(message):
    """Описание мастера (только для секции 'Информация о мастерах')."""
    chat_id = message.chat.id
    lang_code = user_languages.get(chat_id, "ru")

    # Отправляем описание мастера
    bot.send_message(chat_id, masters[message.text])

    # Возвращаем пользователя к выбору
    bot.send_message(chat_id, get_translation(lang_code, "choose_master_info"))


@bot.message_handler(func=lambda msg: msg.text == get_translation(user_languages.get(msg.chat.id, "ru"), "book_appointment"))
def book_appointment(message):
    """Начало записи на услугу."""
    chat_id = message.chat.id
    lang_code = user_languages.get(chat_id, "ru")
    user_data[chat_id]['state'] = USER_STATES['WAITING_FOR_NAME']

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = [types.KeyboardButton(service) for service in services.keys()]
    markup.add(*buttons)
    bot.send_message(chat_id, get_translation(lang_code, "name"), reply_markup=markup)


@bot.message_handler(func=lambda msg: user_data.get(msg.chat.id, {}).get('state') == USER_STATES['WAITING_FOR_NAME'])
def get_name(message):
    """Получение имени пользователя."""
    chat_id = message.chat.id
    lang_code = user_languages.get(chat_id, "ru")
    user_data[chat_id]['name'] = message.text
    user_data[chat_id]['state'] = USER_STATES['WAITING_FOR_PHONE']
    bot.send_message(chat_id, get_translation(lang_code, "sayphon"))


@bot.message_handler(func=lambda msg: user_data.get(msg.chat.id, {}).get('state') == USER_STATES['WAITING_FOR_PHONE'])
def get_phone(message):
    """Получение номера телефона."""
    chat_id = message.chat.id
    lang_code = user_languages.get(chat_id, "ru")
    phone_number = message.text

    if is_valid_phone(phone_number):
        user_data[chat_id]['phone'] = phone_number
        user_data[chat_id]['state'] = USER_STATES['WAITING_FOR_SERVICE']
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        buttons = [types.KeyboardButton(service) for service in services.keys()]
        markup.add(*buttons)
        bot.send_message(chat_id, get_translation(lang_code, "uslug"), reply_markup=markup)
    else:
        bot.send_message(chat_id, get_translation(lang_code, "nopthone"))



@bot.message_handler(func=lambda msg: user_data.get(msg.chat.id, {}).get('state') == USER_STATES['WAITING_FOR_SERVICE'])
def get_service(message):
    """Получение услуги."""
    chat_id = message.chat.id
    lang_code = user_languages.get(chat_id, "ru")
    selected_service = message.text

    if selected_service in services:
        # Записываем услугу в user_data и обновляем состояние
        user_data[chat_id]['service'] = selected_service
        user_data[chat_id]['state'] = USER_STATES['WAITING_FOR_SUBSERVICE']

        # Создаём кнопки для подкатегорий услуги
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        buttons = [types.KeyboardButton(subservice) for subservice in services[selected_service]]
        markup.add(*buttons)

        bot.send_message(chat_id, get_translation(lang_code, "subservice"), reply_markup=markup)
    else:
        # Если выбрана недопустимая услуга
        bot.send_message(chat_id, get_translation(lang_code, "wrong_service"))


@bot.message_handler(func=lambda msg: user_data.get(msg.chat.id, {}).get('state') == USER_STATES['WAITING_FOR_SUBSERVICE'])
def get_subservice(message):
    """Получение подкатегории услуги."""
    chat_id = message.chat.id
    lang_code = user_languages.get(chat_id, "ru")
    selected_subservice = message.text

    # Проверяем, что подкатегория услуги корректна
    if selected_subservice in services[user_data[chat_id]['service']]:
        user_data[chat_id]['subservice'] = selected_subservice
        user_data[chat_id]['state'] = USER_STATES['WAITING_FOR_OPTIONS']

        # Создаём кнопки для выбора дополнительных параметров
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        buttons = [types.KeyboardButton(option) for option in service_options.keys()]
        markup.add(*buttons)

        bot.send_message(chat_id, get_translation(lang_code, "choose_option"), reply_markup=markup)
    else:
        # Если выбрана недопустимая подкатегория
        bot.send_message(chat_id, get_translation(lang_code, "wrong_subservice"))



@bot.message_handler(func=lambda msg: user_data.get(msg.chat.id, {}).get('state') == USER_STATES['WAITING_FOR_OPTIONS'])
def get_options(message):
    """Получение дополнительных параметров."""
    chat_id = message.chat.id
    lang_code = user_languages.get(chat_id, "ru")
    selected_option = message.text

    if selected_option in service_options:
        user_data[chat_id].setdefault('options', {})[selected_option] = selected_option

        # Если все параметры выбраны, переход к выбору мастера
        if len(user_data[chat_id]['options']) == len(service_options):
            user_data[chat_id]['state'] = USER_STATES['WAITING_FOR_MASTER']

            # Показать доступных мастеров
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            buttons = [types.KeyboardButton(master) for master in masterss]
            markup.add(*buttons)
            bot.send_message(chat_id, get_translation(lang_code, "choose_master"), reply_markup=markup)
        else:
            bot.send_message(chat_id, get_translation(lang_code, "continue_options"))
    else:
        bot.send_message(chat_id, get_translation(lang_code, "wrong_option"))


@bot.message_handler(func=lambda msg: user_data.get(msg.chat.id, {}).get('state') == USER_STATES['WAITING_FOR_MASTER'])
def get_master(message):
    """Выбор мастера."""
    chat_id = message.chat.id
    lang_code = user_languages.get(chat_id, "ru")
    selected_master = message.text

    if selected_master in masterss:
        user_data[chat_id]['master'] = selected_master
        user_data[chat_id]['state'] = USER_STATES['WAITING_FOR_TIME']

        # Показать доступные временные окна
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        buttons = [types.KeyboardButton(time) for time in available_times]
        markup.add(*buttons)
        bot.send_message(chat_id, get_translation(lang_code, "choose_time"), reply_markup=markup)
    else:
        bot.send_message(chat_id, get_translation(lang_code, "wrong_master"))


@bot.message_handler(func=lambda msg: user_data.get(msg.chat.id, {}).get('state') == USER_STATES['WAITING_FOR_TIME'])
def select_time(message):
    """Выбор времени записи."""
    chat_id = message.chat.id
    lang_code = user_languages.get(chat_id, "ru")
    selected_time = message.text

    if selected_time in available_times:
        user_data[chat_id]['time'] = selected_time
        user_data[chat_id]['state'] = USER_STATES['DONE']

        # Формируем сообщение заявки
        request_message = (
            f"Имя: {user_data[chat_id]['name']}\n"
            f"Телефон: {user_data[chat_id]['phone']}\n"
            f"Услуга: {user_data[chat_id]['service']}\n"
            f"Подкатегория: {user_data[chat_id]['subservice']}\n"
            f"Опции: {', '.join(user_data[chat_id]['options'].values())}\n"
            f"Мастер: {user_data[chat_id]['master']}\n"
            f"Время: {user_data[chat_id]['time']}"
        )

        # Отправляем админам
        for admin_id in adminKirill.union(adminAyazgan):
            bot.send_message(admin_id, request_message)

        # Подтверждение пользователю
        bot.send_message(chat_id, get_translation(lang_code, "request_sent"))
    else:
        bot.send_message(chat_id, get_translation(lang_code, "wrong_time"))


@bot.message_handler(commands=["add_time"])
def add_time(message):
    """Добавление времени записи (только для админов)."""
    chat_id = message.chat.id
    if chat_id not in adminKirill and chat_id not in adminAyazgan:
        bot.reply_to(message, "У вас нет прав для выполнения этой команды.")
        return

    # Ожидание ввода времени
    bot.reply_to(message, "Введите время записи (через запятую, например: 10:00, 11:00, 12:00):")
    bot.register_next_step_handler(message, save_times)


def save_times(message):
    """Сохраняем временные окна."""
    chat_id = message.chat.id
    times = message.text.split(',')
    global available_times
    available_times.extend([time.strip() for time in times])
    bot.reply_to(message, f"Время добавлено: {', '.join(times)}")


if __name__ == "__main__":
    bot.polling(none_stop=True)
