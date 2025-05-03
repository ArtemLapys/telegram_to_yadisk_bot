import random
import string
import os
from services.yadisk_service import upload_to_yadisk
from auth import check_auth
from aiogram import types
from aiogram.fsm.context import FSMContext

async def handle_link_command(message: types.Message, state: FSMContext):
    
    if not await check_auth(message, state):
        return  # Выход, если пользователь не авторизован

    # Получаем данные состояния (папка, в которую нужно загрузить)
    data = await state.get_data()
    folder_path = data.get("folder_path")
    
    if not folder_path or folder_path == "/":   
        await message.reply("❌ Ошибка: Папка не выбрана. Выберите папку с помощью команды /upload или /folder.")
        return


    # Разбиваем сообщение на части
    parts = message.text.split(maxsplit=2)

    if len(parts) < 3:
        await message.reply("❌ Некорректное знание: введите `/link [ссылка] [имя файла]`", parse_mode="Markdown")
        return
    
    link = parts[1]
    filename = parts[2]
    
    # Формируем имя файла на основе имени пользователя и названия файла
    user_name = data.get("owner", "UnknownUser")  # Получаем имя пользователя из состояния, если нет — ставим "UnknownUser"
    file_name = f"{filename}_link_{user_name}_"+''.join(random.choices(string.ascii_letters + string.digits, k=10))+".txt"  # Сохраняем ссылку как текстовый файл

    # Сформировать путь на Яндекс.Диск для загрузки
    yadisk_path = f"{folder_path}/{file_name}"
    
    # Сохраняем ссылку как текстовый файл
    local_file_path = f"downloads/{file_name}"

    with open(local_file_path, 'w') as file:
        file.write(link)  # Записываем ссылку в файл

    # Загрузим файл на Яндекс.Диск
    await upload_to_yadisk(local_file_path, yadisk_path, file_name)

    # Удаляем локальный файл после загрузки
    os.remove(local_file_path)

    await message.reply(f"✅ Ссылка сохранена в файл <code>{file_name}</code> в папке <code>{folder_path}</code> на Яндекс.Диск.", parse_mode="HTML")
