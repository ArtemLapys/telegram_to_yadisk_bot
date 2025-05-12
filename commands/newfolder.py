# Создание новых папок
from aiogram import types
from aiogram.fsm.context import FSMContext
from services.yadisk_service import get_yadisk, check_or_create_folder
from keyboards import folder_keyboard
from datetime import datetime, timedelta
import logging

# Обработчик создания новой папки
async def handle_new_folder(message: types.Message, state: FSMContext):
    if not await state.get_data():
        await message.answer("❌ Ошибка: Вы не авторизованы. Используйте команду `/login <токен>`.", parse_mode="Markdown")
        return

    # Получаем текущий путь папки
    data = await state.get_data()
    current_folder = data.get("folder_path", "/")
    last_message_id = data.get("last_message_id")
    last_interaction = data.get("last_interaction")

    # Проверяем, прошло ли больше 5 минут с последнего взаимодействия
    if last_interaction and datetime.now() - last_interaction > timedelta(minutes=5):
        await message.answer("❗ Время для выбора папки истекло. Пожалуйста, используйте команду /upload, чтобы снова выбрать папку.", parse_mode="Markdown")
        return

    # Получаем имя новой папки
    folder_name = message.text.replace("/newfolder ", "").strip()
    if not folder_name:
        await message.answer("❌ Ошибка: Укажите имя новой папки. Пример: `/newfolder МояПапка`", parse_mode="Markdown")
        return

    # Создаем новую папку
    y = get_yadisk()
    if not y:
        await message.answer("❌ Ошибка: Не удалось подключиться к Яндекс.Диску.")
        return

    new_folder_path = f"{current_folder.rstrip('/')}/{folder_name}"
    await check_or_create_folder(y, new_folder_path)

    # Удаляем старое сообщение с кнопками, если оно есть
    if last_message_id:
        try:
            await message.bot.delete_message(chat_id=message.chat.id, message_id=last_message_id)
            logging.info(f"Удалено старое сообщение с ID: {last_message_id}")
        except Exception as e:
            logging.warning(f"Не удалось удалить старое сообщение с ID {last_message_id}: {e}")

    # Получаем обновленный список подпапок
    folders = [folder["name"] for folder in y.listdir(current_folder) if folder["type"] == "dir"]
    keyboard = await folder_keyboard(folders, include_back=True, state=state)

    # Отправляем новое меню с кнопками
    # current_folder_name = "Корневая папка Я.Диска" if current_folder == "/" else current_folder
    new_message = await message.answer(
        f"📂 Текущая папка: {"Корневая папка Яндекс Диска" if current_folder=="/" else current_folder}\n\n✅ Папка `{folder_name}` успешно создана.\n\nВыберите существующую подпапку или создайте новую `/newfolder [имя]`",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

    # Сохраняем ID нового сообщения для последующего удаления
    await state.update_data(last_message_id=new_message.message_id)
    await state.update_data(last_interaction=datetime.now())



