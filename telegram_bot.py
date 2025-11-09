import os
import telebot
from flask import Flask
import requests
import time
from threading import Thread
from datetime import datetime

# === НАСТРОЙКИ ===
BOT_TOKEN = os.environ.get('BOT_TOKEN')
# ⚠️ ИСПРАВЛЕННЫЙ URL!
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
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
            .container {{ background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .status {{ color: #2ecc71; font-weight: bold; }}
            .error {{ color: #e74c3c; }}
            .info {{ color: #3498db; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 Психобот - Статус системы</h1>
            
            <h2>📊 Основная информация:</h2>
            <p><strong>Статус:</strong> <span class="status">🟢 АКТИВЕН</span></p>
            <p><strong>Время запуска:</strong> {start_time.strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Время работы:</strong> {str(datetime.now() - start_time).split('.')[0]}</p>
            <p><strong>Запросов к статусу:</strong> {request_count}</p>
            
            <h2>🔗 Подключения:</h2>
            <p><strong>Telegram бот:</strong> <span class="status">@GoodPsyhobot</span></p>
            <p><strong>Hugging Face Space:</strong> <span class="info">{HF_SPACE_URL}</span></p>
            <p><strong>Токен бота:</strong> {'<span class="status">✅ Установлен</span>' if BOT_TOKEN else '<span class="error">❌ НЕ НАЙДЕН</span>'}</p>
            
            <h2>⚙️ Техническая информация:</h2>
            <p><strong>Сервис:</strong> Render.com</p>
            <p><strong>Текущее время:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <hr>
            <p><em>🤖 Бот работает в фоновом режиме и обрабатывает сообщения в Telegram</em></p>
        </div>
    </body>
    </html>
    """
    return status_html

@server.route('/health')
def health_check():
    return "OK", 200

def get_answer_from_huggingface(question):
    """Отправляет вопрос в Hugging Face и получает ответ"""
    try:
        print(f"🔍 Отправляем запрос в Hugging Face: {question}")
        
        # Данные для запроса
        data = {
            "data": [question]
        }
        
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "TelegramBot/1.0"
        }
        
        # Делаем запрос с таймаутом
        response = requests.post(
            f"{HF_SPACE_URL}/api/predict",
            json=data,
            headers=headers,
            timeout=60
        )
        
        print(f"📡 Ответ от Hugging Face: статус {response.status_code}")
        
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

# Обработчик команды /start (ИСПРАВЛЕННЫЙ - без обрезания)
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = """👋 Привет! Я Психобот 🤖

Задайте мне ваш вопрос или опишите проблему, и я найду подходящие цитаты с видеофрагментами.

💡 Примеры вопросов:
• "апатия и нет сил"
• "стресс на работе" 
• "кризис в жизни"
• "проблемы в отношениях"

Просто напишите ваш вопрос — и я найду ответ!"""
    bot.reply_to(message, welcome_text)

# Обработчик всех текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    bot.send_chat_action(message.chat.id, 'typing')
    
    print(f"📩 Получен вопрос от пользователя: {message.text}")
    
    answer = get_answer_from_huggingface(message.text)
    
    print(f"📤 Отправляем ответ пользователю: {answer[:100]}...")
    
    bot.reply_to(message, answer, parse_mode='HTML')

def run_bot():
    """Запускает бота с защитой от конфликтов"""
    print("🔄 Безопасный запуск бота...")
    time.sleep(5)
    
    try:
        bot.infinity_polling(skip_pending=True, timeout=90)
        print("✅ Бот успешно запущен!")
    except Exception as e:
        print(f"❌ Ошибка запуска бота: {e}")
        print("🔄 Перезапуск через 30 секунд...")
        time.sleep(30)
        run_bot()

if __name__ == "__main__":
    print("🚀 Запускаем сервис Психобот...")
    print(f"🔗 URL Hugging Face: {HF_SPACE_URL}")
    print(f"🔑 Токен бота: {'установлен' if BOT_TOKEN else 'НЕ НАЙДЕН!'}")
    print(f"⏰ Время запуска: {start_time}")
    
    if not BOT_TOKEN:
        print("❌ КРИТИЧЕСКАЯ ОШИБКА: BOT_TOKEN не найден!")
        exit(1)
    
    # Запускаем бота в отдельном потоке
    bot_thread = Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Запускаем Flask сервер
    port = int(os.environ.get("PORT", 10000))
    print(f"🌐 Веб-сервер запущен на порту {port}")
    print(f"📊 Статус доступен по URL: https://ваш-сервис.onrender.com")
    server.run(host="0.0.0.0", port=port, debug=False)
