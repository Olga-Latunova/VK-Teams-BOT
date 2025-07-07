import json
from bot.bot import Bot
from bot.handler import MessageHandler, BotButtonCommandHandler
import time
from datetime import datetime, timedelta
import threading
import pytz  # Импортируем библиотеку для работы с часовыми поясами
from dotenv import load_dotenv
import os

# Загружаем переменные из .env
load_dotenv()

TOKEN = os.getenv("VK_API_TOKEN")
TELEGRAM_CHANNEL = "https://t.me/IT_105Koderline"  # Ссылка на канал
COMPANY_SITE = "https://105.ooo"  # Сайт компании

# Устанавливаем московский часовой пояс
MOSCOW_TZ = pytz.timezone('Europe/Moscow')

bot = Bot(token=TOKEN)

# Состояния для обработки тикетов
user_states = {}
tickets = {}  # Хранение созданных тикетов {chat_id: [список тикетов]}
events = {}   # Хранение созданных событий {chat_id: [список событий]}
user_context = {}  # Хранит текущий контекст пользователя


def back_command_button(chat_id):  # Кнопка "Назад"
    bot.send_text(
        chat_id=chat_id,
        text="Выберите действие:",
        inline_keyboard_markup=json.dumps([
            [{"text": "❌ Назад", "callbackData": "user_cmd_/back", "style": "secondary"}]
        ])
    )


def start_command_buttons(chat_id):  # Главное меню
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
                {"text": "🛟 Создать тикет", "callbackData": "user_cmd_/support", "style": "primary"},
                {"text": "📋 Мои тикеты", "callbackData": "user_cmd_/my_tickets", "style": "primary"}
            ],
            [
                {"text": "🗓 Создать событие", "callbackData": "user_cmd_/create_event", "style": "primary"},
                {"text": "🗓 Мои события", "callbackData": "user_cmd_/my_events", "style": "primary"}
            ]
        ]),
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
    time.sleep(0.1)
    start_command_buttons(chat_id)


def send_news(chat_id):  # новости
    user_context[chat_id] = "news"
    time.sleep(0.3)
    bot.send_text(
        chat_id=chat_id,
        text=f"📢 Актуальные новости компании доступны в нашем Telegram-канале:\n\n{TELEGRAM_CHANNEL}",
        inline_keyboard_markup=json.dumps([[
            {"text": "📨 Перейти в Telegram", "url": TELEGRAM_CHANNEL, "style": "primary"}
        ],
        [
            {"text": "❌ Назад", "callbackData": "user_cmd_/back", "style": "secondary"}
        ]
    ]))
    time.sleep(0.1)


def send_about(chat_id):  # информация о компании
    user_context[chat_id] = "about"
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
        ],
        [
            {"text": "❌ Назад", "callbackData": "user_cmd_/back", "style": "secondary"}
        ]])
    )


def send_contacts(chat_id):  # контактная информация
    user_context[chat_id] = "contacts"
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
        ],
        [
            {"text": "❌ Назад", "callbackData": "user_cmd_/back", "style": "secondary"}
        ]])
    )


def send_1c_docs(chat_id):  # доки 1с (заготовка)
    user_context[chat_id] = "1c_docs"
    """Материалы по 1С"""
    docs_text = (
        "📚 Материалы по 1С:\n\n"
        "• Официальная документация: https://1c.ru\n"
        "• Учебные материалы: https://learning.1c.ru\n"
        "• Методические пособия: https://solutions.1c.ru"
    )
    bot.send_text(chat_id=chat_id, text=docs_text, inline_keyboard_markup=json.dumps([
            [{"text": "❌ Назад", "callbackData": "user_cmd_/back", "style": "secondary"}]
        ]))
    time.sleep(0.1)


def send_1c_reviews(chat_id):  # отзывы 1с (заготовка)
    user_context[chat_id] = "1c_reviews"
    """Отзывы о внедрениях 1С"""
    reviews_text = (
        "⭐ Отзывы о наших внедрениях 1С:\n\n"
        "1. ООО «Ромашка» - внедрение 1С:ERP\n"
        "2. АО «Василек» - переход с 1С 7.7 на 8.3\n"
        "3. ИП Петров - автоматизация торговли"
    )
    bot.send_text(chat_id=chat_id, text=reviews_text, inline_keyboard_markup=json.dumps([[
        {"text": "❌ Назад", "callbackData": "user_cmd_/back", "style": "secondary"}
    ]]))


