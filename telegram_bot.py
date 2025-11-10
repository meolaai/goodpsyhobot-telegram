import os
import telebot
import requests
import time

# Новый токен от нового бота
BOT_TOKEN = os.environ.get('BOT_TOKEN')
HF_SPACE_URL = "https://meolaai-psihobot.hf.space"

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "✅ Бот перезапущен! Тестируем Hugging Face...")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    print(f"📩 Получено: {message.text}")
    
    try:
        # Простой запрос к Hugging Face
        response = requests.post(
            f"{HF_SPACE_URL}/api/predict",
            json={"data": [message.text]},
            timeout=10
        )
        
        print(f"📡 Статус: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            bot.reply_to(message, f"✅ Ответ: {result['data'][0]}")
        else:
            bot.reply_to(message, f"❌ Ошибка {response.status_code}")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        bot.reply_to(message, f"❌ Ошибка: {e}")

print("🔄 Запускаем бота...")
time.sleep(5)

try:
    bot.remove_webhook()
    time.sleep(2)
    bot.infinity_polling()
    print("✅ Бот работает!")
except Exception as e:
    print(f"❌ Ошибка запуска: {e}")
