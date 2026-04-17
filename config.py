import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

WELCOME_TEXT = """
🏢 <b>Добро пожаловать!</b>

Мы рады, что вы обратились к нам.

📞 Оставьте свои контактные данные, и наш менеджер свяжется с вами!

👇 Нажмите кнопку ниже, чтобы начать.
"""

WELCOME_IMAGE = "welcome.jpg"
ASK_NAME = "👤 Введите ваше <b>имя</b>:"
ASK_PHONE = "📱 Введите <b>номер телефона</b> или нажмите «Поделиться контактом»:"
ASK_EMAIL = "📧 Введите ваш <b>email</b> (или «Пропустить»):"
ASK_MESSAGE = "💬 Оставьте <b>сообщение</b> (или «Пропустить»):"
THANK_YOU = """
✅ <b>Спасибо за обращение!</b>

👤 Имя: {name}
📱 Телефон: {phone}
📧 Email: {email}
💬 Сообщение: {message}

Наш менеджер свяжется с вами! 😊
"""
