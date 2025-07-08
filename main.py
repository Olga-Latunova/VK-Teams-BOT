import json
from bot.bot import Bot
from bot.handler import MessageHandler, BotButtonCommandHandler
import time
from datetime import datetime, timedelta
import threading
import pytz  # библиотека для работы с часовыми поясами
import re

TOKEN = "001.1806729577.0340071044:1011814127"  # токен бота

#Ссылки и контакты
TELEGRAM_CHANNEL = "https://t.me/IT_105Koderline"  # Ссылка на канал
COMPANY_SITE = "https://105.ooo"  # Сайт компании
CONTACTS = (
        "📞 Контактная информация компании «105 Кодерлайн»:\n\n"
        "<b>Руководство</b>\n"
        "• <b>Оводков Василий</b> - генеральный директор\n"
        "  Согласования по любым вопросам\n"
        "  vovodkov@koderline.com | вн. номер 105\n\n"
        
        "• <b>Иванова Елена</b> - финансовый директор\n"
        "  Взаиморасчеты с сотрудниками, руководитель проектов\n"
        "  eivanova@koderline.com | вн. номер 501\n\n"
        
        "<b>Отдел кадров</b>\n"
        "• <b>Рык Наталья</b> - директор по персоналу\n"
        "  Приём, адаптация, перевод и увольнение сотрудников\n"
        "  nryk@koderline.com | вн. номер 502\n\n"
        
        "<b>ИТ отдел</b>\n"
        "• <b>Малинин Алексей</b> - системный администратор\n"
        "  IP телефония, техническое обеспечение\n"
        "  avmalinin@koderline.com | вн. номер 100\n\n"
        
        "• <b>Абросимов Артём</b> - администратор сети и СРМ\n"
        "  Учётные записи, инструкции пользователя\n"
        "  aabrosimov@koderline.com\n\n"
        
        "<b>Отдел продаж</b>\n"
        "• <b>Кожемяк Максим</b> - и.о. руководителя отдела продаж\n"
        "  Взаимодействие с менеджерами по продажам\n"
        "  mkozhemyak@koderline.com | вн. номер 508"
    ) #контакты
REVIEWS = "https://1c.ru/solutions/public/" #отзывы
DOCS_VIDEO = "https://disk.yandex.ru/d/OTc3jOmE1Vf2Gg" #видеоматериалы для менеджеров
DOCS_TEXT = "https://disk.yandex.ru/d/VZC9ueCQYMGX2Q" #инструкции для менеджеров (текстовый формат)

# Устанавливаем московский часовой пояс
MOSCOW_TZ = pytz.timezone('Europe/Moscow')

bot = Bot(token=TOKEN)

# Состояния для обработки тикетов
user_states = {}
tickets = {}  # Хранение созданных тикетов {chat_id: [список тикетов]}
events = {}   # Хранение созданных событий {chat_id: [список событий]}
user_context = {}  # Хранит текущий контекст пользователя
#admin_users = set()  # Множество пользователей с админскими правами
active_chats = set()  # Множество активных чатов с ботом
user_tickets = {}  # Хранение тикетов пользователей {chat_id: [ticket_ids]}
admin_tickets = {}  # Хранение тикетов администраторов {chat_id: [ticket_ids]}
adm_password = str(105) # Пароль администратора
admin_users = {
    "a.kalinin@bot-60.bizml.ru": "Калинин Артур",
    "o.latunova@bot-60.bizml.ru": "Латунова Ольга",
    "vovodkov@koderline.com": "Оводков Василий",
    "eivanova@koderline.com": "Иванова Елена",
    "nryk@koderline.com": "Рык Наталья",
    "avmalinin@koderline.com": "Малинин Алексей",
    "aabrosimov@koderline.com": "Абросимов Артём",
    "mkozhemyak@koderline.com": "Кожемяк Максим"
}  # Словарь администраторов {email: имя}
#"o.latunova@bot-60.bizml.ru": "Латунова Ольга",
# Глобальный счетчик тикетов
ticket_counter = 1

#общие кнопки для всех состояний
back_button = {"text": "⬅️ Назад", "callbackData": "user_cmd_/back"} #кнопка "назад"
menu_button = {"text": "Меню", "callbackData": "user_cmd_/back", "style": "secondary"} #кнопка "меню"
cancel_button = {"text": "❌ Отмена", "callbackData": "user_cmd_/cancel"} #кнопка "отмена"

#время задержки ответа (симуляция обработки запроса)
processing_time = time.sleep(0.2)

def generate_ticket_id(): #генерация идентификатора тикета
    global ticket_counter
    ticket_id = f"TKT-{ticket_counter:04d}"
    ticket_counter += 1
    return ticket_id

def start_command_buttons(chat_id):  # Главное меню
    # Если пользователь админ, показываем дополнительные кнопки
    if chat_id in admin_users:
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
                ],
                [
                    {"text": "🛠 Администраторам", "callbackData": "user_cmd_/admin_panel", "style": "attention"}
                ]
            ]),
        )
    else:
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

