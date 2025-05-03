import logging
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums.parse_mode import ParseMode

from config import API_TOKEN
from commands import upload, folder, help as help_cmd, newfolder, file_handler, link as link_cmd
from auth import cmd_login
from aiogram import F

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))

dp = Dispatcher(storage=MemoryStorage())

async def bot_middleware(handler, event, data):
    data["bot"] = bot  # Добавляем bot в контекст
    return await handler(event, data)

dp.update.middleware(bot_middleware)

# Регистрация обработчиков команд
dp.message.register(cmd_login, F.text.startswith("/login"))
dp.message.register(help_cmd.help_message, F.text == "/help")
dp.message.register(upload.cmd_upload, F.text == "/upload")
dp.message.register(folder.handle_folder, F.text.startswith("/folder"))
dp.message.register(newfolder.handle_new_folder, F.text.startswith("/newfolder"))
dp.message.register(help_cmd.help_message, F.text == "/start") #костыль. Нужен отдельный метод :)
dp.message.register(link_cmd.handle_link_command, F.text.startswith("/link")) 
dp.message.register(file_handler.handle_file, F.content_type.in_([types.ContentType.DOCUMENT, types.ContentType.VIDEO, types.ContentType.VIDEO_NOTE, types.ContentType.PHOTO]))

if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
