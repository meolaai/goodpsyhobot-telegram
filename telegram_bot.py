import os
import telebot
from flask import Flask
import requests
import json
from threading import Thread

# === НАСТРОЙКИ ===
BOT_TOKEN = os.environ.get('BOT_TOKEN')
HF_SPACE_URL = "https://huggingface.co/spaces/meolaai/Psihobot"

# Создаем бота
bot = telebot.TeleBot(BOT_TOKEN)

# Создаем Flask приложение для работы с портом
server = Flask(__name__)

@server.route('/')
def home():
    return "🤖 Психобот активен!", 200

def get_answer_from_huggingface(question):
    """Отправляет вопрос в Hugging Face и получает ответ"""
    try:
        # Отправляем запрос к Hugging Face Space
        response = requests.post(
            f"{HF_SPACE_URL}/api/predict",
            json={"data": [question]},
            headers={"Content-Type": "application/json"},
            timeout=30  # добавляем таймаут
        )
        
        if response.status_code == 200:
            result = response.json()
            return result["data"][0]
        else:
            return f"❌ Ошибка соединения с Hugging Face (код: {response.status_code})"
            
    except Exception as e:
        return f"❌ Произошла ошибка: {str(e)}"

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = """
👋 Привет! Я Психобот 🤖

Задайте мне ваш вопрос или опишите проблему, и я найду подходящие цитаты с видеофрагментами.

💡 Примеры вопросов:
• "апатия и нет сил"
• "стресс на работе" 
• "кризис в жизни"

Просто напишите ваш вопрос — и я найду ответ!
    """
    bot.reply_to(message, welcome_text)

# Обработчик всех текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    # Показываем, что бот печатает
    bot.send_chat_action(message.chat.id, 'typing')
    
    # Получаем ответ (пока тестовый)
    answer = get_answer_from_huggingface(message.text)
    
    # Отправляем ответ пользователю
    bot.reply_to(message, answer, parse_mode='HTML')

# === ЗАПУСК ===
def run():
    # Запускаем бота в отдельном потоке
    bot_thread = Thread(target=bot.infinity_polling)
    bot_thread.daemon = True
    bot_thread.start()
    print("🤖 Бот запущен в фоновом режиме...")

    # Запускаем веб-сервер для Render
    port = int(os.environ.get("PORT", 10000))
    server.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    run()

