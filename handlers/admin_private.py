from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from filters.chat_types import ChatTypeFilter, IsAdmin
from kbds.reply import get_keyboard


admin_router = Router()
admin_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())


ADMIN_KB = get_keyboard(
    "СО-2010",
    "РСБН",
    placeholder="Выберите изделие",
    sizes=(2,),
)


@admin_router.message(Command("admin"))
async def admin_features(message: types.Message):
    await message.answer("Выберите изделие с которым хотите работать", reply_markup=ADMIN_KB)

#Хендлер СО-2010 и клавиатура
@admin_router.message(F.text == "СО-2010")
async def co2010(message: types.Message):
    await message.answer(
        'Выберите деталь входящую в изделие СО-2010',
        reply_markup=get_keyboard(
            'ПРД',
            'ППИ',
            'ПКиУ',
            'Железо',
            'Назад',
            placeholder='Выберите деталь',
            sizes=(3,2)
    ),
    )
@admin_router.message(F.text.in_({'ПРД', 'ППИ', 'ПКиУ','Железо'}) )
async def details(message: types.Message):
    await message.answer(
        'Выберите действие',
        reply_markup=get_keyboard(
            'Добавить',
            'Изменить статус',
            'Отчет',
            'Назад',
            placeholder='Выберите действие',
            sizes=(2,1)
        ),
    )

#Хендлер РСБН и клавиатура
@admin_router.message(F.text == "РСБН")
async def rsbn (message: types.Message):
    await message.answer(
        'Выберите тип изделия РСБН',
        reply_markup=get_keyboard(
            'РСБН-85В',
            'РСБН-85В-02',
            'РСБН-НП',
            'Назад',
            placeholder='Выберите тип изделия',
            sizes=(3,1)
    ),
    )

#Код ниже для машины состояний (FSM)

class AddProduct(StatesGroup):
    name = State()
    number = State()
    status = State()


texts = {
    'AddProduct:number': 'Введите заводской номер:',
    'AddProduct:status': 'Введите статус:',
}


@admin_router.message(StateFilter(None), F.text == 'Добавить')
async def add_product(message: types.Message, state: FSMContext):
    await message.answer(
    'Введите заводской номер', reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(AddProduct.number)


#Хендлер отмены и сброса состояния должен быть всегда именно хдесь,
#после того как только встали в состояние номер 1 (элементарная очередность фильтров)
@admin_router.message(StateFilter('*'), Command("отмена"))
@admin_router.message(StateFilter('*'), F.text.casefold() == "отмена")
async def cancel_handler(message: types.Message, state: FSMContext) -> None:

    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    await message.answer("Действия отменены", reply_markup=ADMIN_KB)


@admin_router.message(AddProduct.number, F.text)
async def add_number(message: types.Message, state: FSMContext):
    await state.update_data(number=message.text)
    await message.answer('Введите статус')
    await state.set_state(AddProduct.status)

@admin_router.message(AddProduct.number)
async def add_number(message: types.Message, state: FSMContext):
    await message.answer('Вы ввели не допустимые данные, введите заводской номер в формате "12345"')



@admin_router.message(AddProduct. status,F.text)
async def add_status(message: types.Message, state: FSMContext):
    await state.update_data(status=message.text)
    await message.answer('Данные добавлены', reply_markup=ADMIN_KB)
    data = await state.get_data()
    await message.answer(str(data))
    await state.clear()