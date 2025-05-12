from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from services.yadisk_service import get_yadisk
from keyboards import folder_keyboard_with_pagination
from commands.upload import cmd_upload
import os
from states import Form
from datetime import datetime
import logging

callback_router = Router()


@callback_router.callback_query(lambda c: c.data.startswith("page:"))
async def paginate_folders(callback: types.CallbackQuery, state: FSMContext):
    try:
        page = int(callback.data.split(":")[1])  # Извлекаем номер страницы
        data = await state.get_data()
        current_folder = data.get("folder_path", "/")  # Получаем текущую папку из состояния
    except Exception as e:
        logging.error(f"Ошибка при разборе данных пагинации: {e}")
        await callback.answer("❌ Ошибка при разборе страницы.", show_alert=True)
        return

    y = get_yadisk()
    folders = [f["name"] for f in y.listdir(current_folder) if f["type"] == "dir"]

    keyboard = await folder_keyboard_with_pagination(
        folders,
        page=page,
        include_back=current_folder != "/",
        is_root=current_folder == "/",
        state=state
    )

    await callback.message.edit_reply_markup(reply_markup=keyboard)
    await callback.answer()


@callback_router.callback_query(lambda c: c.data.startswith("folder:"))
async def select_folder(callback: types.CallbackQuery, state: FSMContext):
    try:
        index = int(callback.data.split(":")[1])  # Извлекаем индекс папки
        data = await state.get_data()
        current_folder = data.get("folder_path", "/")  # Получаем текущую папку из состояния
        #await state.update_data(folder_path=current_folder)
    except Exception as e:
        logging.error(f"Ошибка при разборе callback folder: {e}")
        await callback.answer("❌ Неверный формат данных", show_alert=True)
        return

    y = get_yadisk()
    folders = [f["name"] for f in y.listdir(current_folder) if f["type"] == "dir"]
    
    # Назад
    if index == 0:
        parent = os.path.dirname(current_folder.rstrip('/')) or "/"
        updated_folder = parent
    elif 0 < index <= len(folders):  # Проверяем, что индекс в пределах списка папок
        selected = f"{current_folder.rstrip('/')}/{folders[index - 1]}"  # Индексы кнопок начинаются с 1
        updated_folder = selected
    else:
        await callback.answer("❌ Неверный индекс", show_alert=True)
        return

    # Обновляем путь в состоянии FSM
    await state.update_data(folder_path=updated_folder)

    # Получаем список подпапок
    subfolders = [f["name"] for f in y.listdir(updated_folder) if f["type"] == "dir"]
    keyboard = await folder_keyboard_with_pagination(
        subfolders,
        page=0,
        include_back=updated_folder != "/",
        is_root=updated_folder == "/",
        state=state
    )

    # Проверяем, изменилось ли сообщение
    new_text = f"📂 Текущая папка: {"Корневая папка Яндекс Диска" if updated_folder=="/" else updated_folder}\n\nВыберите подпапку или создайте новую `/newfolder [имя]`"
    if callback.message.text != new_text or callback.message.reply_markup != keyboard:
        await callback.message.edit_text(
            new_text,
            reply_markup=keyboard
        )

    # Сохраняем путь в состоянии FSM
    await state.update_data(folder_path=updated_folder)
    await state.set_state(Form.waiting_for_folder)
    await state.update_data(last_interaction=datetime.now())
    await callback.answer()


@callback_router.callback_query(lambda c: c.data == "upload")
async def handle_upload_button(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()  # Удаляем сообщение с кнопкой
    await cmd_upload(callback.message, state)  # Вызываем команду /upload
