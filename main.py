from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])  # Разрешаем оба метода
def webhook():
    if request.method == 'GET':
        return jsonify({"status": "ready"})  # Ответ для проверки VK Teams
    
    # Обработка POST-запроса от бота
    data = request.json
    chat_id = data['chat']['chatId']
    text = data['text'].lower()

    if text == "/help":
        response_text = "📜 Команды:\n/help\n/about\n/news\n/contacts"
    else:
        response_text = "Напишите /help"

    # Отправка ответа (ваш код здесь)
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

#----------------------------------------------

from flask import Flask, request, jsonify
import requests
import logging

app = Flask(__name__)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Конфигурация бота
BOT_TOKEN = ""  # Замените на реальный токен!
API_URL = "https://api.myteam.mail.ru/bot/v1"  # Или с internal для корпоративных ботов

def send_message(chat_id, text):
    """Отправка сообщения через API VK Teams"""
    try:
        response = requests.post(
            f"{API_URL}/messages/sendText",
            json={"chatId": chat_id, "text": text},
            headers={"Authorization": f"Bearer {BOT_TOKEN}"}
        )
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Ошибка отправки: {e}")
        return False

@app.route('/', methods=['GET', 'POST'])
def webhook():
    # Логируем входящий запрос
    logger.info(f"Request: {request.method} {request.json}")

    # Проверка вебхука (GET-запрос)
    if request.method == 'GET':
        return jsonify({"status": "ready"})

    # Обработка команд от пользователя
    data = request.json
    chat_id = data['chat']['chatId']
    user_text = data['text'].strip().lower()

    # Обработка команд
    if user_text == "/help":
        response_text = """📜 Доступные команды:
/help - Справка
/about - О компании
/news - Последние новости
/contacts - Контакты поддержки"""
    
    elif user_text == "/about":
        response_text = "🚀 105 Кодерлайн - IT-компания, партнер 1С\nСайт: https://кодерлайн.рф"
    
    elif user_text == "/news":
        response_text = "🔔 Последние новости:\n1. Запуск нового проекта\n2. Обновление API\nЧитать: vk.com/coderline"
    
    elif user_text == "/contacts":
        response_text = """📞 Контакты:
- Техподдержка: support@coderline.ru
- Отдел продаж: +7 (XXX) XXX-XX-XX (доб. 105)"""
    
    else:
        response_text = "Неизвестная команда. Напишите /help для списка команд"

    # Отправка ответа
    if not send_message(chat_id, response_text):
        logger.error("Не удалось отправить сообщение!")

    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
