from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import Message
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware

import os
import logging

# Получение токена из переменных окружения
bot_token = os.getenv('API_TOKEN')

# Создание бота с токеном, который выдал в BotFather при регистрации бота
bot = Bot(token=bot_token)

# Инициализация диспетчера команд
dp = Dispatcher(bot, storage=MemoryStorage())

# Активация системы логирования
logging.basicConfig(level=logging.INFO)

# Сохранённая база
saved_data = {}

# Форма, которая хранит информацию о пользователе
class Form(StatesGroup):
    name_currency_entry = State() # Поле в котором хранится имя валюты
    exchange_rate = State()
    name_currency_find = State() # Поле в котором хранится имя валюты
    amount_currency = State()

# Обработчик комманды /start
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.reply("Привет! Я бот, который поможет тебе конвертировать валюту")

# Обработчик комманды /save_currency (Пользователь вводит название валюты)
@dp.message_handler(commands=['save_currency'])
async def process_start_command(message: Message):
    await Form.name_currency_entry.set()
    await message.reply("Введите название валюты")

# После ввода названия валюты бот предлагает ввести курс валюты к рублю
@dp.message_handler(state=Form.name_currency_entry)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name_currency_entry=message.text)
    course = await state.get_data()
    await Form.exchange_rate.set()
    await message.reply("Введите курс " + course['name_currency_entry'] + " к рублю")

# Программа сохраняет название валюты и курс в словарь
@dp.message_handler(state=Form.exchange_rate)
async def process_money(message: types.Message, state: FSMContext):
    await state.update_data(exchange_rate=message.text)
    user_data = await state.get_data()
    saved_data['form'] = user_data
    await state.finish()
    await message.reply("Курс валюты успешно сохранён")

# Обработчик комманды /convert (После ввода команды /convert бот предлагает ввести название валюты)
@dp.message_handler(commands=['convert'])
async def start_command2(message: types.Message):
    await Form.name_currency_find.set()
    await message.reply('Введите название валюты')

# После ввода названия валюты бот предлагает ввести сумму в указанной валюте
@dp.message_handler(state=Form.name_currency_find)
async def process_name2(message: Message, state: FSMContext):
    await state.update_data(name_currency_find=message.text)
    course1 = await state.get_data()
    await Form.amount_currency.set()
    await message.reply("Введите сумму в указанной валюте " + course1['name_currency_find'])

# Бот конвертирует указанную пользователем сумму в рубли по ранее сохраненному курсу выбранной валюты
@dp.message_handler(state=Form.amount_currency)
async def process_convert(message: types.Message, state: FSMContext):
    await state.update_data(amount_currency=message.text)
    user_data2 = await state.get_data()
    await message.reply(float(user_data2['amount_currency']) * float(saved_data['form']['exchange_rate']))

# Точка входа в приложение
if __name__ == '__main__':
    # Инициализация системы логирования
    logging.basicConfig(level=logging.INFO)
    # Подключение системы логирования к боту
    dp.middleware.setup(LoggingMiddleware())
    # Запуск обработки сообщений
    executor.start_polling(dp, skip_updates=True)