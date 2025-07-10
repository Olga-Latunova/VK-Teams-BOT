import json
from bot.bot import Bot
from bot.handler import MessageHandler, BotButtonCommandHandler
import time
from datetime import datetime, timedelta
import threading
import pytz  # библиотека для работы с часовыми поясами
import re
import sqlite3
from datetime import datetime, timedelta

# Подключение к базе данных
conn = sqlite3.connect('tickets.db')
cursor = conn.cursor()

# Выбираем все данные из таблицы tickets
cursor.execute("SELECT * FROM tickets")

# Получаем заголовки столбцов
columns = [description[0] for description in cursor.description]

# Выводим заголовки
print(" | ".join(columns))

# Выводим строки
for row in cursor.fetchall():
    print(" | ".join(str(cell) for cell in row))

# Закрываем соединение
conn.close()
# Создаем соединение с базой данных

DB_FILE = 'tickets.db' 

TOKEN = "001.1806729577.0340071044:1011814127"  # токен бота
# Удалите старую функцию init_db() и оставьте только:
class Database:
    @staticmethod
    def init_db():
        """Инициализация структуры базы данных"""
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            
            # Таблица тикетов
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS tickets (
                id TEXT PRIMARY KEY,
                creator TEXT NOT NULL,
                assigned_to TEXT,
                assigned_to_name TEXT,
                subject TEXT NOT NULL,
                description TEXT NOT NULL,
                deadline TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                closed_at TEXT,
                closed_by TEXT,
                ticket_type TEXT
            )
            ''')
            
            # Индексы для ускорения запросов
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_creator ON tickets(creator)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON tickets(status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_assigned ON tickets(assigned_to)')
            
            conn.commit()

# Инициализация БД
Database.init_db()

# Получаем следующий номер тикета из БД
def get_next_ticket_number():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(id) FROM tickets")
        result = cursor.fetchone()[0]
        if result:
            last_num = int(result.split('-')[1])
            return last_num + 1
        else:
            return 1

ticket_counter = get_next_ticket_number()

def generate_ticket_id():
    global ticket_counter
    ticket_id = f"TKT-{ticket_counter:04d}"
    ticket_counter += 1
    return ticket_id
    

ticket_counter = 1
usage_stats = {}
user_stats = {}

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
admin_users = set()  # Множество пользователей с админскими правами
active_chats = set()  # Множество активных чатов с ботом
user_tickets = {}  # Хранение тикетов пользователей {chat_id: [ticket_ids]}
admin_tickets = {}  # Хранение тикетов администраторов {chat_id: [ticket_ids]}
adm_password = str(105) # Пароль администратора
admin_users = {
    "i.osipova@bot-60.bizml.ru": "Осипова Ирина",
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



def start_command_buttons(chat_id): #главное меню
    buttons = [
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
            {"text": "📊 Моя статистика", "callbackData": "user_cmd_/my_stats", "style": "primary"}
        ]
    ]

    if chat_id in admin_users:
        buttons.append([{"text": "🛠 Администраторам", "callbackData": "user_cmd_/admin_panel", "style": "attention"}])

    bot.send_text(
        chat_id=chat_id,
        text="Выберите действие ниже:",
        inline_keyboard_markup=json.dumps(buttons)
    )

# Добавляем обработку команды /my_stats
def show_my_stats(chat_id):
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            
            # Общее количество тикетов
            cursor.execute('SELECT COUNT(*) FROM tickets WHERE creator = ?', (chat_id,))
            total_tickets = cursor.fetchone()[0]
            
            # Количество открытых тикетов
            cursor.execute('''
            SELECT COUNT(*) 
            FROM tickets 
            WHERE creator = ? AND status = 'Открыт'
            ''', (chat_id,))
            open_tickets = cursor.fetchone()[0]
            
            bot.send_text(
                chat_id=chat_id,
                text=f"📊 Ваша статистика:\n\n"
                     f"👤 Пользователь: {admin_users.get(chat_id, chat_id)}\n"
                     f"📧 Email: {chat_id}\n"
                     f"🔢 Всего запросов: {user_stats.get(chat_id, 0)}\n"
                     f"🎫 Всего тикетов: {total_tickets}\n"
                     f"🟢 Открытых тикетов: {open_tickets}",
                inline_keyboard_markup=json.dumps([[back_button]])
            )
            
    except sqlite3.Error as e:
        print(f"Ошибка базы данных: {e}")
        bot.send_text(chat_id=chat_id, text="❌ Ошибка при загрузке статистики")
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
    time.sleep(0.2)
    bot.send_text(
        chat_id=chat_id, 
        text="🛠 Создание тикета\n\nУкажите тему обращения:",
        inline_keyboard_markup=json.dumps([[back_button]])
    )


def process_ticket_creation(chat_id, message_text): #обработка и сохранение тикета
    # Проверка на отмену
    if message_text.strip().lower() in ("/cancel", "/back"):
        user_states.pop(chat_id, None)
        bot.send_text(chat_id=chat_id, text="❌ Создание тикета отменено")
        return

    state = user_states.get(chat_id, {}).get("state")
    ticket_data = user_states.get(chat_id, {}).get("ticket_data", {})

    if not state or not ticket_data:
        bot.send_text(chat_id=chat_id, text="❌ Ошибка: данные тикета не найдены")
        return

    if state == "awaiting_ticket_subject":
        if not message_text.strip():
            bot.send_text(chat_id=chat_id, text="❌ Тема не может быть пустой.")
            return
        ticket_data["subject"] = message_text.strip()
        user_states[chat_id]["state"] = "awaiting_ticket_description"
        time.sleep(0.2)
        bot.send_text(
            chat_id=chat_id, 
            text="📝 Теперь опишите проблему подробно:", 
            inline_keyboard_markup=json.dumps([[back_button, cancel_button]])
        )

    elif state == "awaiting_ticket_description":
        if not message_text.strip():
            bot.send_text(chat_id=chat_id, text="❌ Описание не может быть пустым.")
            return
        ticket_data["description"] = message_text.strip()
        user_states[chat_id]["state"] = "awaiting_ticket_deadline"
        time.sleep(0.2)
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

            admin_buttons = [{
                "text": "👤 Назначить себе", 
                "callbackData": "assign_ticket_self"
            }]

            for email, name in admin_users.items():
                if email != chat_id:
                    admin_buttons.append({
                        "text": f"👤 {name}",
                        "callbackData": f"assign_ticket_{email}"
                    })

            keyboard = [admin_buttons[i:i + 2] for i in range(0, len(admin_buttons), 2)]
            keyboard.append([back_button, cancel_button])

            time.sleep(0.2)
            bot.send_text(
                chat_id=chat_id,
                text="👥 Выберите, кому назначить тикет:",
                inline_keyboard_markup=json.dumps(keyboard)
            )

        except ValueError:
            time.sleep(0.2)
            bot.send_text(
                chat_id=chat_id,
                text="❌ Неверный формат даты. Пожалуйста, укажите дату в формате ДД.ММ.ГГГГ:"
            )

def assign_ticket(chat_id, admin_id):
    if chat_id not in user_states:
        bot.send_text(chat_id=chat_id, text="❌ Ошибка: данные тикета не найдены")
        return
    
    ticket_data = user_states[chat_id]["ticket_data"]
    
    # Обработка назначения
    if admin_id == "self":
        ticket_data.update({
            "ticket_type": "personal",
            "assigned_to": chat_id,
            "assigned_to_name": "Себе"
        })
    else:
        ticket_data.update({
            "ticket_type": "assigned",
            "assigned_to": admin_id,
            "assigned_to_name": admin_users.get(admin_id, "Администратор")
        })
    
    # Генерация ID и даты
    ticket_id = generate_ticket_id()
    created_at = datetime.now(MOSCOW_TZ).strftime("%d.%m.%Y %H:%M")
    
    # Проверяем, не существует ли такой ID
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT 1 FROM tickets WHERE id = ?', (ticket_id,))
            if cursor.fetchone():
                print(f"Ошибка: тикет с ID {ticket_id} уже существует")
                bot.send_text(chat_id=chat_id, text="❌ Ошибка: конфликт ID, попробуйте ещё раз")
                return

            # Сохранение в БД
            cursor.execute('''
            INSERT INTO tickets VALUES (
                :id, :creator, :assigned_to, :assigned_to_name, :subject,
                :description, :deadline, :status, :created_at,
                :closed_at, :closed_by, :ticket_type
            )
            ''', {
                "id": ticket_id,
                "creator": ticket_data["creator"],
                "assigned_to": ticket_data["assigned_to"],
                "assigned_to_name": ticket_data["assigned_to_name"],
                "subject": ticket_data["subject"],
                "description": ticket_data["description"],
                "deadline": ticket_data["deadline"],
                "status": "Открыт",
                "created_at": created_at,
                "closed_at": None,
                "closed_by": None,
                "ticket_type": ticket_data["ticket_type"]
            })
            conn.commit()
    except sqlite3.Error as e:
        print(f"Ошибка базы данных: {e}")
        bot.send_text(chat_id=chat_id, text="❌ Ошибка при сохранении тикета")
        return
    
    # Уведомление администратора
    if ticket_data["ticket_type"] == "assigned":
        try:
            bot.send_text(
                chat_id=admin_id,
                text=(
                    f"🔔 Вам назначен новый тикет!\n\n"
                    f"🔹 Номер: {ticket_id}\n"
                    f"🔹 От: {admin_users.get(chat_id, chat_id)}\n"
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

    # Сообщение создателю
    bot.send_text(
        chat_id=chat_id,
        text=(
            f"✅ Тикет успешно создан!\n\n"
            f"🔹 Номер: {ticket_id}\n"
            f"🔹 Назначен: {ticket_data['assigned_to_name']}\n"
            f"🔹 Тема: {ticket_data['subject']}\n"
            f"🔹 Дедлайн: {ticket_data['deadline']}\n"
            f"🔹 Статус: Открыт\n\n"
            f"Вы можете просмотреть его в разделе 'Мои тикеты'"
        ),
        inline_keyboard_markup=json.dumps([
            [{"text": "📋 Мои тикеты", "callbackData": "user_cmd_/my_tickets", "style": "primary"}],
            [menu_button]
        ])
    )

    # Очистка состояния
    user_states.pop(chat_id, None)

def show_user_tickets(chat_id):
    try:
            conn = sqlite3.connect(DB_FILE)
            conn.row_factory = sqlite3.Row  
            cursor = conn.cursor()
            cursor.execute('''
            SELECT id, subject, status, assigned_to_name 
            FROM tickets 
            WHERE creator = ?
            ORDER BY created_at DESC
            ''', (chat_id,))
            
            tickets = cursor.fetchall()
            
            if not tickets:
                bot.send_text(chat_id=chat_id, text="❌ У вас нет созданных тикетов.")
                return
            
            keyboard = []
            for ticket in tickets:
                row = [{
                    "text": f"{ticket['id']}: {ticket['subject']} ({ticket['status']})",
                    "callbackData": f"view_ticket_{ticket['id']}"
                }]
                
                if ticket['status'] == "Открыт" and ticket['assigned_to_name'] == "Себе":
                    row.append({
                        "text": "✅ Закрыть",
                        "callbackData": f"close_ticket_{ticket['id']}"
                    })
                
                keyboard.append(row)
            
            keyboard.append([back_button])
            
            bot.send_text(
                chat_id=chat_id,
                text="📋 Ваши тикеты:",
                inline_keyboard_markup=json.dumps(keyboard)
            )
            
    except sqlite3.Error as e:
        print(f"Ошибка базы данных: {e}")
        bot.send_text(chat_id=chat_id, text="❌ Ошибка при загрузке тикетов")

def show_admin_tickets(chat_id):
    try:
            conn = sqlite3.connect(DB_FILE)
            conn.row_factory = sqlite3.Row  # ✅ ПРАВИЛЬНО
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT id, subject, status 
            FROM tickets 
            WHERE assigned_to = ? AND status = 'Открыт'
            ORDER BY created_at DESC
            ''', (chat_id,))
            
            admin_tickets = cursor.fetchall()
            
            if not admin_tickets:
                bot.send_text(chat_id=chat_id, text="❌ Нет назначенных вам тикетов.")
                return
            
            keyboard = []
            for ticket in admin_tickets:
                keyboard.append([
                    {
                        "text": f"{ticket['id']}: {ticket['subject']}",
                        "callbackData": f"view_ticket_{ticket['id']}"
                    },
                    {
                        "text": "✅ Закрыть",
                        "callbackData": f"admin_cmd_close_ticket_{ticket['id']}"
                    }
                ])
            
            keyboard.append([back_button])
            
            bot.send_text(
                chat_id=chat_id,
                text="📋 Назначенные вам тикеты:",
                inline_keyboard_markup=json.dumps(keyboard))
                
    except sqlite3.Error as e:
        print(f"Ошибка БД: {e}")
        bot.send_text(chat_id=chat_id, text="❌ Ошибка при загрузке тикетов")
