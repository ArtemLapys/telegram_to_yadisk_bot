# states.py
from aiogram.fsm.state import State, StatesGroup

class Form(StatesGroup):
    waiting_for_folder = State()
    waiting_for_file = State()