def start_support_ticket(chat_id):
    """Начало создания тикета"""
    user_states[chat_id] = {
        "state": "awaiting_ticket_subject",
        "ticket_data": {}  # Будем хранить данные тикета здесь
    }
    bot.send_text(chat_id=chat_id, text="🛠 Создание тикета\n\nУкажите тему обращения:",
    inline_keyboard_markup=json.dumps([[
        {"text": "❌ Назад", "callbackData": "user_cmd_/back", "style": "secondary"}
    ]]))

def process_ticket_creation(chat_id, message_text):
    """Обработка шагов создания тикета"""
    if user_states.get(chat_id, {}).get("state") == "awaiting_ticket_subject":
        user_states[chat_id]["ticket_data"]["subject"] = message_text
        user_states[chat_id]["state"] = "awaiting_ticket_description"
        bot.send_text(chat_id=chat_id, text="📝 Теперь опишите проблему подробно:",inline_keyboard_markup=json.dumps([[
                {"text": "⬅️ Назад", "callbackData": "user_cmd_/back_in_ticket"},
                {"text": "❌ Отмена", "callbackData": "user_cmd_/cancel"}
            ]]))
    
    elif user_states.get(chat_id, {}).get("state") == "awaiting_ticket_description":
        user_states[chat_id]["ticket_data"]["description"] = message_text
        user_states[chat_id]["state"] = "awaiting_ticket_deadline"
        bot.send_text(
            chat_id=chat_id,
            text="⏰ Укажите дедлайн для задачи (в формате ДД.ММ.ГГГГ, например 31.12.2023):", inline_keyboard_markup=json.dumps([[
                {"text": "⬅️ Назад", "callbackData": "user_cmd_/back_in_ticket"},
                {"text": "❌ Отмена", "callbackData": "user_cmd_/cancel"}
            ]])
        )
    
    elif user_states.get(chat_id, {}).get("state") == "awaiting_ticket_deadline":
        try:
            deadline = datetime.strptime(message_text, "%d.%m.%Y").date()
            user_states[chat_id]["ticket_data"]["deadline"] = deadline.strftime("%d.%m.%Y")
            
            # Сохраняем тикет
            if chat_id not in tickets:
                tickets[chat_id] = []
            
            ticket_id = f"TKT-{len(tickets[chat_id])+1:03d}"
            ticket_data = user_states[chat_id]["ticket_data"]
            ticket_data["id"] = ticket_id
            ticket_data["status"] = "Открыт"
            ticket_data["created_at"] = datetime.now(MOSCOW_TZ).strftime("%d.%m.%Y %H:%M")
            
            tickets[chat_id].append(ticket_data)
            
            # Формируем сообщение с информацией о тикете
            ticket_info = (
                f"✅ Тикет создан!\n\n"
                f"🔹 Номер: {ticket_id}\n"
                f"🔹 Тема: {ticket_data['subject']}\n"
                f"🔹 Описание: {ticket_data['description']}\n"
                f"🔹 Дедлайн: {ticket_data['deadline']}\n"
                f"🔹 Статус: {ticket_data['status']}\n"
                f"🔹 Создан: {ticket_data['created_at']}"
            )
            
            bot.send_text(chat_id=chat_id, text=ticket_info, inline_keyboard_markup=json.dumps([[
        {"text": "⬅️ В главное меню", "callbackData": "user_cmd_/back", "style": "secondary"}
    ]]) )
            user_states.pop(chat_id, None)  # Удаляем состояние
            time.sleep(0.5)
            
        except ValueError:
            bot.send_text(
                chat_id=chat_id,
                text="❌ Неверный формат даты. Пожалуйста, укажите дату в формате ДД.ММ.ГГГГ:"
            )
    


def show_my_tickets(chat_id):
    """Показывает тикеты пользователя с возможностью закрытия"""
    if chat_id not in tickets or not tickets[chat_id]:
        bot.send_text(chat_id=chat_id, text="У вас нет активных тикетов.")
        return

    keyboard = []
    for ticket in tickets[chat_id]:
        ticket_id = ticket["id"]
        subject = ticket["subject"]
        status = ticket["status"]
        deadline = ticket["deadline"]

        row = [{
            "text": f"{ticket_id} - {subject} ({status}, до {deadline})",
            "callbackData": f"user_cmd_view_ticket_{ticket_id}"  # Убрали /
        }]
        if status == "Открыт":
            row.append({
                "text": "❌ Закрыть",
                "callbackData": f"user_cmd_confirm_close_ticket_{ticket_id}"  # Убрали /
            })
        keyboard.append(row)

    bot.send_text(
        chat_id=chat_id,
        text="📋 Ваши тикеты:",
        inline_keyboard_markup=json.dumps(keyboard)
    )

