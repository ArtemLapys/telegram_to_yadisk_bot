from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram import types


async def folder_keyboard(folders, state:FSMContext, include_back=False, is_root=False):


    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    if folders:
        for idx, folder in enumerate(folders):
            keyboard.inline_keyboard.append(
                [InlineKeyboardButton(text=f"{idx + 1}. {folder}", callback_data=f"folder:{idx}")]
            )
    else:
        keyboard.inline_keyboard.append(
            [InlineKeyboardButton(text="📂 Нет доступных папок", callback_data="noop")]
        )

    # Добавляем кнопку "Назад", только если это не корневая папка
    if include_back and not is_root:
        keyboard.inline_keyboard.append(
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="folder:0")]
        )

    return keyboard

async def folder_keyboard_with_pagination(folders, state:FSMContext, page=0, include_back=False, is_root=False):
    """
    Создает клавиатуру для выбора папок с пагинацией.
    :param folders: Список папок.
    :param page: Текущая страница.
    :param include_back: Включить кнопку "Назад".
    :param is_root: Является ли текущая папка корневой.
    """

    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    items_per_page = 6
    start_index = page * items_per_page
    end_index = start_index + items_per_page
    current_page_folders = folders[start_index:end_index]

    # Добавляем кнопки для текущей страницы
    for idx, folder in enumerate(current_page_folders, start=start_index + 1):
        keyboard.inline_keyboard.append(
            [InlineKeyboardButton(text=f"{idx}. {folder}", callback_data=f"folder:{idx}")]
        )

    # Добавляем кнопки для навигации по страницам
    navigation_buttons = []
    if page > 0:
        navigation_buttons.append(InlineKeyboardButton(text="⏪️", callback_data=f"page:{page - 1}"))
    if end_index < len(folders):
        navigation_buttons.append(InlineKeyboardButton(text="⏩️", callback_data=f"page:{page + 1}"))
    if navigation_buttons:
        keyboard.inline_keyboard.append(navigation_buttons)

    # Добавляем кнопку "Назад", только если это не корневая папка
    if include_back and not is_root:
        keyboard.inline_keyboard.append(
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="folder:0")]
        )
    return keyboard