def show_ticket_info(chat_id, ticket_id):
    try:
            conn = sqlite3.connect(DB_FILE)
            conn.row_factory = sqlite3.Row  # ✅ ПРАВИЛЬНО
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM tickets WHERE id = ?', (ticket_id,))
            ticket = cursor.fetchone()
            
            if not ticket:
                bot.send_text(chat_id=chat_id, text="❌ Тикет не найден.")
                return
            
            info_text = (
                f"ℹ️ Информация о тикете #{ticket['id']}:\n\n"
                f"🔹 Тема: {ticket['subject']}\n"
                f"🔹 Описание: {ticket['description']}\n"
                f"🔹 Дедлайн: {ticket['deadline']}\n"
                f"🔹 Статус: {ticket['status']}\n"
                f"🔹 Создан: {ticket['created_at']}\n"
                f"🔹 Создатель: {admin_users.get(ticket['creator'], ticket['creator'])}\n"
                f"🔹 Назначен: {ticket['assigned_to_name']}\n"
                f"🔹 Закрыт: {ticket['closed_at'] if ticket['closed_at'] else '—'}"
            )
            
            keyboard = []
            can_close = (
                chat_id in admin_users or 
                (ticket['creator'] == chat_id and ticket['assigned_to_name'] == "Себе" and ticket['status'] == "Открыт")
            )
            
            if can_close and ticket['status'] == "Открыт":
                keyboard.append([{
                    "text": "✅ Закрыть тикет",
                    "callbackData": f"close_ticket_{ticket['id']}"
                }])
            
            keyboard.append([back_button])
            
            bot.send_text(
                chat_id=chat_id,
                text=info_text,
                inline_keyboard_markup=json.dumps(keyboard))
                
    except sqlite3.Error as e:
        print(f"Ошибка базы данных: {e}")
        bot.send_text(chat_id=chat_id, text="❌ Ошибка при загрузке информации о тикете")


