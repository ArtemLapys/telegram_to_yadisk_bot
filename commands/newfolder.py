# Создание новых папок
from aiogram import types
from aiogram.fsm.context import FSMContext
from auth import check_auth
from config import YADISK_TOKEN
from services.yadisk_service import check_or_create_folder
from datetime import datetime
import yadisk
import logging
from states import Form

# Обработчик создания новой папки
async def handle_new_folder(message: types.Message, state: FSMContext):
    if not await check_auth(message, state):
        return  # Выход, если пользователь не авторизован

    y = yadisk.YaDisk(token=YADISK_TOKEN)
    if not y.check_token():
        logging.error("Ошибка: Из /newfolder не подключились к Я.Диску. Неверный OAuth-токен.")
        await message.answer("❌ Ошибка сервера: Неверный OAuth-токен Я.Диска.")
        return

    # Получаем путь текущей папки
    data = await state.get_data()
    current_folder = data.get("folder_path", "/")

    folder_name = message.text.replace("/newfolder ", "").strip()
    new_folder_path = f"{current_folder.rstrip('/')}/{folder_name}"

    await check_or_create_folder(y, new_folder_path)
    await state.update_data(folder_path=new_folder_path)

    await message.answer(f"✅ Новая папка создана: {new_folder_path}. Теперь можете загружать файлы сюда.")
    await state.set_state(Form.waiting_for_file)
    await state.update_data(last_interaction=datetime.now())



