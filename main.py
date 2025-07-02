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

def send_news(bot, chat_id):
    """Отправляет сообщение с ссылкой на Telegram-канал"""
    bot.send_text(
        chat_id=chat_id,
        text=f"📢 Актуальные новости компании доступны в нашем Telegram-канале:\n\n{TELEGRAM_CHANNEL}",
        inline_keyboard_markup=json.dumps([[
            {
                "text": "📨 Перейти в Telegram", 
                "url": TELEGRAM_CHANNEL,
                "style": "primary"
            }
        ]])
    )

def send_about(bot, chat_id):
    """Отправляет информацию о компании"""
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

def send_contacts(bot, chat_id):
    """Отправляет контактную информацию (заготовка)"""
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

def send_1c_docs(bot, chat_id):
    """Отправляет материалы по 1С (заготовка)"""
    docs_text = (
        "📚 Материалы по 1С:\n\n"
        "Здесь будет список различных материалов, ссылки на сайты, "
        "диск и документацию по 1С.\n\n"
        "⚠️ Этот раздел находится в разработке"
    )
    bot.send_text(
        chat_id=chat_id,
        text=docs_text,
        inline_keyboard_markup=json.dumps([[
            {
                "text": "Официальный сайт 1С",
                "url": "https://1c.ru",
                "style": "primary"
            },
            {
                "text": "Документация 1С",
                "url": "https://1c.ru",
                "style": "default"
            }
        ]])
    )

def send_1c_reviews(bot, chat_id):
    """Отправляет отзывы о внедрениях 1С (заготовка)"""
    reviews_text = (
        "⭐ Отзывы о наших внедрениях 1С:\n\n"
        "Здесь будут ссылки на отзывы клиентов о выполненных проектах "
        "по внедрению и сопровождению 1С.\n\n"
        "⚠️ Этот раздел находится в разработке"
    )
    bot.send_text(
        chat_id=chat_id,
        text=reviews_text,
        inline_keyboard_markup=json.dumps([[
            {
                "text": "Пример отзыва 1",
                "url": COMPANY_SITE,
                "style": "primary"
            },
            {
                "text": "Пример отзыва 2",
                "url": COMPANY_SITE,
                "style": "default"
            }
        ]])
    )

def start_support_ticket(bot, chat_id):
    """Начинает процесс создания тикета"""
    user_states[chat_id] = {"state": "awaiting_ticket_subject"}
    bot.send_text(
        chat_id=chat_id,
        text="🛠 Создание тикета поддержки\n\nПожалуйста, укажите тему обращения:"
    )

def show_my_tickets(bot, chat_id):
    """Показывает открытые тикеты пользователя (заготовка)"""
    bot.send_text(
        chat_id=chat_id,
        text="📋 Ваши открытые тикеты:\n\n"
             "1. #TKT-001 - Проблема с доступом (Создан: 01.01.2023)\n"
             "2. #TKT-002 - Вопрос по 1С (Создан: 05.01.2023)\n\n"
             "⚠️ Этот раздел находится в разработке"
    )

def close_ticket(bot, chat_id):
    """Закрывает тикет (заготовка)"""
    bot.send_text(
        chat_id=chat_id,
        text="🔒 Закрытие тикета\n\n"
             "Пожалуйста, укажите номер тикета для закрытия:\n"
             "(например: #TKT-001)\n\n"
             "⚠️ Этот раздел находится в разработке"
    )

def show_stats(bot, chat_id):
    """Показывает статистику использования бота (заготовка)"""
    bot.send_text(
        chat_id=chat_id,
        text="📊 Статистика использования бота:\n\n"
             "• Всего пользователей: 100\n"
             "• Активных сессий: 42\n"
             "• Обработано запросов: 1,234\n\n"
             "⚠️ Этот раздел находится в разработке"
    )

def start_broadcast(bot, chat_id):
    """Начинает процесс рассылки (заготовка)"""
    bot.send_text(
        chat_id=chat_id,
        text="📢 Рассылка сообщений сотрудникам\n\n"
             "Введите текст сообщения для рассылки:\n\n"
             "⚠️ Только для администраторов\n"
             "⚠️ Этот раздел находится в разработке"
    )

