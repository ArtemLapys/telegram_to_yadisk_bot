# Команда /upload и логика выбора папки
from aiogram import types
from aiogram.fsm.context import FSMContext
from states import Form
from services.yadisk_service import get_yadisk, get_current_path_and_subfolders
from auth import check_auth
from datetime import datetime

async def cmd_upload(message: types.Message, state: FSMContext):
    if not await check_auth(message, state):
        return

    y = get_yadisk()
    if not y:
        await message.answer("❌ Не удалось подключиться к Я.Диску.")
        return

    # Устанавливаем начальную папку
    await state.update_data(folder_path="/")

    # Получаем готовый текст из yadisk_service.py
    response_message = await get_current_path_and_subfolders(state)

    # Проверяем, что response_message — это строка
    if isinstance(response_message, tuple):
        response_message = response_message[0]  # Извлекаем строку из кортежа

    # Отправляем сообщение пользователю
    await message.answer(response_message)

    # Устанавливаем состояние ожидания выбора папки
    await state.set_state(Form.waiting_for_folder)
    await state.update_data(last_interaction=datetime.now())