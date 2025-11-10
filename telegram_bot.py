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

print("🟢 ВЕРСИЯ 21: Испаравляем ошибки")
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
        
        # ДОБАВЛЯЕМ ЗАГОЛОВОК ВИДЕО К КАЖДОЙ ССЫЛКЕ
        # Ищем все YouTube ссылки и добавляем к ним заголовок
        import re
        # Паттерн для поиска YouTube ссылок
        youtube_pattern = r'(https://youtu\.be/[\w?-]+)'
        
        # Добавляем заголовок к каждой ссылке
        def add_video_title(match):
            video_url = match.group(1)
            # Можно добавить любой заголовок, например:
            return f"🎬 Видео: {video_url}"
        
        # Применяем замену ко всем YouTube ссылкам
        final_result = re.sub(youtube_pattern, add_video_title, clean_result)
        
        return final_result
        
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
    
    # Флаги управления
    notification_sent = False
    notification_message_id = None
    processing_complete = False
    
    def keep_typing():
        """Постоянно обновляем индикатор печати"""
        while not processing_complete:
            bot.send_chat_action(message.chat.id, 'typing')
            time.sleep(3)  # Обновляем каждые 3 секунды
    
    def send_delay_notification():
        nonlocal notification_sent, notification_message_id
        time.sleep(5)  # Ждем 5 секунд
        if not processing_complete and not notification_sent:
            print("⏳ Отправляем уведомление о долгой обработке")
            sys.stdout.flush()
            sent_msg = bot.send_message(message.chat.id, "⏳ Ищу наиболее релевантные ответы...")
            notification_message_id = sent_msg.message_id
            notification_sent = True
    
    # Запускаем постоянный индикатор печати
    typing_thread = threading.Thread(target=keep_typing)
    typing_thread.daemon = True
    typing_thread.start()
    
    # Запускаем таймер для уведомления
    notification_thread = threading.Thread(target=send_delay_notification)
    notification_thread.daemon = True
    notification_thread.start()
    
    # Получаем ответ от AI
    answer = get_answer_from_huggingface(message.text)
    
    # Помечаем, что обработка завершена
    processing_complete = True
    
    # Если уведомление было отправлено - удаляем его
    if notification_sent and notification_message_id:
        try:
            print("🗑️ Удаляем уведомление")
            bot.delete_message(message.chat.id, notification_message_id)
            time.sleep(0.3)
        except Exception as e:
            print(f"❌ Ошибка при удалении уведомления: {e}")
    
    # ОТПРАВЛЯЕМ БЕЗ disable_web_page_preview - чтобы ссылки открывались
    bot.send_message(message.chat.id, answer)
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



