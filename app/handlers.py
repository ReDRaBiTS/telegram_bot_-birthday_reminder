from datetime import datetime
from core.classes import Date_Manipulete, DataBaseCommand
from sqlite3 import Error
import logging
from aiogram import Bot
from aiogram.types import Message
from config import ADMIN_ID, DONAT_INFO
from data.list_of_greetings import birthday_wishes
import random
from aiogram.fsm.context import FSMContext
from app.FSM import StepsForm_New_User, StepsForm_Update_User
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.exceptions import TelegramForbiddenError


async def hello_message(message: Message, state: FSMContext) -> None:
    await message.answer("Привіт!👋Давай додамо твій день народження до календаря, \nщоб я міг пам'ятати його та вітати тебе!🎂")
    await DataBaseCommand.reg_new_user(
        first_name = message.from_user.first_name,
        last_name = message.from_user.last_name,
        user_id = message.from_user.id, 
        user_nickname = message.from_user.username
    )
    await message.answer('Будь ласка, напиши свою дату народження у форматі\nДата-Місяць-Рік (наприклад 01 01 2001 або 01-01-2001),\nщоб я міг додати її до календаря.')
    await state.set_state(StepsForm_New_User.ADD_NEW_USER)


    


async def add_to_DB(message: Message, state: FSMContext, bot: Bot) -> None:
    date = Date_Manipulete(message.text)
    if isinstance(date.recognition_birthday_date(), datetime):
        brth_date = date.datetime_in_str()
        await DataBaseCommand.add_birthday_date(
            brth_date,
            message.from_user.id
        )
        await message.answer('Дякую за надану інформацію!')
        await state.clear()
    else:
        await message.answer('Ви ввели дату свого народження не у форматі, який очікувався.\nБудь ласка, введіть дату народження у форматі ДД-ММ-РРРР')

    list_users = await DataBaseCommand.check_birthday_date()
    non_birthday_persons = set()
    all_chats = await DataBaseCommand.select_all_chats_id() 
    for user in list_users:
        Date = Date_Manipulete(user[0])  # birthday_date
        days_left = Date.calculate_message_day_remind()
        if  0 > days_left >= -7:
            persons_list = await DataBaseCommand.select_non_birthday_persons(user[1])# user id
            non_birthday_persons.update(persons_list)
            chat_with_birthday_user = []
            for chat in all_chats:
                chat_member = await bot.get_chat_member(chat, user[1])
                if chat_member.status in ["creator", "member", "administrator"] :
                    chat_with_birthday_user.append(chat)
                    sended_users = []
            for chat in chat_with_birthday_user:
                for nb_user in non_birthday_persons:
                    chat_member = await bot.get_chat_member(chat, nb_user)
                    if chat_member.status in ["creator", "member", "administrator"] and nb_user not in sended_users and days_left == -1:
                        await bot.send_message(nb_user , text = f'У користувача <b>{user[2]}</b> {user[3]} завтра буде день народження!🎉\nНе забудь надіслати свої привітання🎂')  # first and nickname
                        sended_users.append(nb_user)
                    elif chat_member.status in ["creator", "member", "administrator"] and nb_user not in sended_users and -1 > days_left > -5:
                        await bot.send_message(nb_user , text = f'У користувача <b>{user[2]}</b> {user[3]} через {abs(days_left)} днІ День народження!🎉\nНе забудь надіслати свої привітання🎂')
                        sended_users.append(nb_user)
                    elif chat_member.status in ["creator", "member", "administrator"] and nb_user not in sended_users and -5 >= days_left >= -7:
                        await bot.send_message(nb_user , text = f'У користувача <b>{user[2]}</b> {user[3]} через {abs(days_left)} днІв День народження!🎉\nНе забудь надіслати свої привітання🎂')
                        sended_users.append(nb_user)
            non_birthday_persons.clear()

        elif days_left == 0:
            chat_with_birthday_user = []
            existing_chats = []
            for chat in all_chats:
                try:
                    chat_member = await bot.get_chat_member(chat, user[1])
                    if chat_member.status in ["creator", "member", "administrator"]:
                        chat_with_birthday_user.append(chat)
                except TelegramForbiddenError:
                        await DataBaseCommand.delete_old_chat(chat)
            for chat in chat_with_birthday_user:
                await bot.send_message(chat, f'🎉🎉🎉 У {user[2]} {user[3]} сьогодні День народження! 🎉🎉🎉')
                await bot.send_message(chat, text = random.choice(birthday_wishes))
                existing_chats.append(chat)
        


