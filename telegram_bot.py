import os
import telebot
import requests
import json

# === НАСТРОЙКИ ===
# Вставьте сюда токен из @BotFather
BOT_TOKEN = os.environ.get('BOT_TOKEN', "ВАШ_ТОКЕН_ЗДЕСЬ")
# Вставьте сюда ссылку на ваш Hugging Face Space
HF_SPACE_URL = "https://ваш-логин-ваш-psychobot.hf.space"

# Создаем бота
bot = telebot.TeleBot(BOT_TOKEN)

def get_answer_from_huggingface(question):
    """Отправляет вопрос в Hugging Face и получает ответ"""
    try:
        # Отправляем запрос к Hugging Face Space
        response = requests.post(
            f"{HF_SPACE_URL}/api/predict",
            json={"data": [question]},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            return result["data"][0]
        else:
            return "❌ Ошибка соединения с ботом"
            
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
• "проблемы в отношениях"

Просто напишите ваш вопрос — и я найду ответ!
    """
    bot.reply_to(message, welcome_text)

# Обработчик всех текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    # Показываем, что бот печатает
    bot.send_chat_action(message.chat.id, 'typing')
    
    # Получаем ответ от Hugging Face
    answer = get_answer_from_huggingface(message.text)
    
    # Отправляем ответ пользователю
    bot.reply_to(message, answer, parse_mode='HTML')

# Запускаем бота
print("🤖 Бот запущен...")
bot.infinity_polling()