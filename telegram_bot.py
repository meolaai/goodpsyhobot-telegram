import os
import telebot
from flask import Flask
import requests
import time

# === НАСТРОЙКИ ===
BOT_TOKEN = os.environ.get('BOT_TOKEN')
HF_SPACE_URL = "https://meolaai-psihobot.hf.space"

bot = telebot.TeleBot(BOT_TOKEN)
server = Flask(__name__)

@server.route('/')
def home():
    return "🤖 Психобот работает! Порт открыт.", 200

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "✅ Бот работает! Отправьте мне вопрос.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        response = requests.post(
            f"{HF_SPACE_URL}/api/predict",
            json={"data": [message.text]},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            bot.reply_to(message, result['data'][0])
        else:
            bot.reply_to(message, f"❌ Ошибка {response.status_code}")
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")

# Простой запуск
if __name__ == "__main__":
    print("🚀 Запускаем сервис...")
    
    # Запускаем бота в фоне
    def start_bot():
        time.sleep(10)
        try:
            bot.remove_webhook()
            bot.infinity_polling(skip_pending=True)
        except Exception as e:
            print(f"❌ Бот: {e}")
    
    import threading
    threading.Thread(target=start_bot, daemon=True).start()
    
    # Запускаем сервер (это важно для порта)
    port = int(os.environ.get("PORT", 10000))
    print(f"🌐 Сервер на порту {port}")
    server.run(host="0.0.0.0", port=port, debug=False)