def close_ticket(chat_id):
    """Выводит список тикетов для закрытия"""
    if chat_id not in tickets or not tickets[chat_id]:
        bot.send_text(chat_id=chat_id, text="❌ У вас нет активных тикетов.")
        return

    keyboard = []
    for ticket in tickets[chat_id]:
        if ticket["status"] == "Открыт":
            ticket_id = ticket["id"]
            keyboard.append([{
                "text": f"❌ Закрыть #{ticket_id}",
                "callbackData": f"user_cmd_/confirm_close_ticket_{ticket_id}"
            }])

    if not keyboard:
        bot.send_text(chat_id=chat_id, text="❌ Нет тикетов для закрытия.")
        return

    bot.send_text(
        chat_id=chat_id,
        text="🗑 Выберите тикет для закрытия:",
        inline_keyboard_markup=json.dumps(keyboard)
    )

def start_create_event(chat_id):
    """Начало создания события"""
    user_states[chat_id] = {
        "state": "awaiting_event_name",
        "event_data": {}
    }
    bot.send_text(
        chat_id=chat_id,
        text="🗓 Создание события\n\nУкажите название события:",
        inline_keyboard_markup=json.dumps([[
            {"text": "❌ Отмена", "callbackData": "user_cmd_/cancel"},
            {"text": "⬅️ Назад", "callbackData": "user_cmd_/back_in_event"}
        ]])
    )

def go_back_in_event(chat_id):
    if chat_id in user_states:
        state_info = user_states[chat_id]
        state = state_info["state"]

        if state == "awaiting_event_description":
            name = state_info["event_data"].get("name", "")
            bot.send_text(chat_id=chat_id, text=f"🗓 Измените название события:\n(было: {name})",inline_keyboard_markup=json.dumps([[
                {"text": "⬅️ Назад", "callbackData": "user_cmd_/back_in_event"},
                {"text": "❌ Отмена", "callbackData": "user_cmd_/cancel"}
            ]]))
            state_info["state"] = "awaiting_event_name"

        elif state == "awaiting_event_datetime":
            name = state_info["event_data"].get("name", "")
            description = state_info["event_data"].get("description", "")
            bot.send_text(
                chat_id=chat_id,
                text=f"🗓 Название: {name}\n📝 Описание: {description}\n\nИзмените описание события:",
                inline_keyboard_markup=json.dumps([[
                    {"text": "⬅️ Назад", "callbackData": "user_cmd_/back_in_event"},
                    {"text": "❌ Отмена", "callbackData": "user_cmd_/cancel"}
                ]])
            )
            state_info["state"] = "awaiting_event_description"

        else:
            # Если нечего откатывать, просто выводим меню
            bot.send_text(chat_id=chat_id, text="⬅️ Вы вернулись в главное меню.")
            start_command_buttons(chat_id)

    else:
        # Обычный возврат из других разделов
        current_context = user_context.get(chat_id)
        if current_context:
            del user_context[chat_id]
            bot.send_text(chat_id=chat_id, text="⬅️ Вы вернулись в главное меню.")
            start_command_buttons(chat_id)
        else:
            start_command_buttons(chat_id)

