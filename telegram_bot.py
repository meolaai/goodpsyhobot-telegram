import os
import telebot
from flask import Flask, request
import requests

print("🟢 ВЕРСИЯ 2: Код с диагностикой API")

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
        
        # Проверяем, доступен ли Space
        space_status_url = f"{HF_SPACE_URL}"
        print(f"🌐 Проверяем доступность Space...")
        
        # Правильный URL для API
        api_url = f"{HF_SPACE_URL}/api/predict"
        print(f"🌐 Используем API URL: {api_url}")
        
        # Данные для запроса
        data = {"data": [question]}
        print(f"📦 Данные запроса: {data}")
        
        # Отправляем запрос
        response = requests.post(
            api_url,
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=60  # Увеличиваем таймаут
        )
        
        print(f"📡 HTTP статус ответа: {response.status_code}")
        print(f"📄 Тело ответа: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Успешный ответ от API")
            return result["data"][0]
        elif response.status_code == 404:
            return f"❌ Ошибка 404: API не найден. Проверьте URL: {api_url}"
        else:
            return f"❌ Ошибка HTTP {response.status_code}: {response.text}"
            
    except requests.exceptions.Timeout:
        error_msg = "❌ Таймаут при подключении к AI (более 60 секунд)"
        print(error_msg)
        return error_msg
    except requests.exceptions.ConnectionError:
        error_msg = f"❌ Ошибка соединения. Не удается достичь {HF_SPACE_URL}"
        print(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"❌ Неожиданная ошибка: {str(e)}"
        print(error_msg)
        return error_msg
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
    print("✅ Ответ на /start отправлен")

# Обработчик всех сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    print(f"📨 Текстовое сообщение от {message.from_user.id}: {message.text}")
    print(f"🔍 Начинаем обработку через AI...")
    
    bot.send_chat_action(message.chat.id, 'typing')
    answer = get_answer_from_huggingface(message.text)
    
    print(f"📤 Отправляем ответ пользователю: {answer[:100]}...")
    bot.reply_to(message, answer)
    print("✅ Ответ отправлен")

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