def delete_ticket(ticket_id):
    conn = sqlite3.connect('tickets.db')
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM tickets WHERE id = ?', (ticket_id,))
    conn.commit()
    conn.close()

def close_ticket(chat_id, ticket_id):
    try:
        with sqlite3.connect(DB_FILE) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Получаем данные тикета
            cursor.execute('''
            SELECT creator, assigned_to_name, status, subject 
            FROM tickets 
            WHERE id = ?
            ''', (ticket_id,))
            ticket = cursor.fetchone()
            
            if not ticket:
                bot.send_text(chat_id=chat_id, text="❌ Тикет не найден.")
                return
                
            # Проверяем права на закрытие
            if (chat_id not in admin_users and 
                (ticket['creator'] != chat_id or ticket['assigned_to_name'] != "Себе")):
                bot.send_text(chat_id=chat_id, text="❌ Вы не можете закрыть этот тикет.")
                return
            
            # Обновляем статус
            closed_at = datetime.now(MOSCOW_TZ).strftime("%d.%m.%Y %H:%M")
            cursor.execute('''
            UPDATE tickets 
            SET status = 'Закрыт', closed_at = ?, closed_by = ?
            WHERE id = ?
            ''', (closed_at, chat_id, ticket_id))
            conn.commit()
            
            # Уведомляем создателя (если закрыл не он сам)
            if ticket['creator'] != chat_id:
                try:
                    bot.send_text(
                        chat_id=ticket['creator'],
                        text=(
                            f"🔔 Ваш тикет #{ticket_id} был закрыт!\n\n"
                            f"🔹 Тема: {ticket['subject']}\n"
                            f"🔹 Закрыт: {closed_at}\n"
                            f"🔹 Закрыл: {admin_users.get(chat_id, 'Администратор')}"
                        ),
                        inline_keyboard_markup=json.dumps([[back_button]])
                    )
                except Exception as e:
                    print(f"Ошибка при уведомлении создателя: {e}")
            
            bot.send_text(
                chat_id=chat_id,
                text=f"✅ Тикет #{ticket_id} успешно закрыт.",
                inline_keyboard_markup=json.dumps([[back_button]])
            )
            
    except sqlite3.Error as e:
        print(f"Ошибка базы данных: {e}")
        bot.send_text(chat_id=chat_id, text="❌ Ошибка при закрытии тикета")
        
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
    bot.send_text(
        chat_id=chat_id,
        text="🛠 Админ-панель",
        inline_keyboard_markup=json.dumps([
            [
                {"text": "📢 Рассылка", "callbackData": "admin_cmd_broadcast", "style": "attention"},
                {"text": "📊 Вся статистика", "callbackData": "admin_cmd_all_stats", "style": "primary"}
            ],
            [back_button]
        ])
    )

