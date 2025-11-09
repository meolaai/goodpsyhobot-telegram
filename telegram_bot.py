import os
import telebot
from flask import Flask
import requests
import time
from threading import Thread

# === НАСТРОЙКИ ===
BOT_TOKEN = os.environ.get('BOT_TOKEN')
# ⚠️ ЗАМЕНИТЕ на ваш реальный URL Hugging Face Space!
HF_SPACE_URL = "https://huggingface.co/spaces/meolaai/Psihobot"

# Создаем бота
bot = telebot.TeleBot(BOT_TOKEN)

# Создаем Flask приложение
server = Flask(__name__)

@server.route('/')
def home():
    return "🤖 Психобот активен!", 200

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
            timeout=60  # Увеличиваем таймаут до 60 секунд
        )
        
        print(f"📡 Ответ от Hugging Face: статус {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Успешный ответ от Hugging Face")
            return result["data"][0]
        else:
            error_msg = f"❌ Ошибка API Hugging Face (код: {response.status_code})"
            print(error_msg)
            print(f"📄 Тело ответа: {response.text}")
            return error_msg
            
    except requests.exceptions.Timeout:
        error_msg = "❌ Таймаут при подключении к Hugging Face (более 60 секунд)"
        print(error_msg)
        return error_msg
    except requests.exceptions.ConnectionError:
        error_msg = "❌ Ошибка соединения с Hugging Face - проверьте URL"
        print(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"❌ Неожиданная ошибка: {str(e)}"
        print(error_msg)
        return error_msg

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = """
👋 Привет! Я Психобот 🤖

Задайте мне ваш вопрос или опишите проблему, и я найду подходящие цитаты с видеофрагментами.

💡 Примеры вопросов:
• "апатия и нет сил"
• "стресс на работе" 
• "почему я молодец"

Просто напишите ваш вопрос — и я найду ответ!
    """
    bot.reply_to(message, welcome_text)

# Обработчик всех текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    # Показываем, что бот печатает
    bot.send_chat_action(message.chat.id, 'typing')
    
    print(f"📩 Получен вопрос от пользователя: {message.text}")
    
    # Получаем ответ от Hugging Face
    answer = get_answer_from_huggingface(message.text)
    
    print(f"📤 Отправляем ответ пользователю: {answer[:100]}...")
    
    # Отправляем ответ пользователю
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
        print(f"❌ Ошибка запуска бота: {e}")
        print("🔄 Перезапуск через 30 секунд...")
        time.sleep(30)
        run_bot()  # Перезапускаем при ошибке

if __name__ == "__main__":
    print("🚀 Запускаем сервис Психобот...")
    print(f"🔗 URL Hugging Face: {HF_SPACE_URL}")
    print(f"🔑 Токен бота: {'установлен' if BOT_TOKEN else 'НЕ НАЙДЕН!'}")
    
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
    server.run(host="0.0.0.0", port=port, debug=False)
