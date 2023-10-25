from datetime import datetime
from core.classes import Date_Manipulete, DataBaseCommand
from sqlite3 import Error
import logging
from aiogram import Bot
from aiogram.types import Message
from config import ADMIN_ID


async def hello_message(message: Message, bot: Bot):
    await message.answer("Привіт!👋 Я - бот Запам'ятуйчик. Моя головна місія - відзначати особливі дні!")
    await message.answer("Я тут, щоб допомагати тобі не забувати про дні народження твоїх друзів")
    await message.answer("Давай відзначимо й твій день народження та додамо його до бази даних, \nщоб я завжди міг пам'ятати його та вітати тебе!🎂")
    await DataBaseCommand.reg_new_user(
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        user_id=message.from_user.id,
        user_nickname=message.from_user.username
    )
    await message.answer('Будь ласка, надішліть свою дату народження у форматі Дата-Місяць-Рік (ДД-ММ-РРРР),\nщоб я міг додати її до бази даних.')


async def add_to_DB(message: Message):
    date = Date_Manipulete(message.text)
    if isinstance(date.recognition_birthday_date(), datetime):
        brth_date = date.datetime_in_str()
        await DataBaseCommand.add_birthday_date(
            brth_date,
            message.from_user.id
        )
        await message.answer('Дякую вам за надану інформацію!')
    else:
        await message.answer('Ви ввели дату свого народження не у форматі, який очікувався.\nБудь ласка, введіть дату народження у форматі ДД-ММ-РРРР')


async def reminder(bot: Bot):
    DB = DataBaseCommand
    list_users = await DB.check_birthday_date()
    for user in list_users:
        date = Date_Manipulete(user[0])  # birthday_date
        days_left = date.calculate_message_day_remind()
        id_birsday_person = int(user[1])  # user id
        non_birthday_persons = await DB.select_non_birthday_persons(id_birsday_person)
        if days_left == -7:
            for person in non_birthday_persons:
                await bot.send_message(int(person[0]),
                                       f'У {user[2]} {user[3]} через тиждень буде день народження!')  # first and nickname
                await bot.send_message(ADMIN_ID,
                                       f'#Admin# У користувача {user[2]} {user[3]}  день народження через тиждень')
        elif days_left == -3:
            for person in non_birthday_persons:
                await bot.send_message(int(person[0]),
                                       f'Користувач {user[2]} {user[3]} через 3 дні відзначатиме день народження!')
                await bot.send_message(ADMIN_ID,
                                       f'#Admin# У користувача {user[2]} {user[3]}  день народження через 3 дні')
        elif days_left == -1:
            for person in non_birthday_persons:
                await bot.send_message(int(person[0]),
                                       f'У користувача {user[2]} {user[3]} завтра день народження!')
                await bot.send_message(ADMIN_ID,
                                       f'#Admin# У користувача {user[2]} {user[3]} завтра день народження!')
        elif days_left == 0:
            await bot.send_message(id_birsday_person, "🎉🎉🎉\тВітаю з днем народження! Нехай кожна мить твого життя буде наповнена любов'ю, щастям та незабутніми враженнями. \n Бажаю тобі сміливо йти вперед і завжди досягати нових вершин!\n🎉🎉🎉")
            await bot.send_message(ADMIN_ID,  f'#Admin# Користувачу {user[2]} {user[3]} надіслано поздоровлення')
            for person in non_birthday_persons:
                await bot.send_message(int(person[0]),
                                       f'У користувача {user[2]} {user[3]}  сьогодні день народження!. Незабудь його привітати 🎈')


async def start_bot(bot: Bot):
    await bot.send_message(ADMIN_ID, "Бот запустився")


async def stop_bot(bot: Bot):
    await bot.send_message(ADMIN_ID, "Бот закрився")


async def update_brthday_pre_message(message: Message):
    await message.answer("Для оновлення вашої дати народження введіть дату свого народження у форматі РРРР-MM-ДД")


async def update_brthday(message: Message):
    date = Date_Manipulete(message.text)
    if isinstance(date.recognition_birthday_date(), datetime):
        brth_date = date.datetime_in_str()
        await DataBaseCommand.update_birthday_date(
            brth_date,
            message.from_user.id
        )
        await message.answer('Дата Вашого народження оновлена')
    else:
        await message.answer('Ви ввели дату свого народження не за шаблоном')


async def help_func(message: Message):
    await message.answer(text="Цей бот запам'ятовує дати днів народження твої та твоїх друзів. Та нагадує тобі завчасно о ДР твоїх друзів.\n\
                    Для того щоб подивитись яку дату народження ти вказав(-ла) вебири у списку команду /view")


async def view_func(message: Message):
    date = await DataBaseCommand.check_my_data(message.from_user.id)
    if date:
        await message.answer(f'Ти вказав(-ла), що твоє день народження {date[0]}')
    else:
        await message.answer('Ви ще не вказали свою дату народження')


async def admin_info(message: Message):
    await message.answer("Команди для адміністратора:\n/see - Вивести таблицю з БД у чат\n/delete [id] - видалити вибраного користувача з БД\n ")
    await message.answer(f"@{message.from_user.username}")


async def admin_see_all_users(message: Message):
    if message.from_user.id == ADMIN_ID:
        table = await DataBaseCommand.select_all()
        for raw in table:
            await message.answer(f"{raw}")


async def admin_delete_user(message: Message):
    '''
    Команда яка повина бути написана в чат - "delete 0000000000"
    '''
    if message.from_user.id == ADMIN_ID:
        try:
            await DataBaseCommand.admin_delete_User_from_db(int(message.text.strip()[7:]))
            await message.answer(f"КористувачА {message.text.strip()[7:]} було  видалено з бази даних")
            logging.debug(
                f"КористувачА {message.text.strip()[7:]} було  видалено з бази даних")
        except Error:
            await message.answer("Ти ввів команду не правильно")
            logging.info(Error)
