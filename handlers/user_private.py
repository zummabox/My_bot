from aiogram import  F, types, Router
from aiogram.filters import CommandStart, Command
from filters.chat_types import ChatTypeFilter

from sqlalchemy.ext.asyncio import AsyncSession
from database.orm_query import orm_get_details, orm_get_categories

from kbds.reply import get_keyboard
from kbds.inline import get_callback_btns

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(['private']))
#Хендлер start и стартовая клавиатура
@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer(
        "Выберите действие",
        reply_markup=get_keyboard(
            "Отчет по деталям",
            # placeholder="Выберите изделие",
            sizes=(1, )
        ),
    )

@user_private_router.message(F.text == "Отчет")
async def starring_at_detail(message: types.Message, session: AsyncSession):
        categories = await orm_get_categories(session)
        btns = {category.name: f'category_{category.id}' for category in categories}
        await message.answer("Выберите категорию", reply_markup=get_callback_btns(btns=btns))


@user_private_router.callback_query(F.data.startswith('category_'))
async def starring_at_detail(callback: types.CallbackQuery, session: AsyncSession):
        category_id = callback.data.split('_')[-1]
        for detail in await orm_get_details(session, int(category_id)):
            await callback.message.answer(
                text = f"<strong>{detail.name}\
                </strong>\n{detail.number}\nСтатус: {detail.status}",
                reply_markup=get_callback_btns(
                    btns={
                    'Удалить': f'delete_{detail.id}',
                    'Изменить данные': f'change_{detail.id}'
                    },
                ),
            )
            await callback.answer()
            await callback.message.answer("Полный отчет ⬆️")


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