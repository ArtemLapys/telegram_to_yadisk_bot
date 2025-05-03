# auth.py
from aiogram import types
from aiogram.fsm.context import FSMContext
from config import TOKENS

async def cmd_login(message: types.Message, state: FSMContext):
    token = message.text.replace("/login ", "").strip()
    if token in TOKENS:
        await state.update_data(authenticated=True, owner=TOKENS[token])
        await message.answer(f"✅ Авторизация успешна! Добро пожаловать, {TOKENS[token]}!\n\nЗагрузить файл с помощью `/upload` или узнайте больше о возможностях бота `/help`.",parse_mode="Markdown")
        await message.delete()

    else:
        await message.reply("❌ Неверный токен. Попробуйте снова.")

async def check_auth(message: types.Message, state: FSMContext) -> bool:
    data = await state.get_data()
    if not data.get("authenticated"):
        await message.answer("🔒 Введите токен с помощью `/login <токен>`.", parse_mode="Markdown")
        return False
    return True
