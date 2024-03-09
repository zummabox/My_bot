from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_keyboard(
        *btns: str,
        placeholder: str = None,
        sizes: tuple[int] = (2,),
):
    keyboard = ReplyKeyboardBuilder()

    for index, text in enumerate(btns, start=0):
        keyboard.add(KeyboardButton(text=text))

    return keyboard.adjust(*sizes).as_markup(
        resize_keyboard=True, input_field_placeholder=placeholder)

# #Стартовая клавиатура
# start_kb = ReplyKeyboardBuilder()
# start_kb.add(
#     KeyboardButton(text='СО-2010'),
#     KeyboardButton(text='РСБН'),
# )
# start_kb.adjust(2, 2)
#
# #Клавиатура для изделие РСБН
# rsbn_kb = ReplyKeyboardBuilder()
# rsbn_kb.add(
#     KeyboardButton(text='РСБН-85В'),
#     KeyboardButton(text='РСБН-85В-02'),
#     KeyboardButton(text='РСБН-НП'),
# KeyboardButton(text='Назад'),
# )
# rsbn_kb.adjust(3, 1)
#
# #Клавиатура для изделие СО-2010
# co2010_kb =ReplyKeyboardBuilder()
# co2010_kb.add(
# KeyboardButton(text='ПРД'),
# KeyboardButton(text='ППИ'),
#             KeyboardButton(text='ПКиУ'),
# KeyboardButton(text='Железо'),
# KeyboardButton(text='Назад'),
# )
# co2010_kb.adjust(4, 1)
