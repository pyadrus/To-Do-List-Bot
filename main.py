import logging
import sqlite3

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
import configparser

config = configparser.ConfigParser()
config.read('config.ini')
TOKEN = config['Token']['Token']

# Установка уровня логгирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token="TOKEN")
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# Подключение к базе данных SQLite
conn = sqlite3.connect('tasks.db')
cursor = conn.cursor()

# Создание таблицы для хранения заданий
cursor.execute('''CREATE TABLE IF NOT EXISTS tasks
                  (date TEXT, task TEXT)''')
conn.commit()

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Привет! Чем могу помочь?")

# Обработчик для кнопки "Записать выполненное дело на сегодня"
@dp.message_handler(commands=['done'])
async def done_task(message: types.Message):
    await message.answer("Что сегодня Вы выполнили?")
    await dp.register_next_step_handler(message, save_done_task)


async def save_done_task(message: types.Message):
    date = message.date.strftime("%Y-%m-%d")
    task = message.text
    cursor.execute("INSERT INTO tasks VALUES (?, ?)", (date, task))
    conn.commit()
    await message.answer("Задание успешно сохранено!")


# Обработчик для кнопки "Список дел на сегодня"
@dp.message_handler(commands=['list'])
async def list_tasks(message: types.Message):
    date = message.date.strftime("%Y-%m-%d")
    cursor.execute("SELECT task FROM tasks WHERE date=?", (date,))
    tasks = cursor.fetchall()
    if tasks:
        tasks_text = "\n".join([f"- {task[0]}" for task in tasks])
        await message.answer(f"Список дел на сегодня ({date}):\n{tasks_text}")
    else:
        await message.answer("На сегодня дел нет.")


# Обработчик для кнопки "Добавить задание"
@dp.message_handler(commands=['add_task'])
async def add_task(message: types.Message):
    await message.answer("Введите дату и задание в формате 'ГГГГ-ММ-ДД Задание'")
    await dp.register_next_step_handler(message, save_task)


async def save_task(message: types.Message):
    try:
        date, task = message.text.split(' ', 1)
        cursor.execute("INSERT INTO tasks VALUES (?, ?)", (date, task))
        conn.commit()
        await message.answer("Задание успешно добавлено!")
    except Exception as e:
        await message.answer(f"Ошибка: {e}")


# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
