from aiogram import  F, types, Router
from aiogram.filters import CommandStart, Command
from filters.chat_types import ChatTypeFilter

from kbds.reply import get_keyboard

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(['private']))
#Хендлер start и стартовая клавиатура
@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer(
        "Выберите изделие с которым собираетесь работать",
        reply_markup=get_keyboard(
            "СО-2010",
            "РСБН",
            placeholder="Выберите изделие",
            sizes=(2, )
        ),
    )


@user_private_router.message(Command('table_co2010'))
async def co2010(message: types.Message):
    await message.answer('Таблица деталей по изделию СО-2010')

@user_private_router.message(Command('table_rsbn85v'))
async def menu_cmd(message: types.Message):
    await message.answer('Таблица деталей по изделию РСБН-85В')

@user_private_router.message(Command('table_rsbn85v02'))
async def menu_cmd(message: types.Message):
    await message.answer('Таблица деталей по изделию РСБН-85В-02')

@user_private_router.message(Command('table_rsbnnp'))
async def menu_cmd(message: types.Message):
    await message.answer('Таблица деталей по изделию РСБН-НП')