# Добавляем функцию показа всей статистики для админов
def show_all_stats(chat_id):
    try:
        conn = sqlite3.connect('tickets.db')
        cursor = conn.cursor()
        
        # Получаем общую статистику
        cursor.execute('SELECT COUNT(*) FROM tickets')
        total_tickets = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM tickets WHERE status = "Открыт"')
        open_tickets = cursor.fetchone()[0]
        
        # Получаем статистику по пользователям
        cursor.execute('''
        SELECT creator, COUNT(*) as ticket_count
        FROM tickets
        GROUP BY creator
        ORDER BY ticket_count DESC
        ''')
        user_stats = cursor.fetchall()
        
        stats_text = "📊 Общая статистика:\n\n"
        stats_text += f"🔹 Всего тикетов: {total_tickets}\n"
        stats_text += f"🔹 Открытых тикетов: {open_tickets}\n\n"
        stats_text += "📌 Статистика по пользователям:\n"
        
        for user, count in user_stats:
            stats_text += f"👤 {admin_users.get(user, user)}: {count} тикетов\n"
        
        bot.send_text(
            chat_id=chat_id,
            text=stats_text,
            inline_keyboard_markup=json.dumps([[back_button]])
        )
        
    except sqlite3.Error as e:
        print(f"Ошибка БД при получении статистики: {e}")
        bot.send_text(
            chat_id=chat_id,
            text="❌ Ошибка при загрузке статистики."
        )
        
    finally:
        if conn:
            conn.close()