async def reminder(bot: Bot) -> None:
    '''
    UA: Функція перевіряє чи є у користувача день народження через БД. Якщо є - відправляє повідомлення у всі чати в яких є користувач і бот.
        Також нагадує іншим користувачам, які з іменником перебувають у одному чаті, що день його день народження буде через неділю.
    EN: The function checks if there is a birthday date in the user's database. If there is, it sends a message to all chats in which the user and the bot are in.
        Moreover, it reminds other users who have the same nickname as the user who has the birthday date, that the birthday date of the user will be in one week.
    '''
    list_users = await DataBaseCommand.check_birthday_date()
    non_birthday_persons = set()
    all_chats = await DataBaseCommand.select_all_chats_id() 
    for user in list_users:
        Date = Date_Manipulete(user[0])  # birthday_date
        days_left = Date.calculate_message_day_remind()
        if  days_left == -7:
            persons_list = await DataBaseCommand.select_non_birthday_persons(user[1])# user id
            non_birthday_persons.update(persons_list)
            chat_with_birthday_user = []
            for chat in all_chats:
                chat_member = await bot.get_chat_member(chat, user[1])
                if chat_member.status in ["creator", "member", "administrator"] :
                    chat_with_birthday_user.append(chat)
            sended_users = []
            for chat in chat_with_birthday_user:
                for nb_user in non_birthday_persons:
                    chat_member = await bot.get_chat_member(chat, nb_user)
                    if chat_member.status in ["creator", "member", "administrator"] and nb_user not in sended_users:
                        await bot.send_message(nb_user , text = f'У користувача <b>{user[2]}</b> {user[3]} через неділю буде День народження!🎉\nНе забудь надіслати свої привітання🎂')  # first and nickname
                        sended_users.append(nb_user)
            non_birthday_persons.clear()

        elif days_left == 0:
            chat_with_birthday_user = []
            existing_chats = []
            for chat in all_chats:
                try:
                    chat_member = await bot.get_chat_member(chat, user[1])
                    if chat_member.status in ["creator", "member", "administrator"]:
                        chat_with_birthday_user.append(chat)
                except TelegramForbiddenError:
                        await DataBaseCommand.delete_old_chat(chat)
            for chat in chat_with_birthday_user:
                await bot.send_message(chat, f'🎉🎉🎉 У {user[2]} {user[3]} сьогодні день народження! 🎉🎉🎉')
                await bot.send_message(chat, text = random.choice(birthday_wishes))
                existing_chats.append(chat)
    


            await bot.send_message(ADMIN_ID,  f'#Admin# Користувачу {user[2]} {user[3]} надіслано привітання у чати {existing_chats}')
            all_chats.clear()
            


async def start_bot(bot: Bot) -> None:
    await bot.send_message(ADMIN_ID, "Бот запустився")


async def stop_bot(bot: Bot) -> None:
    await bot.send_message(ADMIN_ID, "Бот закрився")


async def update_brthday_pre_message(message: Message, state: FSMContext) -> None:
    await DataBaseCommand.reg_new_user(
        first_name = message.from_user.first_name,
        last_name = message.from_user.last_name,
        user_id = message.from_user.id, 
        user_nickname = message.from_user.username
    )
    await message.answer("Будь ласка, введіть вашу дату народження в \nформаті ДД-ММ-РРРР для її оновлення.")
    await state.set_state(StepsForm_Update_User.CHANGE_DATE)


async def update_brthday(message: Message, state: FSMContext) -> None:
    date = Date_Manipulete(message.text)
    if isinstance(date.recognition_birthday_date(), datetime):
        brth_date = date.datetime_in_str()
        await DataBaseCommand.update_birthday_date(
            brth_date,
            message.from_user.id
        )
        await message.answer('Ваша дата народження успішно оновлена')
        await state.clear()
    else:
        await message.answer('Ви ввели неправильну дату або дату, яка не відповідає формату. Будь ласка, введіть дату у встановленому форматі')


async def help_func(message: Message) -> None:
    await message.answer(text="Цей бот допомагає вам та вашим друзям запам'ятовувати дні народження та нагадує про них завчасно.\n\
Щоб переглянути вказану вами дату, введіть команду /view")


async def view_func(message: Message) -> None:
    date = await DataBaseCommand.check_my_data(message.from_user.id)
    if date:
        await message.answer(f'Ви вказали, що ваше день народження {date[0]}p.')
    else:
        await message.answer('Ви ще не вказали свою дату народження')


async def admin_info(message: Message) -> None:
    if message.from_user.id == ADMIN_ID:
        await message.answer("Команди для адміністратора:\n/see - Вивести таблицю з БД у чат\n/delete [id] - видалити вибраного користувача з БД\n ")
        await message.answer(f"@{message.from_user.username}")


async def admin_see_all_users(message: Message) -> None:
    if message.from_user.id == ADMIN_ID:
        table = await DataBaseCommand.select_all()
        for raw in table:
            await message.answer(f"{raw}")


async def admin_delete_user(message: Message) -> None:
    '''
    Видаляє з БД користувача а вказаним ID
    Функція яка зпрацьовує при написанні в чат - "delete id"
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

async def admin_sql_requests(message: Message) -> None:
    '''
    Проброс запитів SQL через повідомлення в телеграмі
    Функція яка зпрацьовує при написанні в чат - "SQL запит"
    '''
    if message.from_user.id == ADMIN_ID:
        try:
            await DataBaseCommand.sql_commads_admin(message.text.strip()[4:])
            logging.debug(f"Команду успішно виконано")
        except Error:
            await message.answer("Твій SQL запит не правильний")
            logging.info(Error)
            await message.answer(text=Error)

async def hello_in_goup(message : Message, bot: Bot) -> None:
    markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⏩Приєднатися⏪",url="https://t.me/Local_birthday_bot")]])
    await bot.send_message(message.chat.id , text="Привіт усім! 👋 Мене додали до цього чату, щоб я міг записувати та нагадувати вам про дні народження ваших друзів. 🎉\n\Я вмію вести календар та повідомляти про наближення дня народження ваших друзів у приватних повідомленнях, а також вітати іменинників у групі. 🎂", 
                           reply_markup = markup)
    await DataBaseCommand.add_new_chats_in_db(message.chat.id)
    await bot.send_message(ADMIN_ID, f"Бота добавили у групу ({message.chat.title})") 
    logging.info(f"Бота добавили у групу----({message.chat.id})----{message.chat.title}----")

async def donate_messege(message : Message) -> None:
    await message.answer(F"Підтримати розробника копійкою можна на карти: \n{DONAT_INFO}")

    