def receiving_admin_access(chat_id, message_text): #получение администраторских прав с помощью пароля (а надо ли?...)
    if message_text.strip() == adm_password:
        admin_users.add(chat_id)
        bot.send_text(
            chat_id=chat_id,
            text="🔓 Вы получили админские права!",
        )
        start_command_buttons(chat_id)
        return True
    return False

def check_admin_access(chat_id): #получение администраторских прав
    if chat_id in admin_users:
        return True
    return False

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
    processing_time
    start_command_buttons(chat_id)

def send_news(chat_id):  # новости
    user_context[chat_id] = "news"
    processing_time
    bot.send_text(
        chat_id=chat_id,
        text=f"📢 Актуальные новости компании доступны в нашем Telegram-канале:\n\n{TELEGRAM_CHANNEL}",
        inline_keyboard_markup=json.dumps([[{"text": "📨 Перейти в Telegram", "url": TELEGRAM_CHANNEL, "style": "primary"}],
        [back_button]
    ]))
    processing_time

def send_about(chat_id):  # информация о компании
    user_context[chat_id] = "about"
    processing_time
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
        [back_button]])
    )

def send_contacts(chat_id):  # контактная информация
    user_context[chat_id] = "contacts"
    processing_time
    bot.send_text(
        chat_id=chat_id,
        text=CONTACTS,
        parse_mode="HTML",
        inline_keyboard_markup=json.dumps([
            [
                {
                    "text": "🌐 Перейти на сайт",
                    "url": COMPANY_SITE,
                    "style": "primary"
                }
            ],
            [back_button]
        ])
    )
    processing_time
    start_command_buttons(chat_id)

def send_1c_docs(chat_id):  #доки 1с
    user_context[chat_id] = "1c_docs"
    docs_text = (
        "📚 Материалы по 1С:\n\n"
        f"• Обучающие видеоматериалы для менеджера по продажам - {DOCS_VIDEO}\n"
        f"• Инструкции в текстовом формате для менеджера по продажам - {DOCS_TEXT}"
    )
    processing_time
    bot.send_text(chat_id=chat_id, text=docs_text, inline_keyboard_markup=json.dumps([[back_button]]))

def send_1c_reviews(chat_id):  #отзывы 1С
    user_context[chat_id] = "1c_reviews"
    reviews_text = f"⭐ Отзывы о наших внедрениях 1С:\n\n{REVIEWS}"
    processing_time
    bot.send_text(
        chat_id=chat_id,
        text=reviews_text,
        inline_keyboard_markup=json.dumps([
            [{   "text": "Перейти к отзывам", "url": REVIEWS, "style": "primary"}],
            [back_button]
        ])
    )

def start_support_ticket(chat_id): #создание тикета
  user_states[chat_id] = {
        "state": "awaiting_ticket_subject",
        "ticket_data": {
            "creator": chat_id,
            "assigned_to": None
        }
    }
  processing_time
  bot.send_text(chat_id=chat_id, text="🛠 Создание тикета\n\nУкажите тему обращения:",
        inline_keyboard_markup=json.dumps([[back_button]]))

def process_ticket_creation(chat_id, message_text): #обработка и сохранение тикета
    state = user_states.get(chat_id, {}).get("state")
    ticket_data = user_states.get(chat_id, {}).get("ticket_data", {})
    
    if state == "awaiting_ticket_subject":
        ticket_data["subject"] = message_text
        user_states[chat_id]["state"] = "awaiting_ticket_description"
        processing_time
        bot.send_text(chat_id=chat_id, text="📝 Теперь опишите проблему подробно:", 
                     inline_keyboard_markup=json.dumps([[back_button, cancel_button]]))
    
    elif state == "awaiting_ticket_description":
        ticket_data["description"] = message_text
        user_states[chat_id]["state"] = "awaiting_ticket_deadline"
        processing_time
        bot.send_text(
            chat_id=chat_id,
            text="⏰ Укажите дедлайн для задачи (в формате ДД.ММ.ГГГГ, например 31.12.2023):", 
            inline_keyboard_markup=json.dumps([[back_button, cancel_button]])
        )
    
    elif state == "awaiting_ticket_deadline":
        try:
            deadline = datetime.strptime(message_text, "%d.%m.%Y").date()
            ticket_data["deadline"] = deadline.strftime("%d.%m.%Y")
            user_states[chat_id]["state"] = "awaiting_ticket_admin"
        
        # Формируем список администраторов для выбора
            admin_buttons = []
        
        # Добавляем кнопку "Назначить себе" для ВСЕХ пользователей
            admin_buttons.append({
                "text": "👤 Назначить себе", 
                "callbackData": "assign_ticket_self"
            })
                           
        # Добавляем остальных администраторов
            for email, name in admin_users.items():
                 if email != chat_id:  # Исключаем текущего пользователя из списка, если он админ
                    admin_buttons.append({
                        "text": f"👤 {name}",
                        "callbackData": f"assign_ticket_{email}"
                })
                    
        # Разбиваем кнопки по 2 в ряд
            keyboard = [admin_buttons[i:i + 2] for i in range(0, len(admin_buttons), 2)]
            keyboard.append([back_button, cancel_button])
        
            processing_time
            bot.send_text(
                chat_id=chat_id,
                text="👥 Выберите, кому назначить тикет:",
                inline_keyboard_markup=json.dumps(keyboard)
            )
        
        except ValueError:
            processing_time
            bot.send_text(
                chat_id=chat_id,
                text="❌ Неверный формат даты. Пожалуйста, укажите дату в формате ДД.ММ.ГГГГ:"
            )

