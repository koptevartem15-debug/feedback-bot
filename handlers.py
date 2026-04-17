import os
import re
import sqlite3
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import *
from keyboards import *

router = Router()

conn = sqlite3.connect("feedback.db")
cur = conn.cursor()
cur.execute("""
    CREATE TABLE IF NOT EXISTS feedbacks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER, username TEXT, name TEXT,
        phone TEXT, email TEXT, message TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")
conn.commit()

class Form(StatesGroup):
    name = State()
    phone = State()
    email = State()
    message = State()
    confirm = State()

async def send_welcome(chat_id, bot):
    if os.path.exists(WELCOME_IMAGE):
        await bot.send_photo(chat_id=chat_id, photo=FSInputFile(WELCOME_IMAGE),
            caption=WELCOME_TEXT, parse_mode="HTML", reply_markup=get_start_keyboard())
    else:
        await bot.send_message(chat_id=chat_id, text=WELCOME_TEXT,
            parse_mode="HTML", reply_markup=get_start_keyboard())

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, bot: Bot):
    await state.clear()
    await send_welcome(message.chat.id, bot)

@router.message(F.text == "❌ Отмена")
async def cancel(message: Message, state: FSMContext, bot: Bot):
    await state.clear()
    await message.answer("Отменено.", reply_markup=remove_keyboard())
    await send_welcome(message.chat.id, bot)

@router.callback_query(F.data == "leave_feedback")
async def start_form(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(Form.name)
    await callback.message.answer(ASK_NAME, parse_mode="HTML")

@router.callback_query(F.data == "contacts")
async def contacts(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "📍 <b>Контакты</b>\n\n📞 +7 (999) 123-45-67\n📧 info@company.com",
        parse_mode="HTML", reply_markup=get_back_keyboard())

@router.callback_query(F.data == "back_to_menu")
async def back(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    await state.clear()
    await send_welcome(callback.message.chat.id, bot)

@router.message(Form.name)
async def get_name(message: Message, state: FSMContext):
    if len(message.text.strip()) < 2:
        await message.answer("⚠️ Слишком короткое. Попробуйте ещё:")
        return
    await state.update_data(name=message.text.strip())
    await state.set_state(Form.phone)
    await message.answer(ASK_PHONE, parse_mode="HTML", reply_markup=get_phone_keyboard())

@router.message(Form.phone, F.contact)
async def get_phone_btn(message: Message, state: FSMContext):
    await state.update_data(phone=message.contact.phone_number)
    await state.set_state(Form.email)
    await message.answer(ASK_EMAIL, parse_mode="HTML", reply_markup=get_skip_keyboard())

@router.message(Form.phone)
async def get_phone_txt(message: Message, state: FSMContext):
    phone = message.text.strip()
    if not re.match(r'^[\+]?[0-9\s\-\(\)]{7,15}$', phone):
        await message.answer("⚠️ Неверный формат. Пример: +79991234567",
            reply_markup=get_phone_keyboard())
        return
    await state.update_data(phone=phone)
    await state.set_state(Form.email)
    await message.answer(ASK_EMAIL, parse_mode="HTML", reply_markup=get_skip_keyboard())

@router.message(Form.email, F.text == "⏭ Пропустить")
async def skip_email(message: Message, state: FSMContext):
    await state.update_data(email="Не указан")
    await state.set_state(Form.message)
    await message.answer(ASK_MESSAGE, parse_mode="HTML", reply_markup=get_skip_keyboard())

@router.message(Form.email)
async def get_email(message: Message, state: FSMContext):
    email = message.text.strip()
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        await message.answer("⚠️ Неверный email.", reply_markup=get_skip_keyboard())
        return
    await state.update_data(email=email)
    await state.set_state(Form.message)
    await message.answer(ASK_MESSAGE, parse_mode="HTML", reply_markup=get_skip_keyboard())

@router.message(Form.message, F.text == "⏭ Пропустить")
async def skip_msg(message: Message, state: FSMContext):
    await state.update_data(msg="Не указано")
    await show_confirm(message, state)

@router.message(Form.message)
async def get_msg(message: Message, state: FSMContext):
    await state.update_data(msg=message.text.strip())
    await show_confirm(message, state)

async def show_confirm(message, state):
    data = await state.get_data()
    await state.set_state(Form.confirm)
    text = (f"📋 <b>Проверьте данные:</b>\n\n"
            f"👤 {data['name']}\n📱 {data['phone']}\n"
            f"📧 {data['email']}\n💬 {data['msg']}\n\nВсё верно?")
    await message.answer(text, parse_mode="HTML", reply_markup=get_confirm_keyboard())

@router.callback_query(Form.confirm, F.data == "confirm")
async def confirm(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    await callback.answer("✅ Отправлено!")
    cur.execute(
        "INSERT INTO feedbacks (user_id,username,name,phone,email,message) VALUES (?,?,?,?,?,?)",
        (callback.from_user.id, callback.from_user.username,
         data['name'], data['phone'], data['email'], data['msg']))
    conn.commit()
    await callback.message.answer(
        THANK_YOU.format(name=data['name'], phone=data['phone'],
            email=data['email'], message=data['msg']),
        parse_mode="HTML", reply_markup=remove_keyboard())
    if ADMIN_CHAT_ID:
        try:
            await bot.send_message(ADMIN_CHAT_ID,
                f"🔔 <b>Новая заявка!</b>\n\n👤 {data['name']}\n"
                f"📱 {data['phone']}\n📧 {data['email']}\n💬 {data['msg']}",
                parse_mode="HTML")
        except: pass
    await callback.message.answer("🔙", reply_markup=get_back_keyboard())
    await state.clear()

@router.callback_query(Form.confirm, F.data == "restart")
async def restart(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await state.set_state(Form.name)
    await callback.message.answer(ASK_NAME, parse_mode="HTML")
