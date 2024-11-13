from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

import crud_functions
from crud_functions import *

api = "7701233404:AAFMRvBKUoY2KKK1m3KGz7PoJeuVZR3P6yE"

initiate_db()
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())
kb = ReplyKeyboardMarkup()
button = KeyboardButton('Рассчитать')
button2 = KeyboardButton('Информация')
button3 = KeyboardButton('Купить')
button_reg = KeyboardButton('Регистрация')
kb.add(button, button2, button3, button_reg)

kb_in = InlineKeyboardMarkup()
button4 = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='Calories')
button5 = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
kb_in.add(button4, button5)
kb_prod = InlineKeyboardMarkup()
button6 = InlineKeyboardButton(text='Product1', callback_data='product_buying')
button7 = InlineKeyboardButton(text='Product2', callback_data='product_buying')
button8 = InlineKeyboardButton(text='Product3', callback_data='product_buying')
button9 = InlineKeyboardButton(text='Product4', callback_data='product_buying')
kb_prod.add(button6, button7, button8, button9)


class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()
    balance = State('1000')


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


@dp.message_handler(commands=['start'])
async def start(message):
    with open(f'files/welc.png', 'rb') as img:
        await message.answer_photo(img, f'Приветствуем в нашем боте! {message.from_user.username}', reply_markup=kb)


@dp.message_handler(text='Информация')
async def info(message):
    await message.answer('Бот поможет следить за калориями v.1.0 и еще мы продаем бады ', reply_markup=kb)


@dp.message_handler(text='Рассчитать')
async def main_menu(message):
    await message.answer('Выберите опцию:', reply_markup=kb_in)


@dp.message_handler(text='Купить')
async def get_buying_list(message):
    for i, product in enumerate(get_all_products()):
        await message.answer(f"Название:{product[0]} | Описание:{product[1]} | Цена: {product[2]}")
        with open(f'files/vit{i + 1}.png', 'rb') as img:
            await message.answer_photo(img)

    await message.answer("Выберите продукт для покупки:", reply_markup=kb_prod)


@dp.callback_query_handler(text='product_buying')
async def send_confirm_message(call):
    await call.message.answer('Вы успешно приобрели продукт!')


@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer('10 х вес (кг) + 6,25 x рост (см) – 5 х возраст (г) + 5')
    await call.answer()


@dp.callback_query_handler(text='Calories')
async def set_age(call):
    await call.message.answer('Введите свой возраст')
    await call.answer()
    await UserState.age.set()


@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age=message.text)
    await message.answer("Введите свой рост:")
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth=message.text)
    await message.answer('Введите свой вес:')
    await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight=message.text)
    data = await state.get_data()
    calorie_norm = 10 * int(data['weight']) + 6.25 * int(data['growth']) - 5 * int(data['age'])
    await message.answer(f'Ваша норма калорий {calorie_norm}')
    await state.finish()


@dp.message_handler(text='регистрация')
async def sing_up(message):
    await message.answer("Введите имя пользователя (только латинский алфавит):")
    await RegistrationState.username.set()


@dp.message_handler(state=RegistrationState.username)
async def set_username(message:type.message, state : F  ):
    await state.update_data(username = message.text)
    await message.answer("Введите свой email:")
    await RegistrationState.email.set()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