def assign_ticket(chat_id, admin_id):
        # Проверяем наличие данных тикета
    if chat_id not in user_states:
        bot.send_text(chat_id=chat_id, text="❌ Ошибка: данные тикета не найдены")
        return
    
    ticket_data = user_states[chat_id]["ticket_data"]
    
    # Обрабатываем назначение
    if admin_id == "self":
        # Назначение себе
        ticket_data.update({
            "ticket_type": "personal",
            "assigned_to": chat_id,
            "assigned_to_name": "Себе"
        })
    else:
        # Назначение администратору
        ticket_data.update({
            "ticket_type": "assigned",
            "assigned_to": admin_id,
            "assigned_to_name": admin_users.get(admin_id, "Администратору")
        })
    
    # Создаем тикет
    ticket_id = generate_ticket_id()
    ticket_data.update({
        "id": ticket_id,
        "status": "Открыт",
        "created_at": datetime.now(MOSCOW_TZ).strftime("%d.%m.%Y %H:%M")
    })
    
    # Сохраняем тикет
    tickets[ticket_id] = ticket_data
    
    # Добавляем в список тикетов создателя
    if ticket_data["creator"] not in user_tickets:
        user_tickets[ticket_data["creator"]] = []
    user_tickets[ticket_data["creator"]].append(ticket_id)
    
    # Если назначено админу - добавляем в его список
    if ticket_data["ticket_type"] == "assigned":
        if admin_id not in admin_tickets:
            admin_tickets[admin_id] = []
        admin_tickets[admin_id].append(ticket_id)
        
        # Уведомляем администратора (если он онлайн)
        try:
            bot.send_text(
                chat_id=admin_id,  # Здесь предполагается, что admin_id - это chat_id
                text=(
                    f"🔔 Вам назначен новый тикет!\n\n"
                    f"🔹 Номер: {ticket_id}\n"
                    f"🔹 От: {chat_id}\n"
                    f"🔹 Тема: {ticket_data['subject']}\n"
                    f"🔹 Дедлайн: {ticket_data['deadline']}\n\n"
                    f"📝 Описание:\n{ticket_data['description']}"
                ),
                inline_keyboard_markup=json.dumps([
                    [
                        {"text": "🛠 Посмотреть", "callbackData": f"view_ticket_{ticket_id}"},
                        {"text": "✅ Закрыть", "callbackData": f"admin_cmd_close_ticket_{ticket_id}"}
                    ]
                ])
            )
        except Exception as e:
            print(f"Ошибка при отправке уведомления администратору: {e}")
    
    # Формируем единое сообщение с информацией о тикете
    ticket_info = (
        f"✅ Тикет успешно создан!\n\n"
        f"🔹 Номер: {ticket_id}\n"
        f"🔹 Назначен: {ticket_data['assigned_to_name']}\n"
        f"🔹 Тема: {ticket_data['subject']}\n"
        f"🔹 Дедлайн: {ticket_data['deadline']}\n"
        f"🔹 Статус: {ticket_data['status']}\n\n"
        f"Вы можете просмотреть его в разделе 'Мои тикеты'"
    )
    
    # Отправляем одно сообщение с информацией
    bot.send_text(
        chat_id=chat_id,
        text=ticket_info,
        inline_keyboard_markup=json.dumps([
            [{"text": "📋 Мои тикеты", "callbackData": "user_cmd_/my_tickets", "style": "primary"}],
            [menu_button]
        ])
    )
    
    # Очищаем состояние
    user_states.pop(chat_id, None)

