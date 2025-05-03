# Обработка загрузки файла
from aiogram import types, Bot
from aiogram.fsm.context import FSMContext
from auth import check_auth
from states import Form
from datetime import datetime, timedelta
import random
import string
import os
from services.yadisk_service import upload_to_yadisk
from services.yadisk_service import get_current_path_and_subfolders  
import logging
import asyncio
import filetype
from aiogram import exceptions


def generate_random_filename(filename: str, user_name: str, file_type: str) -> str:
    """
    Генерирует случайное имя файла с учетом имени пользователя, типа файла и расширения.
    """
    random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
    name, ext = os.path.splitext(filename)
    return f"{user_name}_{file_type}_{random_str}{ext}"


async def handle_file(message: types.Message, bot:Bot, state: FSMContext, **datat):
   
    if not await check_auth(message, state):
        return  # Выход, если пользователь не авторизован

    # Определяем, если это файл (документ) или видео
    file_size = 0
    file_name = ""
    file_id = ""
    type_doc =""

    # Проверяем, что это документ или видео
    if message.document:
        file_size = message.document.file_size  # Размер документа в байтах
        file_name = message.document.file_name
        file_id = message.document.file_id
        type_doc = "document"
        logging.info(f"Получен документ {file_name}[{file_id}], размер: {file_size}.")
        
    elif message.video:
        file_size = message.video.file_size  # Размер видео в байтах
        file_name = message.video.file_name if message.video.file_name else f"video_{message.video.file_id}"
        file_id = message.video.file_id
        type_doc = "video"
        logging.info(f"Получено видео {file_name}[{file_id}], размер: {file_size}.")
    else:
        await message.answer("❌ Ошибка: только файлы и видео поддерживаются.\n\nИзображения должны быть загружены без сжатия(при отправке боту убрать галочку \"Сжать изображение(Compress the image)\".)")
        return

    max_size = 20 * 1024 * 1024  # 20 MB (ограничение Telegram Bot API)

    if file_size > max_size:
        await message.answer(f"❌ Файл {file_name} слишком большой! Из-за ограничений API Телеграмма - бот может обрабатывать файлы размером до 20 МБ.\n"
                             "Попробуйте загрузить его вручную в Яндекс.Диск и отправить ссылку.")
        return

    current_state = await state.get_state()
    if current_state != Form.waiting_for_file:
        await message.answer("❌ Сначала выберите папку с помощью /upload, /folder или создайте новую /newfolder.", parse_mode="Markdown")
        return

    # Получаем данные о времени последнего взаимодействия
    data = await state.get_data()
    last_interaction = data.get("last_interaction")

    # Проверяем, прошло ли больше 5 минут с последнего взаимодействия
    if last_interaction and datetime.now() - last_interaction > timedelta(minutes=5):
        await message.answer("⏰ Время сеанса для загрузки файла истекло. Пожалуйста, используйте команду /upload, чтобы снова выбрать папку для загрузки.", parse_mode="Markdown")
        return

    # Если прошло менее 5 минут, продолжаем обработку
    folder_path = data.get("folder_path")
    if not folder_path:
        await message.answer("❌ Ошибка: папка не выбрана.\nВведите номер подпапки(`/folder [номер]`) или создайте новую (`/newfolder [имя]`).", parse_mode="Markdown")
        message_text, current_path = await get_current_path_and_subfolders(state)
        await message.answer(message_text, parse_mode="Markdown")
        return

    # Запрещаем загрузку файлов в корень Яндекс.Диска
    if folder_path == "/":
        await message.answer("❌ Ошибка: Нельзя загружать файлы в корень Яндекс.Диска.")
        return

    # Выборка случайного имени для документа
    data = await state.get_data()
    user_name = data.get("owner", "UnknownUser")  # Получаем имя пользователя из состояния, если нет — ставим "UnknownUser"
    random_name = generate_random_filename(file_name, user_name, type_doc)
    local_file_path = f"downloads/{random_name}"

    # Скачать файл или видео
    file_info = await bot.get_file(file_id)

    try:
        await bot.download_file(file_info.file_path, local_file_path, timeout=500)
    except asyncio.TimeoutError:
        logging.error(f"Timeout error while downloading file: {file_info.file_path}")
        await bot.send_message(chat_id=bot.chat_id, text=f"⏳ Мы не смогли скачать файл {file_name} из телеграмм - время ожидания истекло, попробуйте снова позже.")
    except exceptions.TelegramNetworkError as e:
        logging.error(f"Ошибка при скачивании файла '{file_name}': {e}")
        
        await message.answer(f"❌ Ошибка при скачивании файла '{file_name}' из телеграмм. Попробуйте отправить файл еще раз.")
    
    except Exception as e:
        # Логируем любую другую ошибку
        logging.error(f"❌Неизвестная ошибка при скачивании файла '{file_name}': {e}")
        await message.answer(f"❌ Неизвестная ошибка при скачивании файла '{file_name}'.")
    # Если это видео, проверяем его реальный формат и делаем имя
    if message.video:
        kind = filetype.guess(local_file_path)
        if kind:
            new_file_path = f"downloads/{random_name}.{kind.extension}"
        else:
            new_file_path = local_file_path  # Если тип не определён, оставляем без изменений

        # Переименовываем, если нужно
        if new_file_path != local_file_path:
            os.rename(local_file_path, new_file_path)
            local_file_path = new_file_path  # Обновляем путь к файлу
            random_name = f"{random_name}.{kind.extension}"
            logging.info(f"Определили тип видео и переименовали его - {random_name}.")

        # Небольшая задержка для корректной работы файловой системы
        await asyncio.sleep(0.1)

    yadisk_path = f"{folder_path}/{random_name}"
    await upload_to_yadisk(local_file_path, yadisk_path, random_name)
    os.remove(local_file_path)

    if message.document:
        await message.reply(f"✅ Файл '{file_name}' загружен в {folder_path} под именем {random_name}.", parse_mode=None)
    elif message.video:
        await message.reply(f"✅ Видео '{file_name}' загружено в {folder_path} под именем {random_name}.", parse_mode=None)

    # Обновляем время последнего взаимодействия
    await state.update_data(last_interaction=datetime.now())
