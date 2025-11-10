import os
import telebot
from flask import Flask, request
import requests

# Настройки
BOT_TOKEN = os.environ.get('BOT_TOKEN')
HF_SPACE_URL = "https://meolaai-psihobot.hf.space"

print("🟢 Бот запускается...")
print(f"🔑 Токен: {'✅ Есть' if BOT_TOKEN else '❌ Нет'}")

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# Функция для общения с AI
def get_answer_from_huggingface(question):
    try:
        print(f"🔍 Запрос к AI: {question}")
        response = requests.post(
            f"{HF_SPACE_URL}/api/predict",
            json={"data": [question]},
            timeout=30
        )
        print(f"📡 Ответ AI: статус {response.status_code}")
        if response.status_code == 200:
            return response.json()["data"][0]
        else:
            return f"❌ Ошибка {response.status_code}"
    except Exception as e:
        print(f"❌ Ошибка AI: {e}")
        return f"❌ Ошибка: {str(e)}"

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    print(f"🎯 Получен /start от {message.from_user.id}")
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
    print(f"📨 Сообщение от {message.from_user.id}: {message.text}")
    bot.send_chat_action(message.chat.id, 'typing')
    answer = get_answer_from_huggingface(message.text)
    print(f"📤 Отправляем ответ: {answer[:100]}...")
    bot.reply_to(message, answer)

# Вебхук endpoint для Telegram
@app.route('/webhook', methods=['POST'])
def webhook():
    print("📍 Получен запрос на /webhook")
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        print("✅ Сообщение обработано")
        return ''
    print("❌ Неверный content-type")
    return 'Bad request', 400

# Статус страница для Render
@app.route('/')
def home():
    print("🌐 Запрос к главной странице")
    return "🤖 Психобот работает! Используется вебхук.", 200

@app.route('/health')
def health():
    return "OK", 200

# Запуск приложения
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 Сервер запущен на порту {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