def show_user_tickets(chat_id):
    # Получаем все тикеты, где текущий пользователь является создателем
    user_created_tickets = [
        t for t in tickets.values() 
        if t.get("creator") == chat_id
    ]

    if not user_created_tickets:
        bot.send_text(chat_id=chat_id, text="❌ У вас нет созданных тикетов.")
        return

    keyboard = []
    for ticket in user_created_tickets:
        ticket_id = ticket["id"]
        status = ticket["status"]
        assigned_to = ticket.get("assigned_to_name", "Не назначен")
        
        # Формируем текст кнопки
        button_text = f"{ticket_id}: {ticket['subject']} ({status})"
        if status == "Открыт" and assigned_to != "Себе":
            button_text += f" → {assigned_to}"
        
        row = [{
            "text": button_text,
            "callbackData": f"view_ticket_{ticket_id}"
        }]
        
        # Добавляем кнопку закрытия только для личных тикетов (назначенных себе)
        if status == "Открыт" and assigned_to == "Себе":
            row.append({
                "text": "✅ Закрыть",
                "callbackData": f"close_ticket_{ticket_id}"
            })
        
        keyboard.append(row)
    
    keyboard.append([back_button])
    
    bot.send_text(
        chat_id=chat_id,
        text="📋 Ваши тикеты:",
        inline_keyboard_markup=json.dumps(keyboard)
    )

def show_admin_tickets(chat_id):
    if chat_id not in admin_tickets or not admin_tickets[chat_id]:
        bot.send_text(chat_id=chat_id, text="❌ Нет назначенных тикетов.")
        return
    
    keyboard = []
    for ticket_id in admin_tickets[chat_id]:
        ticket = tickets[ticket_id]
        if ticket["status"] == "Открыт":  # Показываем только открытые
            keyboard.append([
                {
                    "text": f"{ticket_id}: {ticket['subject']}",
                    "callbackData": f"view_ticket_{ticket_id}"
                },
                {
                    "text": "✅ Закрыть",
                    "callbackData": f"admin_cmd_close_ticket_{ticket_id}"
                }
            ])
    if not keyboard:
        bot.send_text(chat_id=chat_id, text="❌ Нет назначенных тикетов.")
        return
    
    keyboard.append([back_button])
    bot.send_text(
        chat_id=chat_id,
        text="📋 Назначенные вам тикеты:",
        inline_keyboard_markup=json.dumps(keyboard)
    )

def show_ticket_info(chat_id, ticket_id):
    if ticket_id not in tickets:
        processing_time
        bot.send_text(chat_id=chat_id, text="❌ Тикет не найден.")
        return
    
    ticket = tickets[ticket_id]
    info_text = (
        f"ℹ️ Информация о тикете #{ticket_id}:\n\n"
        f"🔹 Тема: {ticket['subject']}\n"
        f"🔹 Описание: {ticket['description']}\n"
        f"🔹 Дедлайн: {ticket['deadline']}\n"
        f"🔹 Статус: {ticket['status']}\n"
        f"🔹 Создан: {ticket['created_at']}\n"
        f"🔹 Создатель: {ticket['creator']}\n"
        f"🔹 Назначен: {ticket.get('assigned_to_name', 'Не назначен')}\n"
        f"🔹 Закрыт: {ticket.get('closed_at', '—')}"
    )
    
    keyboard = []
    
    # Показываем кнопку закрытия только если:
    # 1. Это админ ИЛИ
    # 2. Это создатель тикета И тикет назначен себе
    show_close_button = (
        (chat_id in admin_users) or
        (ticket["creator"] == chat_id and 
         ticket.get("assigned_to_name") == "Себе" and
         ticket["status"] == "Открыт")
    )
    
    if show_close_button and ticket["status"] == "Открыт":
        keyboard.append([{
            "text": "✅ Закрыть тикет",
            "callbackData": f"close_ticket_{ticket_id}"
        }])
    
    keyboard.append([back_button])
    
    processing_time
    bot.send_text(
        chat_id=chat_id,
        text=info_text,
        inline_keyboard_markup=json.dumps(keyboard)
    )

def close_ticket(chat_id, ticket_id):
    ticket = tickets.get(ticket_id)
    if not ticket:
        bot.send_text(chat_id=chat_id, text="❌ Тикет не найден.")
        return
    
    # Разрешаем закрывать:
    # 1. Администраторам
    # 2. Создателю тикета, если он назначен себе
    if (chat_id not in admin_users and 
        (ticket["creator"] != chat_id or ticket.get("assigned_to_name") != "Себе")):
        bot.send_text(chat_id=chat_id, text="❌ Вы не можете закрыть этот тикет.")
        return
    
    # Обновляем статус тикета
    ticket["status"] = "Закрыт"
    ticket["closed_at"] = datetime.now(MOSCOW_TZ).strftime("%d.%m.%Y %H:%M")
    ticket["closed_by"] = chat_id
    
    # Уведомляем создателя тикета (если закрыл не он сам)
    if ticket["creator"] != chat_id and ticket["creator"] in active_chats:
        notification_text = (
            f"🔔 Ваш тикет #{ticket_id} был закрыт!\n\n"
            f"🔹 Тема: {ticket['subject']}\n"
            f"🔹 Закрыт: {ticket['closed_at']}\n"
            f"🔹 Закрыл: {admin_users.get(chat_id, 'Администратор')}"
        )
        bot.send_text(
            chat_id=ticket["creator"],
            text=notification_text,
            inline_keyboard_markup=json.dumps([[back_button]])
        )
    
    processing_time
    bot.send_text(
        chat_id=chat_id,
        text=f"✅ Тикет #{ticket_id} успешно закрыт.",
        inline_keyboard_markup=json.dumps([[back_button]])
    )
        
