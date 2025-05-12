# Команда /upload и логика выбора папки
from aiogram import types
from aiogram.fsm.context import FSMContext
from states import Form
from services.yadisk_service import get_yadisk
from auth import check_auth
from datetime import datetime
from keyboards import folder_keyboard
import logging
from keyboards import folder_keyboard_with_pagination


async def cmd_upload(message: types.Message, state: FSMContext):
    if not await check_auth(message, state):
        return

    y = get_yadisk()
    if not y:
        await message.answer("❌ Не удалось подключиться к Я.Диску.")
        return

    # Устанавливаем корневой каталог
    await state.update_data(folder_path="/")

    # Получаем текущий путь из состояния FSM
    data = await state.get_data()
    current_folder = data.get("folder_path", "/")

    # Получаем список папок в текущей папке
    folders = [folder["name"] for folder in y.listdir(current_folder) if folder["type"] == "dir"]

    # Удаляем старое сообщение с кнопками, если оно есть
    last_message_id = data.get("last_message_id")
    if last_message_id:
        try:
            await message.bot.delete_message(chat_id=message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.warning(f"Не удалось удалить старое сообщение: {e}")

    # Текст о текущей папке
    #current_folder_name = current_folder if current_folder != "/" else "Корневая папка Я.Диска"
    upload_permission = "❌ В эту папку нельзя загружать файлы."  # при необходимости можно адаптировать

    # Формируем клавиатуру с пагинацией
    keyboard = await folder_keyboard_with_pagination(
        folders,
        page=0,
        include_back=current_folder != "/",
        is_root=current_folder == "/",
        state=state
    )

    # Отправляем новое сообщение с кнопками
    new_message = await message.answer(
        f"📂 Текущая папка: `{'Корневая папка Яндекс Диска' if current_folder=='/' else current_folder}`\n\n{'❌ В эту папку нельзя загружать файлы.' if current_folder=='/' else '✅ Вы можете загружать файлы в эту папку.'}\n\nВыберите существующую подпапку или создайте новую `/newfolder [имя]`",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

    # Сохраняем ID нового сообщения
    await state.update_data(last_message_id=new_message.message_id)
    # Обновляем путь при старте
    # await state.update_data(folder_path=current_folder)


    # Обновляем состояние FSM
    await state.set_state(Form.waiting_for_folder)
    
    await state.update_data(last_interaction=datetime.now())
