import os
import telebot
from flask import Flask
import requests
import time
from threading import Thread
from datetime import datetime

# === НАСТРОЙКИ ===
BOT_TOKEN = os.environ.get('BOT_TOKEN')
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
            <p><strong>Запросов к статусу:</strong> {request_count}</p>
        </div>
    </body>
    </html>
    """
    return status_html

@server.route('/health')
def health():
    return "OK", 200

def get_answer_from_huggingface(question):
    """Отправляет вопрос в Hugging Face и получает ответ"""
    try:
        print(f"🔍 Отправляем запрос в Hugging Face: {question}")
        
        api_url = f"{HF_SPACE_URL}/api/predict"
        print(f"🌐 API URL: {api_url}")
        
        data = {
            "data": [question]
        }
        
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "TelegramBot/1.0"
        }
        
        print(f"📤 Отправляем POST запрос...")
        response = requests.post(
            api_url,
            json=data,
            headers=headers,
            timeout=30
        )
        
        print(f"📡 Статус ответа: {response.status_code}")
        
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
    print("🔄 Запуск бота в отдельном потоке...")
    time.sleep(5)
    
    max_retries = 5
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            print(f"🔄 Попытка {retry_count + 1} запуска бота...")
            
            # Сбрасываем webhook и запускаем polling
            bot.remove_webhook()
            time.sleep(2)
            
            print("✅ Запускаем infinity_polling...")
            bot.infinity_polling(
                skip_pending=True, 
                timeout=60, 
                long_polling_timeout=60,
                restart_on_change=True
            )
            print("✅ Бот успешно запущен!")
            break
            
        except Exception as e:
            retry_count += 1
            print(f"❌ Ошибка при запуске бота (попытка {retry_count}): {e}")
            
            if retry_count < max_retries:
                wait_time = 10 * retry_count
                print(f"⏳ Ждем {wait_time} секунд перед повторной попыткой...")
                time.sleep(wait_time)
            else:
                print("❌ Достигнуто максимальное количество попыток запуска бота")

if __name__ == "__main__":
    print("🚀 Запускаем сервис...")
    print(f"🔗 HF URL: {HF_SPACE_URL}")
    print(f"🔑 Токен: {'✅' if BOT_TOKEN else '❌'}")
    
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN не найден!")
        exit(1)
    
    # Запускаем бота в отдельном потоке
    bot_thread = Thread(target=run_bot, daemon=True)
    bot_thread.start()
    print("✅ Поток бота запущен")
    
    # Запускаем Flask сервер (это ОСНОВНОЙ процесс)
    port = int(os.environ.get("PORT", 10000))
    print(f"🌐 Запускаем Flask сервер на порту {port}")
    server.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
