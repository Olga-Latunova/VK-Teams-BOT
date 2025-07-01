import json
from bot.bot import Bot
from bot.handler import MessageHandler, BotButtonCommandHandler

TOKEN = "001.1806729577.0340071044:1011814127"  # your token here
bot = Bot(token=TOKEN)

def buttons_answer_cb(bot, event):
    if event.data['callbackData'] == "call_back_id_2":
        bot.answer_callback_query(
            query_id=event.data['queryId'],
            text="Hey! It's a working button 2.",
            show_alert=True
        )
    elif event.data['callbackData'] == "call_back_id_3":
        bot.answer_callback_query(
            query_id=event.data['queryId'],
            text="Hey! It's a working button 3.",
            show_alert=False
        )

def message_cb(bot, event):
    text = event.text.lower().strip()  # Нормализуем текст команды
    
    if text == "/help":  # Кнопки только на /help
        bot.send_text(
            chat_id=event.from_chat,
            text="Выберите действие:",
            inline_keyboard_markup=json.dumps([[
                {"text": "Контакты", "url": "https://105.ooo/#rec758397817"},
                {"text": "Новости", "url": "https://t.me/IT_105Koderline"},
                {"text": "О нас", "url": "https://105.ooo/#rec756415377"}
            ]])
        )
    else:
        bot.send_text(
            chat_id=event.from_chat,
            text="Напишите /help для вывода меню"  # Стандартный ответ
        )

bot.dispatcher.add_handler(MessageHandler(callback=message_cb))
bot.dispatcher.add_handler(BotButtonCommandHandler(callback=buttons_answer_cb))

bot.start_polling()
bot.idle()
