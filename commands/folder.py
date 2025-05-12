# Переходы между папками, выбор папки
from aiogram import types
from aiogram.fsm.context import FSMContext
from auth import check_auth
from datetime import datetime, timedelta
from config import YADISK_TOKEN
import yadisk
import os
from states import Form
from services.yadisk_service import get_current_path_and_subfolders  
from keyboards import folder_keyboard
import logging

async def handle_folder(message: types.Message, state: FSMContext, folder_index=None):
    if not await check_auth(message, state):
        return  # Выход, если пользователь не авторизован

    # Проверка времени последнего взаимодействия
    data = await state.get_data()
    last_interaction = data.get("last_interaction")
    if last_interaction and datetime.now() - last_interaction > timedelta(minutes=5):
        await message.answer("❗ Время для выбора папки истекло. Пожалуйста, используйте команду /upload, чтобы снова выбрать папку.", parse_mode="Markdown")
        return

    y = yadisk.YaDisk(token=YADISK_TOKEN)
    if not y.check_token():
        logging.error("Ошибка: Из /folder не подключились к Я.Диску. Неверный OAuth-токен.")
        await message.answer("❌ Ошибка: Неверный OAuth-токен.")
        return

    # Получаем текущий путь папки
    current_folder = data.get("folder_path", "/")
    
    # Если folder_index передан через CallbackQuery
    if folder_index is not None:
        folder_index = folder_index.strip()
    else:
        folder_index = message.text.replace("/folder ", "").strip()

    # Если это команда для возврата на уровень выше
    if folder_index == '0':
        parent_folder = os.path.dirname(current_folder.rstrip('/'))  # Получаем родительскую папку
        if not parent_folder:
            parent_folder = '/'
        await state.update_data(folder_path=parent_folder)
        await message.answer(f"📂 Вы вернулись в папку: {parent_folder}")
        message_text, current_path = await get_current_path_and_subfolders(state)
        await message.answer(message_text, parse_mode="Markdown")
        return

    # Получаем список папок
    folders = [folder["name"] for folder in y.listdir(current_folder) if folder["type"] == "dir"]

    # Проверяем правильность введенного индекса
    if not folder_index.isdigit() or int(folder_index) > len(folders) or int(folder_index) < 1:
        await message.answer("❌ Ошибка: Неверный номер папки. Попробуйте снова или создайте новую (`/newfolder [имя]`).", parse_mode="Markdown")
        return

    selected_folder = f"{current_folder.rstrip('/')}/{folders[int(folder_index) - 1]}"

    # Проверка на существование папки
    if not y.exists(selected_folder):
        await message.answer(f"❌ Ошибка: Папка '{selected_folder}' не существует.")
        return

    # Обновляем текущую папку
    await state.update_data(folder_path=selected_folder)

    # Получаем подпапки
    message_text, current_path = await get_current_path_and_subfolders(state)
    await message.answer(message_text, parse_mode="Markdown")

    # Устанавливаем состояние ожидания файла
    await state.set_state(Form.waiting_for_file)
    await state.update_data(last_interaction=datetime.now())
