from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
import os


class Form(StatesGroup):
    NameCurrency = State()
    RateCurrency = State()
    Sum = State()
    CheckCurrency = State()

dictionary = {}

bot_token = os.getenv('TELEGRAM_API_TOKEN')
bot = Bot(token=bot_token)
dp = Dispatcher(bot, storage=MemoryStorage())

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.reply("Привет! я бот конвертирующий валюту.Введите /save_currency,чтобы добавить валюту в бота или /convert, чтобы ее конвертировать")


@dp.message_handler(commands=['save_currency'])
async def save_command(message: types.Message):
    await Form.NameCurrency.set()
    await message.reply("Введите название валюты")

@dp.message_handler(state=Form.NameCurrency)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.reply('Курс "' + message.text + '" по отношению к Рублю: ')
    await Form.RateCurrency.set()

@dp.message_handler(state=Form.RateCurrency)
async def process_course(message: types.Message, state: FSMContext):
    course = message.text
    name = await state.get_data()
    currency_dictionary = name['name']
    dictionary[currency_dictionary] = course
    await message.reply('Вапюта сохранена. Для конвертации воспользуйтесь /convert')
    await state.finish()

@dp.message_handler(commands=['convert'])
async def convert_command(message: types.Message):
    await Form.CheckCurrency.set()
    await message.reply("Введите название валюты, которую вы сохранили ранее")

@dp.message_handler(state=Form.CheckCurrency)
async def process_check(message: types.Message, state: FSMContext):
    await state.update_data(check_course=message.text)
    await message.answer("Введите сумму, которую вы хотите перевести в рубли")
    await Form.Sum.set()

@dp.message_handler(state=Form.Sum)
async def process_convert(message: types.Message, state: FSMContext):
    num = message.text
    check_course = await state.get_data()
    currency_dictionary = check_course['check_course']
    result = int(dictionary[currency_dictionary]) * int(num)
    await message.reply(result)
    await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp)