def start_create_event(chat_id): #создание события
    user_states[chat_id] = {
        "state": "awaiting_event_name",
        "event_data": {}
    }
    processing_time
    bot.send_text(
        chat_id=chat_id,
        text="🗓 Создание события\nУкажите название события:",
        inline_keyboard_markup=json.dumps([[back_button, cancel_button]])
        )

def process_event_creation(chat_id, message_text): #обработка и сохранение события

    if user_states.get(chat_id, {}).get("state") == "awaiting_event_name":
        user_states[chat_id]["event_data"]["name"] = message_text
        user_states[chat_id]["state"] = "awaiting_event_description"
        processing_time
        bot.send_text(
            chat_id=chat_id,
            text="📝 Теперь опишите событие подробно:",
            inline_keyboard_markup=json.dumps([[back_button, cancel_button]])
        )
    
    elif user_states.get(chat_id, {}).get("state") == "awaiting_event_description":
        user_states[chat_id]["event_data"]["description"] = message_text
        user_states[chat_id]["state"] = "awaiting_event_datetime"
        processing_time
        bot.send_text(
            chat_id=chat_id,
            text="⏰ Укажите дату и время события (в формате ДД.ММ.ГГГГ ЧЧ:ММ):",
            inline_keyboard_markup=json.dumps([[back_button, cancel_button]])
        )
    
    elif user_states.get(chat_id, {}).get("state") == "awaiting_event_datetime":
        try:
        # Преобразуем введенное время с учетом московского часового пояса
            naive_datetime = datetime.strptime(message_text, "%d.%m.%Y %H:%M")
            event_datetime = MOSCOW_TZ.localize(naive_datetime)
            user_states[chat_id]["event_data"]["datetime"] = event_datetime

            # Переходим к вводу времени напоминания
            processing_time
            bot.send_text(
                chat_id=chat_id,
                text="⏰ Через сколько времени напомнить?\n"
                    "Введите интервал в формате:\n"
                    "Д:ЧЧ:ММ:СС\n"
                    "Например: 0:02:30:00 — за 2 часа 30 минут",
                inline_keyboard_markup=json.dumps([[back_button, cancel_button]])
            )

            user_states[chat_id]["state"] = "awaiting_event_reminder"
        except ValueError:
            processing_time
            bot.send_text(
                chat_id=chat_id,
                text="❌ Неверный формат даты и времени. Пожалуйста, укажите в формате ДД.ММ.ГГГГ ЧЧ:ММ:"
            )
    elif user_states.get(chat_id, {}).get("state") == "awaiting_event_reminder":
        time_format_pattern = r"^\d+:\d{2}:\d{2}:\d{2}$"
        if not re.match(time_format_pattern, message_text):
            processing_time
            bot.send_text(
                chat_id=chat_id,
                text="❌ Неверный формат времени напоминания.\n"
                     "Используйте формат Д:ЧЧ:ММ:СС\n"
                     "Пример: 0:00:10:30 — за 10 минут 30 секунд"
            )
            return
        try:
            # Парсим формат Д:ЧЧ:ММ:СС
            days, hours, minutes, seconds = map(int, message_text.split(':'))
            if any(x < 0 for x in [days, hours, minutes, seconds]):
                raise ValueError("Время не может быть отрицательным")

            event_data = user_states[chat_id]["event_data"]
            event_datetime = event_data["datetime"]

            # Вычисляем время напоминания
            reminder_delta = timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
            reminder_time = event_datetime - reminder_delta

            # Сохраняем событие
            if chat_id not in events:
                events[chat_id] = []
            event_id = f"EVT-{len(events[chat_id]) + 1:03d}"
            event_data["id"] = event_id
            event_data["status"] = "Запланировано"
            event_data["created_at"] = datetime.now(MOSCOW_TZ).strftime("%d.%m.%Y %H:%M")
            events[chat_id].append(event_data)

            # Сообщение пользователю
            event_info = (
                f"✅ Событие создано!\n"
                f"🔹 Название: {event_data['name']}\n"
                f"🔹 Описание: {event_data['description']}\n"
                f"🔹 Дата и время: {event_datetime.strftime('%d.%m.%Y %H:%M')}\n"
                f"🔔 Напомню за {days} дней {hours} часов {minutes} минут {seconds} секунд"
            )

            processing_time
            bot.send_text(chat_id=chat_id, text=event_info,
                inline_keyboard_markup=json.dumps([[back_button]])
            )

            # Запуск напоминания
            threading.Thread(
                target=schedule_reminder,
                args=(chat_id, event_id, event_data['name'], reminder_time),
                daemon=True
            ).start()

            # Очистка состояния
            user_states.pop(chat_id, None)
        except Exception as e:
            print(e)
            processing_time
            bot.send_text(
                chat_id=chat_id,
                text="❌ Неверный формат времени напоминания.\n"
                     "Используйте формат Д:ЧЧ:ММ:СС\n")
               