def show_user_stats_options(chat_id):
    if not admin_users:
        bot.send_text(chat_id=chat_id, text="❌ Нет доступных пользователей для просмотра.")
        return
    
    keyboard = []
    admin_list = list(admin_users.items())
    
    for i in range(0, len(admin_list), 2):
        row = []
        # Первая кнопка в ряду
        email, name = admin_list[i]
        count = user_stats.get(email, 0)
        open_tickets = len([t for t in tickets.values() if t.get("creator") == email and t.get("status") == "Открыт"])
        row.append({
            "text": f"{name} ({count}|{open_tickets}🎫)",
            "callbackData": f"show_user_detail_{email}"
        })
        
        # Вторая кнопка в ряду (если есть)
        if i+1 < len(admin_list):
            email, name = admin_list[i+1]
            count = user_stats.get(email, 0)
            open_tickets = len([t for t in tickets.values() if t.get("creator") == email and t.get("status") == "Открыт"])
            row.append({
                "text": f"{name} ({count}|{open_tickets}🎫)",
                "callbackData": f"show_user_detail_{email}"
            })
        
        keyboard.append(row)
    
    keyboard.append([back_button])
    
    bot.send_text(
        chat_id=chat_id,
        text="👥 Выберите пользователя (запросы|открытые тикеты):",
        inline_keyboard_markup=json.dumps(keyboard)
    )

def show_all_users_stats(chat_id):
    if not admin_users:
        bot.send_text(chat_id=chat_id, text="❌ Нет данных о пользователях.")
        return
    
    stats_text = "📊 Статистика всех администраторов:\n\n"
    for email, name in admin_users.items():
        count = usage_stats.get(email, {}).get('count', 0) if usage_stats else 0
        stats_text += f"👤 {name}: {count} запросов\n"
    
    bot.send_text(
        chat_id=chat_id,
        text=stats_text,
        inline_keyboard_markup=json.dumps([
            [{"text": "⬅️ Назад", "callbackData": "admin_cmd_user_stats"}]
        ])
    )

