from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import (
orm_change_banner_image,
orm_get_categories,
    orm_add_detail,
    orm_delete_detail,
orm_get_info_pages,
    orm_get_detail,
    orm_get_details,
    orm_update_detail,
)

from filters.chat_types import ChatTypeFilter, IsAdmin

from kbds.inline import get_callback_btns
from kbds.reply import get_keyboard


admin_router = Router()
admin_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())


ADMIN_KB = get_keyboard(
    "Отчет",
    "Добавить",
    "Изделия",
    placeholder="Выберите действие",
    sizes=(2,),
)

PRODUCTS_KB = get_keyboard(
    'СО-2010',
    'РСБН-85',
    'РСБН-85В',
    'РСБН-85В-02' ,
    'РСБН-НП',
    'Назад',
    placeholder="Выберите изделие",
    sizes=(3,3),
)

CO2010_KB = get_keyboard(
    'ПРД',
            'ППИ',
            'ПКиУ',
            'Железо',
            'Назад',
            placeholder='Выберите деталь',
            sizes=(3,2)
)


@admin_router.message(Command("admin"))
async def admin_features(message: types.Message):
    await message.answer("Выберите действие", reply_markup=ADMIN_KB)

@admin_router.message(StateFilter(None), F.text == "Изделия")
async def add_detail(message: types.Message, state: FSMContext):
    await message.answer(
        "Выберите деталь", reply_markup=PRODUCTS_KB
    )

# #Хендлер Изделия и клавиатура
# @admin_router.message(F.text == "Изделия")
# async def co2010(message: types.Message):
#     await message.answer(
#         'Выберите действие',
#         reply_markup=get_keyboard(
#             'Добавить',
#              'Изменить статус',
#              'Отчет',
#              'Назад',
#             placeholder="Выберите действие",
#             sizes=(2,),
#     ),
#     )


#Хендлер СО-2010 и клавиатура
@admin_router.message(F.text == "СО-2010")
async def rsbn (message: types.Message):
    await message.answer(
        'Хотите добавить данные?',
        reply_markup=get_keyboard(
            'Добавить',
            'Назад',
            placeholder='Выберите тип изделия',
            sizes=(3,1)
    ),
    )


@admin_router.message(F.text == "Отчет")
async def starring_at_detail(message: types.Message, session: AsyncSession):
        categories = await orm_get_categories(session)
        btns = {category.name: f'category_{category.id}' for category in categories}
        await message.answer("Выберите категорию", reply_markup=get_callback_btns(btns=btns))


@admin_router.callback_query(F.data.startswith('category_'))
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
            #await callback.message.answer("Полный отчет ⬆️")


@admin_router.callback_query(F.data.startswith('delete_'))
async def delete_detail(callback: types.CallbackQuery, session: AsyncSession):

    detail_id = callback.data.split("_")[-1]
    await orm_delete_detail(session, int(detail_id))

    await callback.answer("Данные удалены")
    await callback.message.answer("Данные удалены!")


################# Микро FSM для загрузки/изменения баннеров ############################

class AddBanner(StatesGroup):
    image = State()

# Отправляем перечень информационных страниц бота и становимся в состояние отправки photo
@admin_router.message(StateFilter(None), F.text == 'Добавить/Изменить баннер')
async def add_image2(message: types.Message, state: FSMContext, session: AsyncSession):
    pages_names = [page.name for page in await orm_get_info_pages(session)]
    await message.answer(f"Отправьте фото баннера.\nВ описании укажите для какой страницы:\
                         \n{', '.join(pages_names)}")
    await state.set_state(AddBanner.image)

# Добавляем/изменяем изображение в таблице (там уже есть записанные страницы по именам:
# main, catalog, cart(для пустой корзины), about, payment, shipping
@admin_router.message(AddBanner.image, F.photo)
async def add_banner(message: types.Message, state: FSMContext, session: AsyncSession):
    image_id = message.photo[-1].file_id
    for_page = message.caption.strip()
    pages_names = [page.name for page in await orm_get_info_pages(session)]
    if for_page not in pages_names:
        await message.answer(f"Введите нормальное название страницы, например:\
                         \n{', '.join(pages_names)}")
        return
    await orm_change_banner_image(session, for_page, image_id,)
    await message.answer("Баннер добавлен/изменен.")
    await state.clear()

# ловим некоррекный ввод
@admin_router.message(AddBanner.image)
async def add_banner2(message: types.Message, state: FSMContext):
    await message.answer("Отправьте фото баннера или отмена")

#########################################################################################

#############################Код ниже для машины состояний (FSM)#########################

class AddDetail(StatesGroup):
    name = State()
    number = State()
    category = State()
    status = State()

    detail_for_change = None

    texts = {
        "AddDetail:name": "Введите имя заново:",
        "AddDetail:number": "Введите заводской номер заново:",
        "AddProduct:category": "Выберите изделия  заново ⬆️",
        "AddDetail:status": "Введите статус заново:",
    }

