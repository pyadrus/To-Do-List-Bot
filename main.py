import configparser
import logging
import sqlite3

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
config = configparser.ConfigParser()
config.read('config.ini')
TOKEN = config['Token']['Token']

# Установка уровня логгирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()
# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=storage)


class UserTask(StatesGroup):
    task_done = State()


# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Привет! Чем могу помочь?\n/done - выполненная работа")


# Обработчик для кнопки "Записать выполненное дело на сегодня"
@dp.message_handler(commands=['done'])
async def done_task(message: types.Message):
    await message.answer("Что сегодня Вы выполнили?")
    await UserTask.task_done.set()
    # await dp.register_next_step_handler(message, save_done_task)


@dp.message_handler(state=UserTask.task_done)
async def get_task(message: types.Message, state: State):
    date = message.date.strftime("%Y-%m-%d")
    task = message.text
    # Подключение к базе данных SQLite
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    # Создание таблицы для хранения заданий
    cursor.execute('''CREATE TABLE IF NOT EXISTS tasks
                      (date TEXT, task TEXT)''')
    conn.commit()
    cursor.execute("INSERT INTO tasks VALUES (?, ?)", (date, task))
    conn.commit()
    await message.answer("Задание успешно сохранено!")


# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