def show_user_detail(chat_id, user_email):
    if user_email not in admin_users:
        bot.send_text(chat_id=chat_id, text="❌ Пользователь не найден.")
        return
    
    name = admin_users[user_email]
    count = user_stats.get(user_email, 0)
    # Считаем тикеты пользователя
    created_tickets = len([t for t in tickets.values() if t.get("creator") == user_email])
    open_tickets = len([t for t in tickets.values() if t.get("creator") == user_email and t.get("status") == "Открыт"])
    assigned_tickets = len([t for t in tickets.values() if t.get("assigned_to") == user_email and t.get("status") == "Открыт"])
    
    bot.send_text(
        chat_id=chat_id,
        text=f"📊 Детальная статистика:\n\n"
             f"👤 Имя: {name}\n"
             f"📧 Email: {user_email}\n"
             f"🔢 Всего запросов: {count}\n"
             f"🎫 Всего создано тикетов: {created_tickets}\n"
             f"🟢 Открытых тикетов: {open_tickets}\n"
             f"📌 Назначено тикетов: {assigned_tickets}",
        inline_keyboard_markup=json.dumps([
            [{"text": "⬅️ Назад к списку", "callbackData": "admin_cmd_user_stats"}]
        ])
    )

def show_all_users_stats(chat_id):
    if not usage_stats:
        bot.send_text(chat_id=chat_id, text="❌ Нет данных о пользователях.")
        return
    
    stats_text = "📊 Статистика всех пользователей:\n\n"
    for user_id, stats in sorted(usage_stats.items(), key=lambda x: x[1]['count'], reverse=True):
        stats_text += f"👤 {stats['name']}: {stats['count']} запросов\n"
    
    bot.send_text(
        chat_id=chat_id,
        text=stats_text,
        inline_keyboard_markup=json.dumps([
            [{"text": "⬅️ Назад", "callbackData": "admin_cmd_user_stats"}]
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
            [{"text": "⬅️ Назад", "callbackData": "user_cmd_/admin_panel", "style": "secondary"}]
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

def process_command(chat_id, command): #обработка всех команд
    command = command.lower().strip()
    
    # Если пользователь ввел любую команду во время создания тикета - очищаем состояние
    if chat_id in user_states and user_states[chat_id].get("state", "").startswith("awaiting_ticket"):
        if not command.startswith("/support") and command not in ["/back", "/cancel"]:
            del user_states[chat_id]
            bot.send_text(chat_id=chat_id, text="❌ Создание тикета отменено")
    
    # Очистка состояния создания события при вводе другой команды
    if chat_id in user_states and user_states[chat_id].get("state", "").startswith("awaiting_event"):
        if not command.startswith("/create_event") and command not in ["/back", "/cancel"]:
            del user_states[chat_id]
            bot.send_text(chat_id=chat_id, text="❌ Создание события отменено")
            
    # Обновляем статистику при каждой команде
    user_stats[chat_id] = user_stats.get(chat_id, 0) + 1
            
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
    elif command == "/my_stats":
        show_my_stats(chat_id)
    elif command == "/stats":
        if chat_id in admin_users:
            show_all_stats(chat_id)
        else:
            show_my_stats(chat_id)
    else:
        bot.send_text(chat_id=chat_id, text="Неизвестная команда. Введите /help")

def simulate_user_message(chat_id, text): #команда от пользователя
    processing_time
    bot.send_text(
        chat_id=chat_id,
        text=f"Вы выбрали команду: {text}"
    )
    process_command(chat_id, text)

def message_cb(bot, event): #обработка сообщений
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

def button_cb(bot, event): #обработка кнопок
    try:
        bot.answer_callback_query(
            query_id=event.data['queryId'],
            text="⌛ Обработка..."
        )
        time.sleep(0.1)

        chat_id = event.from_chat
        active_chats.add(chat_id)
        
        # Обновляем статистику при каждом нажатии кнопки
        user_stats[chat_id] = user_stats.get(chat_id, 0) + 1

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
                show_all_stats(chat_id)
            elif command == "all_stats":
                show_all_stats(chat_id)
            elif command == "confirm_broadcast":
                send_broadcast(chat_id)
            elif command == "cancel_broadcast":
                cancel_broadcast(chat_id)
                
        # Просмотр статистики
        elif callback_data == "user_cmd_/my_stats":
            show_my_stats(chat_id)
        elif callback_data == "admin_cmd_all_stats":
            show_all_stats(chat_id)

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