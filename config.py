# Конфигурация и чтение .env
# config.py
import os
import json
from dotenv import load_dotenv
import logging

load_dotenv()

API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
YADISK_TOKEN = os.getenv("YADISK_TOKEN")


tokens_str = os.getenv("USER_TOKENS", "{}")
logging.debug("USER_TOKENS raw value: %s", tokens_str)
try:
    TOKENS = json.loads(tokens_str)
except json.JSONDecodeError as e:
    logging.error("Ошибка при чтении USER_TOKENS: %s", e)
    TOKENS = {}