def process_event_creation(chat_id, message_text):
    """Обработка шагов создания события"""
    if user_states.get(chat_id, {}).get("state") == "awaiting_event_name":
        user_states[chat_id]["event_data"]["name"] = message_text
        user_states[chat_id]["state"] = "awaiting_event_description"
        bot.send_text(
            chat_id=chat_id,
            text="📝 Теперь опишите событие подробно:",
            inline_keyboard_markup=json.dumps([[
                {"text": "⬅️ Назад", "callbackData": "user_cmd_/back_in_event"},
                {"text": "❌ Отмена", "callbackData": "user_cmd_/cancel"}
            ]])
        )
    
    elif user_states.get(chat_id, {}).get("state") == "awaiting_event_description":
        user_states[chat_id]["event_data"]["description"] = message_text
        user_states[chat_id]["state"] = "awaiting_event_datetime"
        bot.send_text(
            chat_id=chat_id,
            text="⏰ Укажите дату и время события (в формате ДД.ММ.ГГГГ ЧЧ:ММ):",
            inline_keyboard_markup=json.dumps([[
                {"text": "⬅️ Назад", "callbackData": "user_cmd_/back_in_event"},
                {"text": "❌ Отмена", "callbackData": "user_cmd_/cancel"}
            ]])
        )
    
    elif user_states.get(chat_id, {}).get("state") == "awaiting_event_datetime":
        try:
            # Преобразуем введенное время с учетом московского часового пояса
            naive_datetime = datetime.strptime(message_text, "%d.%m.%Y %H:%M")
            event_datetime = MOSCOW_TZ.localize(naive_datetime)
            
            user_states[chat_id]["event_data"]["datetime"] = event_datetime
            
            # Сохраняем событие
            if chat_id not in events:
                events[chat_id] = []
            
            event_id = f"EVT-{len(events[chat_id])+1:03d}"
            event_data = user_states[chat_id]["event_data"]
            event_data["id"] = event_id
            event_data["status"] = "Запланировано"
            event_data["created_at"] = datetime.now(MOSCOW_TZ).strftime("%d.%m.%Y %H:%M")
            
            events[chat_id].append(event_data)
            
            # Формируем сообщение с информацией о событии
            event_info = (
                f"✅ Событие создано!\n\n"
                f"🔹 Номер: {event_id}\n"
                f"🔹 Название: {event_data['name']}\n"
                f"🔹 Описание: {event_data['description']}\n"
                f"🔹 Дата и время: {event_datetime.strftime('%d.%m.%Y %H:%M')}\n"
                f"🔹 Статус: {event_data['status']}\n"
                f"🔹 Создано: {event_data['created_at']}\n\n"
                f"Я напомню вам за 10 минут до начала!"
            )
            
            bot.send_text(chat_id=chat_id, text=event_info)
            user_states.pop(chat_id, None)  # Удаляем состояние
            
            # Запускаем напоминание
            reminder_time = event_datetime - timedelta(minutes=10)
            threading.Thread(
                target=schedule_reminder,
                args=(chat_id, event_id, event_data['name'], reminder_time),
                daemon=True
            ).start()
            
            time.sleep(0.5)
            
        except ValueError:
            bot.send_text(
                chat_id=chat_id,
                text="❌ Неверный формат даты и времени. Пожалуйста, укажите в формате ДД.ММ.ГГГГ ЧЧ:ММ:"
            )

def schedule_reminder(chat_id, event_id, event_name, reminder_time):
    """Запланировать напоминание о событии"""
    now = datetime.now(MOSCOW_TZ)
    delay = (reminder_time - now).total_seconds()
    
    if delay > 0:
        time.sleep(delay)
        bot.send_text(
            chat_id=chat_id,
            text=f"🔔 Напоминание о событии!\n\n"
                 f"Через 10 минут начинается:\n"
                 f"*{event_name}*\n\n"
                 f"ID события: {event_id}", inline_keyboard_markup=json.dumps([[
        {"text": "❌ Назад", "callbackData": "user_cmd_/back", "style": "secondary"}
    ]]))

def show_my_events(chat_id):
    """Показывает события пользователя"""
    if chat_id not in events or not events[chat_id]:
        bot.send_text(chat_id=chat_id, text="У вас нет запланированных событий.", inline_keyboard_markup=json.dumps([[
        {"text": "❌ Назад", "callbackData": "user_cmd_/back", "style": "secondary"}
        ]]))
        return
    
    events_text = "🗓 Ваши предстоящие события:\n\n"
    for i, event in enumerate(events[chat_id], 1):
        # Форматируем время с учетом часового пояса
        event_time = event['datetime'].astimezone(MOSCOW_TZ)
        events_text += (
            f"{i}. #{event['id']}\n"
            f"   Название: {event['name']}\n"
            f"   Время: {event_time.strftime('%d.%m.%Y %H:%M')}\n"
            f"   Статус: {event['status']}\n\n"
        )
    
    bot.send_text(chat_id=chat_id, text=events_text, inline_keyboard_markup=json.dumps([[
        {"text": "❌ Назад", "callbackData": "user_cmd_/back", "style": "secondary"}
        ]])
    )

