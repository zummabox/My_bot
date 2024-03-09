from typing import List

from aiogram import F, Router, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from filters.chat_types import ChatTypeFilter, IsAdmin
from kbds.reply import get_keyboard


product_router = Router()
product_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())


class AddProduct(StatesGroup):
                    # Выбрать изделие
    name = State()  # добавить имя детали
    number = State()    # добавить номер детали
    status = State()    # Добавить статус детали


class Detail:
    ...


class Product:
    name: str = ''
    details_to_ready: List[str] = []
    actual_details: List[Detail] = []

    @product_router.message(StateFilter(None), F.text == name)
    async def add_detail(self, message: types.Message, state: FSMContext):
        # Вся логика добавления детали
        await message.answer(
            f'Выберите деталь входящую в изделие {self.name}',
            reply_markup=get_keyboard(
                *self.details_to_ready,
                'Назад',
                placeholder='Выберите деталь',
                sizes=(3, 2)
            ),
        )
        await state.set_state(AddProduct.name)

    @product_router.message(AddProduct.name)
    async def add_detail_name(self, message: types.Message, state: FSMContext):
        # TODO ПРОВЕРКА ИМЕНИ
        await state.update_data(name=message.text)
        await message.answer(
            'Введите заводской номер', reply_markup=types.ReplyKeyboardRemove()
        )
        await state.set_state(AddProduct.number)

    @product_router.message(AddProduct.number, F.text)
    async def add_detail_number(self, message: types.Message, state: FSMContext):
        await state.update_data(number=message.text)
        await message.answer('Введите статус')
        await state.set_state(AddProduct.status)

    @product_router.message(AddProduct.number)
    async def wrong_detail_number(self, message: types.Message, state: FSMContext):
        await message.answer('Вы ввели не допустимые данные, введите заводской номер в формате "12345"')

    @product_router.message(AddProduct.status, F.text)
    async def add_detail_status(self, message: types.Message, state: FSMContext):
        await state.update_data(status=message.text)
        await message.answer('Данные добавлены', reply_markup=self.get_all_products())
        data = await state.get_data()
        await message.answer(str(data))
        await state.clear()

    @staticmethod
    def get_all_products():
        return get_keyboard(
            "СО-2010",
            "РСБН",
            placeholder="Выберите изделие",
            sizes=(2,),
        )


class CO_2010(Product):
    name = 'СО-2010'
    details_to_ready = [
        'ПРД',
        'ППИ',
        'ПКиУ',
        'Железо',
    ]


class RSBN(Product):
    name = 'РСБН'
    details_to_ready = [
        'РСБН-85В', # -> изделия -> платы
        'РСБН-85В-02',
        'РСБН-НП',
    ]