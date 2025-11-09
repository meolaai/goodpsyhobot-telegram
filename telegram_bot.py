import os
import telebot
from flask import Flask
import time
from threading import Thread

# === НАСТРОЙКИ ===
BOT_TOKEN = os.environ.get('BOT_TOKEN')

# Создаем бота
bot = telebot.TeleBot(BOT_TOKEN)

# Создаем Flask приложение
server = Flask(__name__)

@server.route('/')
def home():
    return "🤖 Психобот активен!", 200

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = "👋 Привет! Я Психобот 🤖"
    bot.reply_to(message, welcome_text)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    bot.send_chat_action(message.chat.id, 'typing')
    answer = f"Тестовый ответ на: {message.text}"
    bot.reply_to(message, answer, parse_mode='HTML')

def run_bot():
    """Запускает бота с защитой от конфликтов"""
    print("🔄 Безопасный запуск бота...")
    time.sleep(5)  # Ждем завершения старых процессов
    
    try:
        # Ключевой параметр для решения 409 ошибки
        bot.infinity_polling(skip_pending=True, timeout=90)
        print("✅ Бот успешно запущен!")
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
        time.sleep(30)
        run_bot()  # Перезапускаем при ошибке

if __name__ == "__main__":
    print("🚀 Запускаем сервис...")
    
    # Запускаем бота в отдельном потоке
    bot_thread = Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Запускаем Flask сервер
    port = int(os.environ.get("PORT", 10000))
    print(f"🌐 Веб-сервер запущен на порту {port}")
    server.run(host="0.0.0.0", port=port, debug=False)