def schedule_reminder(chat_id, event_id, event_name, reminder_time): #напоминание о событии
        now = datetime.now(MOSCOW_TZ)
        delay = (reminder_time - now).total_seconds()
        if delay > 0:
            time.sleep(delay)
            bot.send_text(
                chat_id=chat_id,
                text=f"🔔 Напоминание о событии!\n"
                    f"Через несколько минут начнётся:\n"
                    f"*{event_name}*\n"
                    f"ID события: {event_id}",
                inline_keyboard_markup=json.dumps([[back_button]])
            )

def show_my_events(chat_id): #события пользователя
    if chat_id not in events or not events[chat_id]:
        processing_time
        bot.send_text(chat_id=chat_id, text="У вас нет запланированных событий.", 
            inline_keyboard_markup=json.dumps([[back_button]])
        )
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
    
    processing_time
    bot.send_text(chat_id=chat_id, text=events_text, 
        inline_keyboard_markup=json.dumps([[back_button]])
    )

def show_help(chat_id): #действие при команде /help
    user_context[chat_id] = "help"
    help_text = (
        "📋 Список всех доступных команд:\n\n"
        "🔹 Основные команды:\n"
        "/news - Последние новости компании\n"
        "/about - Информация о компании\n"
        "/contacts - Контактные данные\n"
        "/cancel - Прервать текущий диалог\n"
        "/back - Вернуться назад\n\n"
        "🔹 1С материалы:\n"
        "/1c_docs - Документация и материалы по 1С\n"
        "/1c_reviews - Отзывы о наших внедрениях 1С\n\n"
        "🔹 Поддержка:\n"
        "/support - Создать новый тикет\n"
        "/my_tickets - Просмотреть мои тикеты\n"
        "/close_ticket - Закрыть тикет\n\n"
        "🔹 События:\n"
        "/create_event - Создать новое событие\n"
        "/my_events - Посмотреть мои события\n"
        "🔹 Администрирование:\n"
        "/stats - Статистика использования бота\n"
        "/broadcast - Рассылка сообщений\n\n"
        "Воспользуйтесь кнопками или введите команду вручную"
    )
    processing_time
    bot.send_text(chat_id=chat_id, text=help_text)
    start_command_buttons(chat_id)

def cancel_current_dialog(chat_id): #???выход из диалога??? не вижу удаления из списка активных чатов с ботом
    if chat_id in user_states:
        del user_states[chat_id]  # Полностью очищаем состояние

    processing_time
    bot.send_text(chat_id=chat_id, text="❌ Вы вышли из текущего диалога.", 
        inline_keyboard_markup=json.dumps([[back_button]])
    )

def show_admin_panel(chat_id): #панель администратора
    processing_time
    start_command_buttons(chat_id)
    if chat_id not in admin_users:
        processing_time
        bot.send_text(chat_id=chat_id, text="❌ У вас нет доступа к админ-панели.")
        return
    
    processing_time
    bot.send_text(
        chat_id=chat_id,
        text="🛠 Админ-панель",
        inline_keyboard_markup=json.dumps([
            [
                {"text": "📢 Рассылка", "callbackData": "admin_cmd_broadcast", "style": "attention"},
                {"text": "📊 Статистика", "callbackData": "admin_cmd_stats", "style": "primary"}
            ],
            [back_button]
        ])
    )

def start_broadcast(chat_id): #создание рассылки
    if chat_id not in admin_users:
        processing_time
        bot.send_text(chat_id=chat_id, text="❌ У вас нет прав для рассылки.")
        return
    
    user_states[chat_id] = {
        "state": "awaiting_broadcast_message",
        "broadcast_data": {}
    }

    processing_time
    bot.send_text(
        chat_id=chat_id,
        text="📢 Введите сообщение для рассылки всем пользователям:",
        inline_keyboard_markup=json.dumps([
            [{"text": "❌ Отмена", "callbackData": "admin_cmd_cancel_broadcast", "style": "secondary"}]
        ])
    )

def process_broadcast(chat_id, message_text): #обработка и подтверждение рассылки
    if chat_id not in admin_users:
        processing_time
        bot.send_text(chat_id=chat_id, text="❌ У вас нет прав для рассылки.")
        return
    
    # Сохраняем сообщение для рассылки
    user_states[chat_id]["broadcast_data"]["message"] = message_text
    
    # Запрашиваем подтверждение
    processing_time
    bot.send_text(
        chat_id=chat_id,
        text=f"✉️ Вы уверены, что хотите разослать это сообщение всем пользователям?\n\n{message_text}",
        inline_keyboard_markup=json.dumps([
            [
                {"text": "✅ Да, разослать", "callbackData": "admin_cmd_confirm_broadcast", "style": "attention"},
                {"text": "❌ Отмена", "callbackData": "admin_cmd_cancel_broadcast", "style": "secondary"}
            ]
        ])
    )

