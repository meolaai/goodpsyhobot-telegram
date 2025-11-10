import os
import sys
import telebot
from flask import Flask, request
import requests
from gradio_client import Client

# Принудительно сбрасываем буфер вывода
sys.stdout.flush()

# Настройки
BOT_TOKEN = os.environ.get('BOT_TOKEN')
HF_SPACE_URL = "https://meolaai-psihobot.hf.space"
API_URL = "https://meolaai-psihobot.hf.space/"  # просто основной URL

print("🟢 ВЕРСИЯ 12: разметка HTML")
sys.stdout.flush()

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

def get_answer_from_huggingface(question):
    try:
        print(f"🔍 Запрос к AI: {question}")
        sys.stdout.flush()
        
        client = Client("meolaai/Psihobot")
        print("✅ Клиент создан")
        sys.stdout.flush()
        
        result = client.predict(
            user_question=question,
            api_name="/find_relevant_quote"
        )
        print(f"✅ Успешный ответ от AI: {type(result)}")
        sys.stdout.flush()
        
        # Конвертируем HTML в Markdown для Telegram
        result_str = str(result)
        print(f"📄 Результат: {result_str[:200]}...")
        sys.stdout.flush()
        
        formatted_result = (result_str
            .replace('<strong>', '*').replace('</strong>', '*')
            .replace('<em>', '_').replace('</em>', '_')
            .replace('<br>', '\n')
            .replace('<br/>', '\n')
            .replace('<br />', '\n'))
        
        print("✅ Форматирование завершено")
        sys.stdout.flush()
        return formatted_result
        
    except Exception as e:
        print(f"❌ Ошибка AI: {e}")
        sys.stdout.flush()
        return f"❌ Ошибка: {str(e)}"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    print(f"🎯 Получен /start от {message.from_user.id}")
    sys.stdout.flush()
    welcome_text = "👋 Привет! Я Психобот 🤖"
    bot.reply_to(message, welcome_text)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    print(f"📨 Текстовое сообщение: {message.text}")
    sys.stdout.flush()
    bot.send_chat_action(message.chat.id, 'typing')
    answer = get_answer_from_huggingface(message.text)
    bot.reply_to(message, answer, parse_mode='HTML')

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