def show_help(chat_id):
    user_context[chat_id] = "help"
    help_text = (
        "📋 Список всех доступных команд:\n\n"
        "🔹 Основные команды:\n"
        "/news - Последние новости компании\n"
        "/about - Информация о компании\n"
        "/contacts - Контактные данные\n"
        "/cancel - Прервать текущий диалог\n"
        "/back - Вернуться на шаг назад\n\n"
        "🔹 1С материалы:\n"
        "/1c_docs - Документация и материалы по 1С\n"
        "/1c_reviews - Отзывы о наших внедрениях 1С\n\n"
        "🔹 Поддержка:\n"
        "/support - Создать новый тикет\n"
        "/my_tickets - Просмотреть мои тикеты\n"
        # "/back_in_tickets - Вернуться назад (в окне тикетов)\n"
        "/close_ticket - Закрыть тикет\n\n"
        "🔹 События:\n"
        "/create_event - Создать новое событие\n"
        "/my_events - Посмотреть мои события\n"
        # "/back_in_event - Вернуться назад (в окне событий)\n\n"
        "🔹 Администрирование:\n"
        "/stats - Статистика использования бота\n"
        "/broadcast - Рассылка сообщений (админы)\n\n"
        "Воспользуйтесь кнопками или введите команду вручную"
    )
    bot.send_text(chat_id=chat_id, text=help_text, inline_keyboard_markup=json.dumps([
            [{"text": "❌ Назад", "callbackData": "user_cmd_/back", "style": "secondary"}]
        ]))


def cancel_current_dialog(chat_id):
    if chat_id in user_states:
        del user_states[chat_id]  # Полностью очищаем состояние
    bot.send_text(chat_id=chat_id, text="❌ Вы вышли из текущего диалога.", inline_keyboard_markup=json.dumps([
            [{"text": "❌ Назад", "callbackData": "user_cmd_/back", "style": "secondary"}]
        ]))


def go_back(chat_id):
    if chat_id in user_states:
        state_info = user_states[chat_id]
        state = state_info["state"]

        # Возвращаемся к предыдущему шагу
        if state == "awaiting_ticket_description":
            bot.send_text(chat_id=chat_id, text="🛠 Измените тему обращения:",inline_keyboard_markup=json.dumps([[
                {"text": "⬅️ Назад", "callbackData": "user_cmd_/back_in_event"},
                {"text": "❌ Отмена", "callbackData": "user_cmd_/cancel"}
            ]]))
            state_info["state"] = "awaiting_ticket_subject"

        elif state == "awaiting_ticket_deadline":
            subject = state_info["ticket_data"].get("subject", "")
            description = state_info["ticket_data"].get("description", "")

            bot.send_text(
                chat_id=chat_id,
                text=f"🛠 Тема: {subject}\n📝 Описание: {description}\n\nИзмените описание обращения:"
            ,inline_keyboard_markup=json.dumps([[
                {"text": "⬅️ Назад", "callbackData": "user_cmd_/back_in_event"},
                {"text": "❌ Отмена", "callbackData": "user_cmd_/cancel"}
            ]]))
            state_info["state"] = "awaiting_ticket_description"

        else:
            # Если нечего откатывать, просто выводим меню
            bot.send_text(chat_id=chat_id, text="⬅️ Вы вернулись в главное меню.")
            start_command_buttons(chat_id)

    else:
        # Обычный возврат из других разделов
        current_context = user_context.get(chat_id)
        if current_context:
            del user_context[chat_id]
            bot.send_text(chat_id=chat_id, text="⬅️ Вы вернулись в главное меню.")
            start_command_buttons(chat_id)
        else:
            start_command_buttons(chat_id)


def process_command(chat_id, command):  # обрабатывает все команды
    command = command.lower().strip()
    if command == "/start":
        send_welcome(chat_id)
    elif command == "/help":
        show_help(chat_id)
    elif command == "/cancel":
        cancel_current_dialog(chat_id)
    elif command == "/back":
        go_back(chat_id)
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
    elif command == "/close_ticket":
        bot.send_text(chat_id=chat_id, text="Введите ID тикета, который вы хотите закрыть:")
        # Устанавливаем состояние пользователя в "ожидание ID тикета для закрытия"
        user_states[chat_id] = {"state": "awaiting_ticket_id_to_close"}
    elif command == "/create_event":
        start_create_event(chat_id)
    elif command == "/my_events":
        show_my_events(chat_id)
    elif command == "/back":
        go_back(chat_id)
    elif command == "/back_in_ticket":
        if chat_id in user_states:
            go_back(chat_id)
        else:
            start_command_buttons(chat_id)
    elif command == "/back_in_event":
        go_back_in_event(chat_id)
    else:
        bot.send_text(chat_id=chat_id, text="Неизвестная команда. Введите /help")


