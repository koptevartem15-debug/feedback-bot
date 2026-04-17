from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardRemove
)

def get_start_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Оставить заявку", callback_data="leave_feedback")],
        [InlineKeyboardButton(text="📍 Контакты", callback_data="contacts")]
    ])

def get_phone_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Поделиться контактом", request_contact=True)],
            [KeyboardButton(text="❌ Отмена")]
        ],
        resize_keyboard=True, one_time_keyboard=True
    )

def get_skip_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⏭ Пропустить")],
            [KeyboardButton(text="❌ Отмена")]
        ],
        resize_keyboard=True, one_time_keyboard=True
    )

def get_confirm_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm"),
            InlineKeyboardButton(text="🔄 Заново", callback_data="restart")
        ]
    ])

def get_back_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 В меню", callback_data="back_to_menu")]
    ])

def remove_keyboard():
    return ReplyKeyboardRemove()