def send_broadcast(chat_id): #выполнение рассылки
    if chat_id not in admin_users:
        processing_time
        bot.send_text(chat_id=chat_id, text="❌ У вас нет прав для рассылки.")
        return
    
    broadcast_data = user_states[chat_id]["broadcast_data"]
    message = broadcast_data["message"]
    
    # Отправляем сообщение всем активным чатам
    for user_chat in active_chats:
        try:
            processing_time
            bot.send_text(
                chat_id=user_chat,
                text=f"📢 Важное сообщение от администратора:\n\n{message}",
                inline_keyboard_markup=json.dumps([
                    [back_button]
                ])
            )
            processing_time # Небольшая задержка, чтобы не перегружать сервер
        except Exception as e:
            print(f"Ошибка при отправке сообщения пользователю {user_chat}: {e}")
    
    # Уведомляем администратора
    processing_time
    bot.send_text(
        chat_id=chat_id,
        text=f"✅ Рассылка успешно отправлена {len(active_chats)} пользователям.",
        inline_keyboard_markup=json.dumps([
            [{"text": "⬅️ Вернуться в панель администратора", "callbackData": "user_cmd_/admin_panel", "style": "secondary"}]
        ])
    )
    
    # Очищаем состояние
    del user_states[chat_id]

def cancel_broadcast(chat_id): #отмена рассылки
    if chat_id in user_states and user_states[chat_id].get("state") == "awaiting_broadcast_message":
        del user_states[chat_id]
    
    processing_time
    bot.send_text(
        chat_id=chat_id,
        text="❌ Рассылка отменена.",
        inline_keyboard_markup=json.dumps([
            [{"text": "⬅️ В админ-панель", "callbackData": "user_cmd_/admin_panel", "style": "secondary"}]
        ])
    )

def go_back(chat_id): #кнопка "назад"
     # Если есть активное состояние (создание тикета/события)
    if chat_id in user_states:
        state_info = user_states[chat_id]
        state = state_info.get("state", "")
        
        # Создание тикета
        if state == "awaiting_ticket_description":
            processing_time
            bot.send_text(
                chat_id=chat_id,
                text="🛠 Измените тему обращения:",
                inline_keyboard_markup=json.dumps([[back_button, cancel_button]])
            )
            state_info["state"] = "awaiting_ticket_subject"

        elif state == "awaiting_ticket_deadline":
            subject = state_info["ticket_data"].get("subject", "")
            description = state_info["ticket_data"].get("description", "")
            processing_time
            bot.send_text(
                chat_id=chat_id,
                text=f"🛠 Тема: {subject}\n📝 Описание: {description}\n\nИзмените описание обращения:",
                inline_keyboard_markup=json.dumps([[back_button, cancel_button]])
            )
            state_info["state"] = "awaiting_ticket_description"

        # Создание события
        elif state == "awaiting_event_description":
            name = state_info["event_data"].get("name", "")
            processing_time
            bot.send_text(
                chat_id=chat_id,
                text=f"🗓 Измените название события:\n(было: {name})",
                inline_keyboard_markup=json.dumps([[back_button, cancel_button]])
            )
            state_info["state"] = "awaiting_event_name"

        elif state == "awaiting_event_reminder":
            name = state_info["event_data"].get("name", "")
            description = state_info["event_data"].get("description", "")
            datetime_str = state_info["event_data"]["datetime"].strftime("%d.%m.%Y %H:%M")
            processing_time
            bot.send_text(
                chat_id=chat_id,
                text=f"🗓 Название: {name}\n📝 Описание: {description}\n"
                     f"📅 Дата и время: {datetime_str}\nИзмените дату и время события:",
                inline_keyboard_markup=json.dumps([[back_button, cancel_button]])
            )
            state_info["state"] = "awaiting_event_datetime"

        # Для всех необработанных состояний
        else:
            user_states.pop(chat_id, None)
            processing_time
            start_command_buttons(chat_id)

    # Если есть контекст (просмотр разделов)
    elif chat_id in user_context:
        del user_context[chat_id]
        processing_time
        start_command_buttons(chat_id)

    # Стандартный возврат в главное меню
    else:
        processing_time
        start_command_buttons(chat_id)

