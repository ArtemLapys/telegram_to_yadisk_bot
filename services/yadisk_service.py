#Работа с Яндекс.Диском
import yadisk
import logging
import os
from aiogram.fsm.context import FSMContext
from config import YADISK_TOKEN

def get_yadisk():
    y = yadisk.YaDisk(token=YADISK_TOKEN)
    if not y.check_token():
        logging.error("❌ Неверный OAuth-токен Я.Диска.")
        return None
    return y

# Функция загрузки файла на Яндекс.Диск
async def upload_to_yadisk(local_file_path: str, yadisk_path: str, random_name: str):
    y = yadisk.YaDisk(token=YADISK_TOKEN)
    try:
        if not y.check_token():
            logging.error("Ошибка: Неверный OAuth-токен.")
            return
        y.upload(local_file_path, yadisk_path)
        logging.info(f"Файл '{local_file_path}' загружен в '{yadisk_path}' на Яндекс.Диск под именем '{random_name}'.")
    except Exception as e:
        logging.error(f"Ошибка при загрузке файла: {e}({random_name})")

async def check_or_create_folder(y, folder_path):
    if not y.exists(folder_path):
        logging.info(f"Создаю папку '{folder_path}'...")
        y.mkdir(folder_path)
    else:
        logging.info(f"Папка '{folder_path}' уже существует.")
        


# Универсальный метод для получения текущего пути пользователя и списка подпапок
async def get_current_path_and_subfolders(state: FSMContext):
    data = await state.get_data()
    current_folder = data.get("folder_path", "/")

    y = yadisk.YaDisk(token=YADISK_TOKEN)

    if not y.check_token():
        logging.error("❌ Ошибка: Не удалось подключиться к Яндекс.Диску. Неверный OAuth-токен.")
        return "❌ Ошибка: Неверный OAuth-токен.", None

    try:
        subfolders = [
            folder["name"] for folder in y.listdir(current_folder)
            if folder["type"] == "dir"
        ]
    except yadisk.exceptions.PathNotFoundError:
        logging.error(f"❌ Путь не найден: {current_folder}")
        return f"❌ Папка `{current_folder}` не найдена. Используйте `/folder 0` для возврата в корень.", "/"

    subfolders_message = "\n".join(
        [f"{idx + 1}. {name}" for idx, name in enumerate(subfolders)]
    )

    base_msg = f"📂 Текущая папка: _{'Корневая папка Я.Диска.' if current_folder == '/' else 'Корневая папка Я.Диска ' + current_folder}_\n"

    if subfolders:
        folder_msg = (
            f"Существующие подпапки:\n{subfolders_message}\n"
            f"Введите номер подпапки (`/folder [номер]`) или создайте новую (`/newfolder [имя]`).\n"
        )
    else:
        folder_msg = "Подпапок нет. Вы можете создать новую папку (`/newfolder [имя]`) или начать загружать файлы.\n"

    upload_permission = "❌ В эту папку нельзя загружать файлы." if current_folder == "/" else "✅ Вы можете загружать файлы в эту папку."

    return (
        f"{base_msg}{folder_msg}\n{upload_permission}\n🔙 Для возвращения назад используйте команду `/folder 0`",
        current_folder
    )
