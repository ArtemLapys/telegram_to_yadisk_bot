# auth.py
from aiogram import types
from aiogram.fsm.context import FSMContext
from config import TOKENS
from keyboards import folder_keyboard_with_pagination  # Импортируем клавиатуру с пагинацией
from services.yadisk_service import get_yadisk  # Импортируем сервис для работы с Я.Диском
import logging

async def cmd_login(message: types.Message, state: FSMContext):
    token = message.text.replace("/login", "").strip()
    if not token:
        await message.reply(
            "❌ Пожалуйста, введите токен после команды. Пример: `/login <токен>`",
            parse_mode="Markdown"
        )
        return

    if token in TOKENS:
        await state.update_data(authenticated=True, owner=TOKENS[token])
        await message.answer(f"✅ Авторизация успешна! Добро пожаловать, {TOKENS[token]}!", parse_mode="Markdown")
        await message.delete()

        loading_message = await message.answer(
            "🔄 Загружаем список папок...\n\n`Если список папок не загрузился, вы можете принудительно запросить его командой /upload`",
            parse_mode="Markdown"
        )
        await state.update_data(loading_message_id=loading_message.message_id)

        # Получаем список папок и отправляем кнопки с пагинацией
        y = get_yadisk()
        if y:
            folders = [folder["name"] for folder in y.listdir("/") if folder["type"] == "dir"]
            keyboard = await folder_keyboard_with_pagination(
                folders, page=0, include_back=False, is_root=True, state=state
            )
            current_folder_name = "Корневая папка Я.Диска"
            upload_permission = "❌ В эту папку нельзя загружать файлы."
            new_message = await message.answer(
                f"📂 Текущая папка: {current_folder_name}\n\n{upload_permission}\n\nВыберите существующую подпапку или создайте новую `/newfolder [имя]`",
                reply_markup=keyboard
            )

            # Удаляем сообщение о загрузке списка папок
            loading_message_id = (await state.get_data()).get("loading_message_id")
            if loading_message_id:
                try:
                    await message.bot.delete_message(chat_id=message.chat.id, message_id=loading_message_id)
                except Exception as e:
                    logging.warning(f"Не удалось удалить сообщение о загрузке списка папок с ID {loading_message_id}: {e}")

            # Сохраняем ID нового сообщения для последующего удаления
            await state.update_data(last_message_id=new_message.message_id)
    else:
        await message.reply("❌ Неверный токен. Попробуйте снова.", parse_mode="Markdown")

async def check_auth(message: types.Message, state: FSMContext) -> bool:
    data = await state.get_data()
    if not data.get("authenticated"):
        await message.bot.send_message(
            chat_id=message.chat.id,
            text="🔒 Введите токен с помощью `/login <токен>`.",
            parse_mode="Markdown"
        )
        return False
    return True


async def is_authenticated(callback_query: types.CallbackQuery, state: FSMContext) -> bool:
    data = await state.get_data()
    if not data.get("authenticated"):
        await callback_query.answer("🔒 Авторизуйтесь с помощью токена в боте /login <токен>.", show_alert=True)
        return False
    return True