import json
from bot.bot import Bot
from bot.handler import MessageHandler, BotButtonCommandHandler
import time

TOKEN = "001.1806729577.0340071044:1011814127"  # ваш токен
TELEGRAM_CHANNEL = "https://t.me/IT_105Koderline"  # Ссылка на канал
COMPANY_SITE = "https://105.ooo"  # Сайт компании

bot = Bot(token=TOKEN)

# Состояния для обработки тикетов
user_states = {}


def start_command_buttons(chat_id):  # сообщение с кнопками для действий
    bot.send_text(
        chat_id=chat_id,
        text="Выберите действие ниже:",
        inline_keyboard_markup=json.dumps([
            [
                {"text": "📞 Контакты", "callbackData": "user_cmd_/contacts", "style": "primary"},
                {"text": "📰 Новости", "callbackData": "user_cmd_/news", "style": "primary"},
                {"text": "🏢 О компании", "callbackData": "user_cmd_/about", "style": "primary"}
            ],
            [
                {"text": "📚 1С Документы", "callbackData": "user_cmd_/1c_docs", "style": "primary"},
                {"text": "⭐ 1С Отзывы", "callbackData": "user_cmd_/1c_reviews", "style": "primary"}
            ],
            [
                {"text": "🛟 Поддержка", "callbackData": "user_cmd_/support", "style": "primary"},
                {"text": "📋 Мои тикеты", "callbackData": "user_cmd_/my_tickets", "style": "primary"}
            ]
        ])
    )


def send_welcome(chat_id):  # приветственное сообщение при /start
    welcome_text = (
        "👋 Добро пожаловать в бот компании «105 Кодерлайн»!\n\n"
        "Я ваш виртуальный помощник. Вот что я могу:\n"
        "• Предоставить информацию о компании\n"
        "• Показать новости и обновления\n"
        "• Помочь с документацией 1С\n"
        "• Создать тикет в поддержку\n\n"
        "Выберите действие кнопками ниже или введите /help для списка команд."
    )
    bot.send_text(chat_id=chat_id, text=welcome_text)
    time.sleep(0.5)
    start_command_buttons(chat_id)


def send_news(chat_id):  # новости
    time.sleep(0.3)
    bot.send_text(
        chat_id=chat_id,
        text=f"📢 Актуальные новости компании доступны в нашем Telegram-канале:\n\n{TELEGRAM_CHANNEL}",
        inline_keyboard_markup=json.dumps([[
            {"text": "📨 Перейти в Telegram", "url": TELEGRAM_CHANNEL, "style": "primary"}
        ]])
    )
    time.sleep(0.5)
    start_command_buttons(chat_id)


def send_about(chat_id):  # информация о компании
    time.sleep(0.3)
    about_text = (
        "🏢 Компания «105 Кодерлайн» работает в Российском центре программирования "
        "ОЭЗ ТВТ «Дубна» как представительство «Кодерлайн», партнер фирмы 1С, "
        "а также мы и резиденты особой экономической зоны технико-внедренческого типа «Дубна».\n\n"
        f"🌐 Подробнее: {COMPANY_SITE}"
    )
    bot.send_text(
        chat_id=chat_id,
        text=about_text,
        inline_keyboard_markup=json.dumps([[
            {
                "text": "Перейти на сайт",
                "url": COMPANY_SITE,
                "style": "primary"
            }
        ]])
    )
    time.sleep(0.5)
    start_command_buttons(chat_id)


def send_contacts(chat_id):  # контактная информация
    time.sleep(0.3)
    contacts_text = (
        "📞 Контактная информация:\n\n"
        "Здесь будет информация о контактах поддержки, отделах, "
        "добавочных номерах и почтах сотрудников.\n\n"
        "⚠️ Этот раздел находится в разработке"
    )
    bot.send_text(
        chat_id=chat_id,
        text=contacts_text,
        inline_keyboard_markup=json.dumps([[
            {
                "text": "Перейти на сайт",
                "url": COMPANY_SITE,
                "style": "primary"
            }
        ]])
    )
    time.sleep(0.5)
    start_command_buttons(chat_id)


def send_1c_docs(chat_id):  # доки 1с (заготовка)
    """Материалы по 1С"""
    docs_text = (
        "📚 Материалы по 1С:\n\n"
        "• Официальная документация: https://1c.ru\n"
        "• Учебные материалы: https://learning.1c.ru\n"
        "• Методические пособия: https://solutions.1c.ru"
    )
    bot.send_text(chat_id=chat_id, text=docs_text)


