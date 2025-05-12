#Вспомогательные функции
from auth import check_auth

async def is_user_authenticated(state):
    return await check_auth(state)