def simulate_user_message(chat_id, text): #команда от пользователя
    time.sleep(0.3)
    bot.send_text(
        chat_id=chat_id,
        text=f"Вы выбрали команду: {text}"
    )
    time.sleep(0.3)
    process_command(chat_id, text)


def message_cb(bot, event):
    chat_id = event.from_chat
    text = event.text

    state = user_states.get(chat_id, {}).get("state", "")

    # === Обработка закрытия тикета по ID ===
    if state == "awaiting_ticket_id_to_close":
        ticket_id = text.strip()  # Получаем ID тикета, введенный пользователем
        ticket_found = False

        if chat_id in tickets:
            for ticket in tickets[chat_id]:
                if ticket["id"] == ticket_id and ticket["status"] == "Открыт":
                    ticket_found = True
                    # Запрашиваем подтверждение закрытия тикета
                    bot.send_text(
                        chat_id=chat_id,
                        text=f"Вы уверены, что хотите закрыть тикет #{ticket_id}?",
                        inline_keyboard_markup=json.dumps([
                            [
                                {"text": "✅ Да", "callbackData": f"user_cmd_confirm_close_ticket_{ticket_id}"},
                                {"text": "❌ Нет", "callbackData": "user_cmd_/cancel"}
                            ]
                        ])
                    )
                    # Очищаем состояние пользователя
                    del user_states[chat_id]
                    break

        if not ticket_found:
            bot.send_text(chat_id=chat_id, text="❌ Тикет с таким ID не найден или уже закрыт.")
            del user_states[chat_id]  # Очищаем состояние пользователя

    # === Обработка создания тикета ===
    elif state.startswith("awaiting_ticket"):
        process_ticket_creation(chat_id, text)

    # === Обработка создания события ===
    elif state.startswith("awaiting_event"):
        process_event_creation(chat_id, text)

    # === Если состояние не определено, обрабатываем как обычную команду ===
    else:
        process_command(chat_id, text)


def button_cb(bot, event):
    try:
        bot.answer_callback_query(
            query_id=event.data['queryId'],
            text="⌛ Обработка..."
        )
        time.sleep(0.3)

        if event.data['callbackData'].startswith('user_cmd_'):
            chat_id = event.from_chat
            callback_data = event.data['callbackData'][9:]  # Убираем префикс user_cmd_

            # 🔒 Обработка закрытия тикета
            if callback_data.startswith("confirm_close_ticket_"):
                ticket_id = callback_data.replace("confirm_close_ticket_", "")
                ticket_found = False

                for idx, ticket in enumerate(tickets.get(chat_id, [])):
                    if ticket["id"] == ticket_id and ticket["status"] == "Открыт":
                        ticket["status"] = "Закрыт"
                        ticket["closed_at"] = datetime.now(MOSCOW_TZ).strftime("%d.%m.%Y %H:%M")
                        bot.send_text(chat_id=chat_id, text=f"✅ Тикет #{ticket_id} успешно закрыт.")
                        ticket_found = True
                        break

                if not ticket_found:
                    bot.send_text(chat_id=chat_id, text="❌ Не удалось найти открытый тикет.")

                show_my_tickets(chat_id)

            # ℹ Просмотр информации о тикете
            elif callback_data.startswith("view_ticket_"):
                ticket_id = callback_data.replace("view_ticket_", "")
                found = False
                for ticket in tickets.get(chat_id, []):
                    if ticket["id"] == ticket_id:
                        info = (
                            f"🔹 Номер: {ticket['id']}\n"
                            f"🔹 Тема: {ticket['subject']}\n"
                            f"🔹 Описание: {ticket['description']}\n"
                            f"🔹 Дедлайн: {ticket['deadline']}\n"
                            f"🔹 Статус: {ticket['status']}\n"
                            f"🔹 Создан: {ticket['created_at']}\n"
                            f"🔹 Закрыт: {ticket.get('closed_at', '—')}"
                        )
                        bot.send_text(chat_id=chat_id, text=f"ℹ️ Информация о тикете:\n\n{info}")
                        found = True
                        break
                if not found:
                    bot.send_text(chat_id=chat_id, text="❌ Тикет не найден.")

            # 🔄 Все остальные команды обрабатываются через process_command
            else:
                process_command(chat_id, callback_data)

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
