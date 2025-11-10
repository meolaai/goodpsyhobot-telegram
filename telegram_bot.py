import os
import telebot
from flask import Flask
import requests
import time

# === НАСТРОЙКИ ===
BOT_TOKEN = os.environ.get('BOT_TOKEN')
HF_SPACE_URL = "https://meolaai-psihobot.hf.space"

print(f"🔑 Токен: {'✅' if BOT_TOKEN else '❌'}")

# Создаем бота и сервер
bot = telebot.TeleBot(BOT_TOKEN)
server = Flask(__name__)

@server.route('/')
def home():
    return "🤖 Психобот @catpsybot работает!", 200

@server.route('/health')
def health():
    return "OK", 200

def get_answer_from_huggingface(question):
    try:
        response = requests.post(
            f"{HF_SPACE_URL}/api/predict",
            json={"data": [question]},
            timeout=30
        )
        if response.status_code == 200:
            return response.json()["data"][0]
        else:
            return f"❌ Ошибка {response.status_code}"
    except Exception as e:
        return f"❌ Ошибка: {str(e)}"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    print(f"✅ /start от {message.from_user.id}")
    bot.reply_to(message, "👋 Привет! Я Психобот. Задайте вопрос!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    print(f"📨 Сообщение: {message.text}")
    bot.send_chat_action(message.chat.id, 'typing')
    answer = get_answer_from_huggingface(message.text)
    bot.reply_to(message, answer)

# ЗАПУСКАЕМ БОТА СРАЗУ ЖЕ
def start_bot():
    print("🔄 ЗАПУСКАЕМ БОТА...")
    time.sleep(3)  # Уменьшили время ожидания
    try:
        print("🔄 Сбрасываем webhook...")
        bot.remove_webhook()
        time.sleep(1)
        print("✅ Webhook сброшен, запускаем polling...")
        
        # Тестируем подключение к Telegram API
        bot_info = bot.get_me()
        print(f"✅ Бот подключен: @{bot_info.username}")
        
        print("🎯 Начинаем слушать сообщения...")
        bot.infinity_polling(timeout=90, long_polling_timeout=90, restart_on_change=True)
        
    except Exception as e:
        print(f"❌ Ошибка при запуске бота: {e}")
        print("🔄 Перезапуск через 10 секунд...")
        time.sleep(10)
        start_bot()  # Перезапуск
    
    # Запускаем бота в основном потоке
    import threading
    bot_thread = threading.Thread(target=start_bot, daemon=True)
    bot_thread.start()
    print("✅ ПОТОК БОТА ЗАПУЩЕН")
    
    # Запускаем сервер
    port = int(os.environ.get("PORT", 10000))
    print(f"🌐 СЕРВЕР НА ПОРТУ {port}")
    server.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

