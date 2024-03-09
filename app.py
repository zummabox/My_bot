import asyncio
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())

from handlers.user_private import user_private_router
from handlers.user_group import user_group_router
from handlers.admin_private import admin_router
from handlers.admin_products import product_router

from common.bot_cmds_list import private

ALLOWED_UPDATES = ['message, edited_message']

bot = Bot(token=os.getenv('TOKEN'))
bot.my_admins_list = []

dp = Dispatcher()

dp.include_router(user_private_router)
dp.include_router(user_group_router)
dp.include_router(product_router)
# dp.include_router(admin_router)


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(commands=private, scope=types.BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot, allowed_updates=ALLOWED_UPDATES)

if __name__ == '__main__':
    asyncio.run(main())