def message_cb(bot, event):
    text = event.text.lower().strip()
    chat_id = event.from_chat
    
    if text == "/help":
        # Полный список команд с описанием
        help_text = (
            "📋 Список всех доступных команд:\n\n"
            "🔹 Основные команды:\n"
            "/news - Последние новости компании\n"
            "/about - Информация о компании\n"
            "/contacts - Контактные данные\n\n"
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
            "Выберите действие ниже или введите команду вручную:"
        )
        
        bot.send_text(
            chat_id=chat_id,
            text=help_text,
            inline_keyboard_markup=json.dumps([[
                {"text": "Контакты", "callbackData": "contacts_cmd"},
                {"text": "Новости", "callbackData": "news_cmd"},
                {"text": "О компании", "callbackData": "about_cmd"},
                {"text": "Материалы 1С", "callbackData": "1c_docs_cmd"},
                {"text": "Отзывы 1С", "callbackData": "1c_reviews_cmd"},
                {"text": "Поддержка", "callbackData": "support_cmd"},
                {"text": "Мои тикеты", "callbackData": "my_tickets_cmd"}
            ]])
        )
    elif text == "/news":
        send_news(bot, chat_id)
    elif text == "/about":
        send_about(bot, chat_id)
    elif text == "/contacts":
        send_contacts(bot, chat_id)
    elif text == "/1c_docs":
        send_1c_docs(bot, chat_id)
    elif text == "/1c_reviews":
        send_1c_reviews(bot, chat_id)
    elif text == "/support":
        start_support_ticket(bot, chat_id)
    elif text == "/my_tickets":
        show_my_tickets(bot, chat_id)
    elif text == "/close_ticket":
        close_ticket(bot, chat_id)
    elif text == "/stats":
        show_stats(bot, chat_id)
    elif text == "/broadcast":
        start_broadcast(bot, chat_id)
    else:
        # Обработка состояний для создания тикета
        if chat_id in user_states:
            state = user_states[chat_id]["state"]
            if state == "awaiting_ticket_subject":
                user_states[chat_id] = {
                    "state": "awaiting_ticket_description",
                    "subject": text
                }
                bot.send_text(
                    chat_id=chat_id,
                    text="📝 Теперь опишите вашу проблему максимально подробно:"
                )
            elif state == "awaiting_ticket_description":
                user_states[chat_id] = {
                    "state": "awaiting_ticket_priority",
                    "description": text
                }
                bot.send_text(
                    chat_id=chat_id,
                    text="⚡ Укажите срочность:\n\n"
                         "1 - Критическая (система не работает)\n"
                         "2 - Высокая (мешает работе)\n"
                         "3 - Средняя (можно подождать)\n"
                         "4 - Низкая (вопрос/предложение)"
                )
            elif state == "awaiting_ticket_priority":
                if text in ["1", "2", "3", "4"]:
                    priority = {
                        "1": "Критическая",
                        "2": "Высокая",
                        "3": "Средняя",
                        "4": "Низкая"
                    }[text]
                    
                    # Здесь будет сохранение тикета в БД
                    ticket_id = "TKT-123"  # Заглушка
                    
                    bot.send_text(
                        chat_id=chat_id,
                        text=f"✅ Тикет #{ticket_id} создан!\n\n"
                             f"Тема: {user_states[chat_id]['subject']}\n"
                             f"Срочность: {priority}\n\n"
                             "С вами свяжутся в ближайшее время."
                    )
                    del user_states[chat_id]
                else:
                    bot.send_text(
                        chat_id=chat_id,
                        text="❌ Пожалуйста, укажите срочность цифрой от 1 до 4"
                    )
        else:
            bot.send_text(
                chat_id=chat_id,
                text="Напишите /help для вывода меню"
            )

# Обработчики кнопок
def button_news_cb(bot, event):
    if event.data['callbackData'] == "news_cmd":
        send_news(bot, event.from_chat)

def button_about_cb(bot, event):
    if event.data['callbackData'] == "about_cmd":
        send_about(bot, event.from_chat)

def button_contacts_cb(bot, event):
    if event.data['callbackData'] == "contacts_cmd":
        send_contacts(bot, event.from_chat)

def button_1c_docs_cb(bot, event):
    if event.data['callbackData'] == "1c_docs_cmd":
        send_1c_docs(bot, event.from_chat)

def button_1c_reviews_cb(bot, event):
    if event.data['callbackData'] == "1c_reviews_cmd":
        send_1c_reviews(bot, event.from_chat)

def button_support_cb(bot, event):
    if event.data['callbackData'] == "support_cmd":
        start_support_ticket(bot, event.from_chat)

def button_my_tickets_cb(bot, event):
    if event.data['callbackData'] == "my_tickets_cmd":
        show_my_tickets(bot, event.from_chat)

# Регистрация обработчиков
bot.dispatcher.add_handler(MessageHandler(callback=message_cb))
bot.dispatcher.add_handler(BotButtonCommandHandler(callback=button_news_cb))
bot.dispatcher.add_handler(BotButtonCommandHandler(callback=button_about_cb))
bot.dispatcher.add_handler(BotButtonCommandHandler(callback=button_contacts_cb))
bot.dispatcher.add_handler(BotButtonCommandHandler(callback=button_1c_docs_cb))
bot.dispatcher.add_handler(BotButtonCommandHandler(callback=button_1c_reviews_cb))
bot.dispatcher.add_handler(BotButtonCommandHandler(callback=button_support_cb))
bot.dispatcher.add_handler(BotButtonCommandHandler(callback=button_my_tickets_cb))

bot.start_polling()
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Бот остановлен")