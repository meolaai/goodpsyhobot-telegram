python
import os
import telebot
from flask import Flask

# === НАСТРОЙКИ ===
BOT_TOKEN = os.environ.get('BOT_TOKEN', "ВАШ_ТОКЕН_ЗДЕСЬ")
HF_SPACE_URL = "https://ваш-логин-ваш-psychobot.hf.space"

# Создаем бота
bot = telebot.TeleBot(BOT_TOKEN)

# Создаем Flask приложение для работы с портом
server = Flask(__name__)

@server.route('/')
def home():
    return "🤖 Психобот активен!", 200

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = """
👋 Привет! Я Психобот 🤖
Задайте мне ваш вопрос...
    """
    bot.reply_to(message, welcome_text)

# Обработчик всех текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    # Показываем, что бот печатает
    bot.send_chat_action(message.chat.id, 'typing')
    # Временно заглушаем вызов к Hugging Face для теста
    answer = f"Тестовый ответ на: {message.text}"
    bot.reply_to(message, answer, parse_mode='HTML')

# === ЗАПУСК ===
def run():
    # Запускаем бота в отдельном потоке, чтобы он не блокировал основной
    from threading import Thread
    bot_thread = Thread(target=bot.infinity_polling)
    bot_thread.daemon = True
    bot_thread.start()
    print("🤖 Бот запущен в фоновом режиме...")

    # Запускаем веб-сервер, который займет порт для Render
    port = int(os.environ.get("PORT", 10000))
    server.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    run()
