import os
import telebot
from flask import Flask, request
import requests

# Настройки
BOT_TOKEN = os.environ.get('BOT_TOKEN')
HF_SPACE_URL = "https://meolaai-psihobot.hf.space"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# Функция для общения с AI
def get_answer_from_huggingface(question):
    try:
        response = requests.post(
            f"{HF_SPACE_URL}/api/predict",
            json={"data": [question]},
            timeout=30
        )
        if response.status_code == 200:
            return response.json()["data"][0]
        else:
            return f"❌ Ошибка {response.status_code}"
    except Exception as e:
        return f"❌ Ошибка: {str(e)}"

# Обработчик команды /start
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

# Обработчик всех сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    bot.send_chat_action(message.chat.id, 'typing')
    answer = get_answer_from_huggingface(message.text)
    bot.reply_to(message, answer)

# ВАЖНО: Вебхук endpoint для Telegram
@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    return 'Bad request', 400

# Статус страница для Render
@app.route('/')
def home():
    return "🤖 Психобот работает! Используется вебхук.", 200

@app.route('/health')
def health():
    return "OK", 200

# Запуск приложения
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