@admin_router.callback_query(StateFilter(None), F.data.startswith("change_"))
async def change_detail_callback(
    callback: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    detail_id = callback.data.split("_")[-1]

    detail_for_change = await orm_get_detail(session, int(detail_id))

    AddDetail.detail_for_change = detail_for_change

    await callback.answer()
    await callback.message.answer(
        "Выберите деталь", reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(AddDetail.name)



@admin_router.message(StateFilter(None), F.text == "Добавить")
async def add_detail(message: types.Message, state: FSMContext):
    await message.answer(
        "Выберите деталь", reply_markup=CO2010_KB
    )
    await state.set_state(AddDetail.name)


# Хендлер отмены и сброса состояния должен быть всегда именно хдесь,
# после того как только встали в состояние номер 1 (элементарная очередность фильтров)
@admin_router.message(StateFilter("*"), Command("отмена"))
@admin_router.message(StateFilter("*"), F.text.casefold() == "отмена")
async def cancel_handler(message: types.Message, state: FSMContext) -> None:

    current_state = await state.get_state()
    if current_state is None:
        return
    if AddDetail.detail_for_change:
        AddDetail.detail_for_change = None
    await state.clear()
    await message.answer("Действия отменены", reply_markup=ADMIN_KB)


# Вернутся на шаг назад (на прошлое состояние)
@admin_router.message(StateFilter("*"), Command("назад"))
@admin_router.message(StateFilter("*"), F.text.casefold() == "назад")
async def back_step_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()

    if current_state == AddDetail.name:
        await message.answer(
            'Предидущего шага нет, или введите название товара или напишите "отмена"'
        )
        return

    previous = None
    for step in AddDetail.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            await message.answer(
                f"Ок, вы вернулись к прошлому шагу \n {AddDetail.texts[previous.state]}"
            )
            return
        previous = step

@admin_router.message(AddDetail.name, F.text)
async def add_number(message: types.Message, state: FSMContext):
    if message.text == "." and AddDetail.detail_for_change:
        await state.update_data(name=AddDetail.detail_for_change.name)
    else:

        await state.update_data(name=message.text)
    await message.answer('Введите заводской номер')
    await state.set_state(AddDetail.number)


@admin_router.message(AddDetail.number, F.text)
async def add_number(message: types.Message, state: FSMContext, session: AsyncSession):
    if message.text == "." and AddDetail.detail_for_change:
        await state.update_data(number=AddDetail.detail_for_change.number)
    else:
        if 4 >= len(message.text):
            await message.answer(
                "Слишком коротний заводской номер. \n Введите заново"
            )
            return
        await state.update_data(number=message.text)

    categories = await orm_get_categories(session)
    btns = {category.name : str(category.id) for category in categories}
    await message.answer("Выберите категорию", reply_markup=get_callback_btns(btns=btns))
    await state.set_state(AddDetail.category)
# Хендлер для отлова некорректных вводов для состояния number
@admin_router.message(AddDetail.number)
async def add_number(message: types.Message, state: FSMContext):
    await message.answer('Вы ввели не допустимые данные, введите заводской номер в формате "12345"')


# Ловим callback выбора категории
@admin_router.callback_query(AddDetail.category)
async def category_choice(callback: types.CallbackQuery, state: FSMContext , session: AsyncSession):
    if int(callback.data) in [category.id for category in await orm_get_categories(session)]:
        await callback.answer()
        await state.update_data(category=callback.data)
        await callback.message.answer('Теперь введите статус детали.')
        await state.set_state(AddDetail.status)
    else:
        await callback.message.answer('Выберите категорию из кнопок.')
        await callback.answer()

#Ловим любые некорректные действия, кроме нажатия на кнопку выбора категории
@admin_router.message(AddDetail.category)
async def category_choice2(message: types.Message, state: FSMContext):
    await message.answer("'Выберите категорию из кнопок.'")


@admin_router.message(AddDetail. status, or_f(F.text, F.text == "."))
async def add_status(message: types.Message, state: FSMContext, session: AsyncSession):
    if message.text and message.text == "." and AddDetail.detail_for_change:
        await state.update_data(status=AddDetail.detail_for_change.status)
    else:

        await state.update_data(status=message.text)      #
    data = await state.get_data()
    try:
        if AddDetail.detail_for_change:
            await orm_update_detail(session, AddDetail.detail_for_change.id, data)
        else:
            await orm_add_detail(session, data)
        await message.answer("Данные добавлены", reply_markup=ADMIN_KB)
        await state.clear()

    except Exception as e:
        await message.   answer(
            f"Ошибка: \n{str(e)}\n Обратитесь к программисту.",
            reply_markup=ADMIN_KB,
        )
        await state.clear()

    AddDetail.detail_for_change = None