# handlers.py
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from auth import is_authenticated


router = Router()

@router.callback_query()
async def handle_folder_navigation(callback_query: types.CallbackQuery, state: FSMContext):
    # Enforce authentication
    if not await is_authenticated(callback_query, state):
        # Stop further processing if not authenticated
        return

