import os
import sys
import telebot
from flask import Flask, request
import requests
from gradio_client import Client
import threading
import time

# Принудительно сбрасываем буфер вывода
sys.stdout.flush()

# Настройки
BOT_TOKEN = os.environ.get('BOT_TOKEN')
HF_SPACE_URL = "https://meolaai-psihobot.hf.space"

print("🟢 ВЕРСИЯ 15: Добавляем уведомление о долгой обработке, ждем 3 секунды")
sys.stdout.flush()

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

def get_answer_from_huggingface(question):
    try:
        print(f"🔍 Запрос к AI: {question}")
        client = Client("meolaai/Psihobot")
        result = client.predict(
            user_question=question,
            api_name="/find_relevant_quote"
        )
        print(f"✅ Успешный ответ от AI")
        
        # Очищаем от всех HTML-тегов и лишних символов
        clean_result = (str(result)
            .replace('<strong>', '').replace('</strong>', '')
            .replace('<em>', '').replace('</em>', '')
            .replace('*', '')  # Убираем звездочки
            .replace('_', '')  # Убираем подчеркивания
            .replace('<br>', '\n')
            .replace('<br/>', '\n')
            .replace('<br />', '\n')
            .strip())  # Убираем пробелы в начале/конце
        
        return clean_result
        
    except Exception as e:
        print(f"❌ Ошибка AI: {e}")
        return f"❌ Ошибка: {str(e)}"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    print(f"🎯 Получен /start от {message.from_user.id}")
    sys.stdout.flush()
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
    print(f"📨 Текстовое сообщение: {message.text}")
    sys.stdout.flush()
    
    # Отправляем действие "печатает"
    bot.send_chat_action(message.chat.id, 'typing')
    
    # Флаг для отслеживания отправки уведомления
    delay_notification_sent = False
    
    def send_delay_notification():
        nonlocal delay_notification_sent
        time.sleep(3)  # Ждем 3 секунды
        if not delay_notification_sent:
            print("⏳ Отправляем уведомление о долгой обработке")
            sys.stdout.flush()
            bot.send_chat_action(message.chat.id, 'typing')
            bot.send_message(message.chat.id, "⏳ Ищу наиболее релевантные ответы... Это может занять некоторое время")
            delay_notification_sent = True
    
    # Запускаем таймер в отдельном потоке
    timer_thread = threading.Thread(target=send_delay_notification)
    timer_thread.daemon = True
    timer_thread.start()
    
    # Получаем ответ от AI
    answer = get_answer_from_huggingface(message.text)
    
    # Отмечаем, что уведомление больше не нужно
    delay_notification_sent = True
    
    # Отправляем ответ
    bot.reply_to(message, answer, disable_web_page_preview=True)
    print("✅ Ответ отправлен пользователю")
    sys.stdout.flush()

@app.route('/webhook', methods=['POST'])
def webhook():
    print("📍📍📍 ВЕБХУК ВЫЗВАН!")
    sys.stdout.flush()
    
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        print(f"📨 JSON: {json_string}")
        sys.stdout.flush()
        
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        print("✅ Сообщение обработано")
        sys.stdout.flush()
        return ''
    return 'Bad request', 400

@app.route('/')
def home():
    return "🤖 Бот работает!", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 Сервер запущен на порту {port}")
    sys.stdout.flush()
    app.run(host="0.0.0.0", port=port, debug=False)