def process_command(chat_id, command):  # обрабатывает все команды
    command = command.lower().strip()

    # Если пользователь ввел любую команду во время создания тикета - очищаем состояние
    if chat_id in user_states and user_states[chat_id].get("state", "").startswith("awaiting_ticket"):
        if not command.startswith("/support") and command not in ["/back", "/cancel"]:
            del user_states[chat_id]  # Очищаем состояние создания тикета
            bot.send_text(chat_id=chat_id, text="❌ Создание тикета отменено")
    
    # Очистка состояния создания события при вводе другой команды
    if chat_id in user_states and user_states[chat_id].get("state", "").startswith("awaiting_event"):
        if not command.startswith("/create_event") and command not in ["/back", "/cancel"]:
            del user_states[chat_id]
            bot.send_text(chat_id=chat_id, text="❌ Создание события отменено")
            
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
        if chat_id in admin_users:
            # Администраторам показываем оба варианта через кнопки
            bot.send_text(
                chat_id=chat_id,
                text="Выберите тип тикетов:",
                inline_keyboard_markup=json.dumps([
                    [
                        {"text": "📌 Мои личные", "callbackData": "user_cmd_show_personal_tickets"},
                        {"text": "💼 Назначенные мне", "callbackData": "user_cmd_show_assigned_tickets"}
                    ],
                    [back_button]
                ])
            )
        else:
            show_user_tickets(chat_id)
    elif command == "/create_event":
        start_create_event(chat_id)
    elif command == "/my_events":
        show_my_events(chat_id)
    elif command == "/admin_panel":
        show_admin_panel(chat_id)
    elif command == "/broadcast":
        start_broadcast(chat_id)
    else:
        bot.send_text(chat_id=chat_id, text="Неизвестная команда. Введите /help")

def simulate_user_message(chat_id, text): #команда от пользователя
    processing_time
    bot.send_text(
        chat_id=chat_id,
        text=f"Вы выбрали команду: {text}"
    )
    process_command(chat_id, text)

def message_cb(bot, event):
    chat_id = event.from_chat
    text = event.text.strip()
    active_chats.add(chat_id)
    
    # Если это команда (начинается с /) - обрабатываем как команду
    if text.startswith('/'):
        process_command(chat_id, text)
        return
    
    # Если нет - проверяем состояние пользователя
    state = user_states.get(chat_id, {}).get("state", "")
    
    if state == "awaiting_broadcast_message":
        process_broadcast(chat_id, text)
    elif state.startswith("awaiting_ticket"):
        process_ticket_creation(chat_id, text)
    elif state.startswith("awaiting_event"):
        process_event_creation(chat_id, text)
    else:
        bot.send_text(chat_id=chat_id, text="Пожалуйста, используйте команды из меню")
        start_command_buttons(chat_id)

def button_cb(bot, event):
    try:
        bot.answer_callback_query(
            query_id=event.data['queryId'],
            text="⌛ Обработка..."
        )
        time.sleep(0.1)

        chat_id = event.from_chat
        active_chats.add(chat_id)

        callback_data = event.data['callbackData']

        # Обработка назначения тикета
        if callback_data.startswith('assign_ticket_'):
            admin_email = callback_data.replace('assign_ticket_', '')
            assign_ticket(chat_id, admin_email)
            return
            
        # Обработка закрытия тикета
        if callback_data.startswith('close_ticket_'):
            ticket_id = callback_data.replace('close_ticket_', '')
            close_ticket(chat_id, ticket_id)
            return

        # Просмотр информации о тикете
        elif callback_data.startswith('view_ticket_'):
            ticket_id = callback_data.replace('view_ticket_', '')
            show_ticket_info(chat_id, ticket_id)
            return
            
        # Обработка просмотра тикетов администратором
        elif callback_data == "user_cmd_show_personal_tickets":
            show_user_tickets(chat_id)
            return
            
        elif callback_data == "user_cmd_show_assigned_tickets":
            show_admin_tickets(chat_id)
            return

        # Обработка пользовательских команд
        elif callback_data.startswith('user_cmd_'):
            command = callback_data[9:]  # Убираем префикс user_cmd_
            process_command(chat_id, command)
            
        # Обработка админских команд
        elif callback_data.startswith('admin_cmd_'):
            if chat_id not in admin_users:
                bot.send_text(chat_id=chat_id, text="❌ У вас нет прав администратора!")
                return

            command = callback_data[10:]  # Убираем префикс admin_cmd_

            if command == "broadcast":
                start_broadcast(chat_id)
            elif command == "stats":
                stats_text = (
                    f"📊 Статистика бота:\n\n"
                    f"• Активных пользователей: {len(active_chats)}\n"
                    f"• Создано тикетов: {sum(len(v) for v in tickets.values())}\n"
                    f"• Создано событий: {sum(len(v) for v in events.values())}"
                )
                bot.send_text(
                    chat_id=chat_id,
                    text=stats_text,
                    inline_keyboard_markup=json.dumps([
                        [{"text": "⬅️ Назад", "callbackData": "user_cmd_/admin_panel", "style": "secondary"}]
                    ])
                )
            elif command == "confirm_broadcast":
                send_broadcast(chat_id)
            elif command == "cancel_broadcast":
                cancel_broadcast(chat_id)

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