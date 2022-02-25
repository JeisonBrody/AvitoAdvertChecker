from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils import executor
import asyncio
from config import *
from check import pars
from bd import BD

bot = Bot(token=Token)
dp = Dispatcher(bot, storage=MemoryStorage())
base = BD('bd_bot')

list_city = ["Kazan", "Moscow"]
list_brand = ["Subaru", "Lada"]


class TestStates(StatesGroup):
    list_city = State()
    list_brand = State()
    fin = State()


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    if not base.subscriber_exists(message.from_user.id):  # если юзера нет в базе, добавляем его
        base.add_subscriber(message.from_user.id)
    if base.check_status(message.from_user.id):  # Если есть подписка высвечивается полный список команд
        await bot.send_message(message.chat.id, f"Welcome, {message.from_user.first_name}!\n"
                                                f"Список доступных команд:\n"
                                                f"/pars - Начать парсить объявления\n"
                                                f"/stop - Закончить парсинг объявлений\n"
                                                f"/info - Информация об аккаунте")
    else:  # Если нет подписки высвечивается список команд без функции /pars
        await bot.send_message(message.chat.id, f"Welcome, {message.from_user.first_name}!\n"
                                                f"Список доступных команд:\n"
                                                f"/info - Информация об аккаунте")


@dp.message_handler(commands=['pars'])
async def subscribe(message: types.Message, state: FSMContext):
    if base.check_status(message.from_user.id):
        await message.answer(f"Введите город для поиска\n"
                             f"Доступные города: {available_city}")
        await TestStates.list_city.set()
    else:
        await bot.send_message(message.chat.id, "У вас нет подписки")


@dp.message_handler(state=TestStates.list_city)  # добавление города в базу
async def nextstep(message: types.Message, state: FSMContext):
    if not message.text in list_city:
        await message.answer("Введите корректный город (Например: Moscow)")
        return
    else:
        base.update_city(message.from_user.id, message.text)
    await bot.send_message(message.chat.id, f"Введите марку автомобиля\n"
                                            f"Доступные марки авто: {available_brand}")
    await TestStates.next()


@dp.message_handler(state=TestStates.list_brand)  # добавление машины в базу
async def step2(message: types.Message):
    if not message.text in list_brand:
        await message.answer("Введите корректную марку авто (Например: Lada)")
        return
    else:
        base.update_brand(message.from_user.id, message.text)
        await message.answer("Начинаю проверку последних объявлений\n"
                             "Проверка объявлений происходит каждые 5 минут\n"
                             "Для отключения функции напишите команду /stop")
        """Если значени is_pars == True то кидает в таск и переходит в следующее состояние"""
        if base.is_pars(message.from_user.id)[0]:
            loop = asyncio.get_running_loop()
            loop.create_task(call_pars(message))
            await TestStates.next()
        else:
            """Если значени is_pars == False то меняет значние на True кидает в таск и переходит в следующее 
            состояние """
            base.start_pars(message.from_user.id)
            loop = asyncio.get_running_loop()
            loop.create_task(call_pars(message))
            print(message.from_user.id, "Начал парсинг")
            await TestStates.next()


@dp.message_handler(state=TestStates.fin, commands=['stop'])  # остановка парсинга
async def step2(message: types.Message, state: FSMContext):
    if not base.is_pars(message.from_user.id)[0]:
        base.stop_pars(message.from_user.id)
        await bot.send_message(message.chat.id, "Парсинг и так остановлен")
        await state.finish()
    else:
        base.stop_pars(message.from_user.id)
        await bot.send_message(message.chat.id, "Парсинг остановится через 5 минут, пожайлуста подождите")
        await asyncio.sleep(TIME)
        await bot.send_message(message.chat.id, "Парсинг успешно остановлен")
        await state.finish()


@dp.message_handler(commands=['info'])
async def information(message: types.Message):
    info = base.get_info(message.from_user.id)
    if info[1]:
        info_status = "Активная"
    else:
        info_status = "Неактивная"
    ans = f"ID: {message.from_user.id}\n" \
          f"Подписка: {info_status}\n" \
          f"Город: {info[6]}\n" \
          f"Марка авто: {info[5]}\n" \
          f"Радиус поиска: {info[7]}"
    await bot.send_message(message.chat.id, ans)


@dp.message_handler()
async def trash_message(message: types.Message):
    await bot.send_message(message.chat.id, "Я вас не понял")


async def call_pars(message):  # запуск бесконечной работы парсера
    while True:
        if base.is_pars(message.from_user.id)[0]:  # берет данные с бд и проверяет в каком состоянии user
            await parsing(message)
            await asyncio.sleep(TIME)
        else:
            print(message.from_user.id, "Перестал парсить")
            break


async def parsing(message):  # готовый парсер
    city = base.get_info(message.from_user.id)[6]  # Город который выбрал пользователь
    brand = base.get_info(message.from_user.id)[5]  # Марка авто которую выбрал пользователь
    p = pars(id_client=message.from_user.id, City=city, Brand=brand)
    if not p is None:
        await bot.send_message(message.chat.id, p, disable_web_page_preview=True)
    else:
        pass


if __name__ == '__main__':
    executor.start_polling(dp)