def send_1c_reviews(chat_id):  # отзывы 1с (заготовка)
    """Отзывы о внедрениях 1С"""
    reviews_text = (
        "⭐ Отзывы о наших внедрениях 1С:\n\n"
        "1. ООО «Ромашка» - внедрение 1С:ERP\n"
        "2. АО «Василек» - переход с 1С 7.7 на 8.3\n"
        "3. ИП Петров - автоматизация торговли"
    )
    bot.send_text(chat_id=chat_id, text=reviews_text)


def start_support_ticket(chat_id):
    """Начало создания тикета"""
    user_states[chat_id] = {"state": "awaiting_ticket_subject"}
    bot.send_text(chat_id=chat_id, text="🛠 Создание тикета\n\nУкажите тему обращения:")


def show_my_tickets(chat_id):
    """Показывает тикеты пользователя"""
    bot.send_text(
        chat_id=chat_id,
        text="📋 Ваши открытые тикеты:\n\n"
             "1. #TKT-001 - Проблема с доступом (в работе)\n"
             "2. #TKT-002 - Вопрос по 1С (ожидает ответа)"
    )


def process_command(chat_id, command):  # обрабатывает все команды
    command = command.lower().strip()
    if command == "/start":
        send_welcome(chat_id)
    elif command == "/help":
        help_text = (
            "📋 Список всех доступных команд:\n\n"
            "🔹 Основные команды:\n"
            "/news - Последние новости компании\n"
            "/about - Информация о компании\n"
            "/contacts - Контактные данные\n"
            "/cancel - Прервать текущий диалог\n\n"
            "🔹 1С материалы:\n"
            "/1c_docs - Документация и материалы по 1С\n"
            "/1c_reviews - Отзывы о наших внедрениях 1С\n\n"
            "🔹 Поддержка:\n"
            "/support - Создать новый тикет\n"
            "/my_tickets - Просмотреть мои тикеты\n"
            "/close_ticket - Закрыть тикет\n\n"
            "🔹 Администрирование:\n"
            "/stats - Статистика использования бота\n"
            "/broadcast - Рассылка сообщений (админы)\n\n"
            "Воспользуйтесь кнопками или введите команду вручную"
        )
        bot.send_text(chat_id=chat_id, text=help_text)
        start_command_buttons(chat_id)

    elif command == "/news":
        send_news(chat_id)
    elif command == "/about":
        send_about(chat_id)
    elif command == "/contacts":
        send_contacts(chat_id)
    elif command == "/1c_docs":
        send_1c_docs(chat_id)
    elif command == "/1c_reviews":
        send_1c_reviews(chat_id)
    elif command == "/support":
        start_support_ticket(chat_id)
    elif command == "/my_tickets":
        show_my_tickets(chat_id)
    elif command == "/cancel":
        if chat_id in user_states:
            del user_states[chat_id]  # Очищаем состояние
        bot.send_text(chat_id=chat_id, text="❌ Вы вышли из текущего диалога.")
        start_command_buttons(chat_id)
    else:
        bot.send_text(chat_id=chat_id, text="Неизвестная команда. Введите /help")


def simulate_user_message(chat_id, text):  # команда от пользователя
    time.sleep(0.3)
    bot.send_text(
        chat_id=chat_id,
        text=f"Вы выбрали команду: {text}"
    )
    time.sleep(0.3)
    process_command(chat_id, text)


def message_cb(bot, event):  # обработчик сообщений
    process_command(event.from_chat, event.text)


def button_cb(bot, event):  # обработчки кнопок
    try:
        # Подтверждаем получение callback
        bot.answer_callback_query(
            query_id=event.data['queryId'],
            text="⌛ Обработка..."
        )
        time.sleep(0.3)
        if event.data['callbackData'].startswith('user_cmd_'):
            command = event.data['callbackData'][9:]  # Убираем префикс user_cmd_
            simulate_user_message(event.from_chat, command)
    except Exception as e:
        print(f"Ошибка обработки кнопки: {e}")
        bot.answer_callback_query(
            query_id=event.data.get('queryId', ''),
            text="❌ Ошибка обработки"
        )


# Регистрация обработчиков
bot.dispatcher.add_handler(MessageHandler(callback=message_cb))
bot.dispatcher.add_handler(BotButtonCommandHandler(callback=button_cb))

# Запуск бота
print("Бот запущен...")
bot.start_polling()
bot.idle()
