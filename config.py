# Конфигурация и чтение .env
# config.py
import os
import json
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
YADISK_TOKEN = os.getenv("YADISK_TOKEN")

# Загружаем словарь токенов пользователей из JSON-строки
TOKENS = json.loads(os.getenv("USER_TOKENS", "{}"))
