import os
import telebot
from flask import Flask
import requests
import time
from threading import Thread
from datetime import datetime

# === НАСТРОЙКИ ===
BOT_TOKEN = os.environ.get('BOT_TOKEN')
# ⚠️ ПРАВИЛЬНЫЙ URL!
HF_SPACE_URL = "https://meolaai-psihobot.hf.space"

# Создаем бота
bot = telebot.TeleBot(BOT_TOKEN)

# Создаем Flask приложение
server = Flask(__name__)

# Переменные для статуса
start_time = datetime.now()
request_count = 0

@server.route('/')
def home():
    global request_count
    request_count += 1
    
    status_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>🤖 Психобот Статус</title>
        <meta charset="utf-8">
    </head>
    <body>
        <div>
            <h1>🤖 Психобот - Статус системы</h1>
            <p><strong>Статус:</strong> 🟢 АКТИВЕН</p>
            <p><strong>Время запуска:</strong> {start_time.strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Hugging Face:</strong> {HF_SPACE_URL}</p>
            <p><strong>Токен бота:</strong> {'✅ Установлен' if BOT_TOKEN else '❌ НЕ НАЙДЕН'}</p>
        </div>
    </body>
    </html>
    """
    return status_html

def get_answer_from_huggingface(question):
    """Отправляет вопрос в Hugging Face и получает ответ"""
    try:
        print(f"🔍 Отправляем запрос в Hugging Face: {question}")
        
        # Правильный URL
        api_url = f"{HF_SPACE_URL}/api/run"
        print(f"🌐 API URL: {api_url}")
        
        # Данные для запроса
        data = {
            "data": [question]
        }
        
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "TelegramBot/1.0"
        }
        
        # Делаем запрос с подробным логированием
        print(f"📤 Отправляем POST запрос...")
        response = requests.post(
            api_url,
            json=data,
            headers=headers,
            timeout=30
        )
        
        print(f"📡 Статус ответа: {response.status_code}")
        print(f"📄 Заголовки ответа: {dict(response.headers)}")
        print(f"📝 Тело ответа: {response.text[:500]}...")  # Первые 500 символов
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Успешный ответ от Hugging Face")
            return result["data"][0]
        else:
            error_msg = f"❌ Ошибка API Hugging Face (код: {response.status_code})"
            print(error_msg)
            return error_msg
            
    except requests.exceptions.Timeout:
        error_msg = "❌ Таймаут при подключении к Hugging Face"
        print(error_msg)
        return error_msg
    except requests.exceptions.ConnectionError:
        error_msg = "❌ Ошибка соединения с Hugging Face"
        print(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"❌ Неожиданная ошибка: {str(e)}"
        print(error_msg)
        return error_msg

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = """👋 Привет! Я Психобот 🤖

Задайте мне ваш вопрос или опишите проблему, и я найду подходящие цитаты с видеофрагментами.

💡 Примеры вопросов:
• "апатия и нет сил"
• "стресс на работе" 
• "кризис в жизни"

Просто напишите ваш вопрос — и я найду ответ!"""
    bot.reply_to(message, welcome_text)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    bot.send_chat_action(message.chat.id, 'typing')
    answer = get_answer_from_huggingface(message.text)
    bot.reply_to(message, answer, parse_mode='HTML')

def run_bot():
    """Запускает бота с защитой от конфликтов"""
    print("🔄 Запуск бота...")
    time.sleep(10)  # Увеличили ожидание
    
    try:
        # Сбрасываем ВСЕ предыдущие соединения
        bot.remove_webhook()
        time.sleep(5)
        
        # Запускаем с skip_pending
        bot.infinity_polling(skip_pending=True, timeout=120, long_polling_timeout=120)
        print("✅ Бот успешно запущен!")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        time.sleep(30)
        run_bot()  # Перезапускаем

if __name__ == "__main__":
    print("🚀 Запускаем сервис...")
    print(f"🔗 HF URL: {HF_SPACE_URL}")
    print(f"🔑 Токен: {'✅' if BOT_TOKEN else '❌'}")
    
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN не найден!")
        exit(1)
    
    # Запускаем бота
    bot_thread = Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Запускаем сервер
    port = int(os.environ.get("PORT", 10000))
    print(f"🌐 Сервер на порту {port}")
    server.run(host="0.0.0.0", port=port, debug=False)



