import re
from datetime import datetime
import aiosqlite
from sqlite3 import Error
import logging
import os


def db_path():
    data_base_name = "db.sqlite"
    directory = os.path.abspath(os.path.join('data'))
    if not os.path.exists(directory):
        os.makedirs(directory)
    db_path = os.path.join(directory, data_base_name)
    return db_path


class Date_Manipulete:

    def __init__(self, date: str) -> None:
        self.date = date.strip()

    def recognition_birthday_date(self) -> [datetime, None]:
        regex1 = re.compile(r"(\d\d?).(\d\d?).(\d\d\d\d)")
        regex2 = re.compile(r"(\d\d\d\d).(\d\d?).(\d\d?)")
        if re.findall(regex1, self.date):
            try:
                cal = re.findall(regex1, self.date)
                cal = [int(_) for _ in cal[0][::-1]]
                calendar_date = datetime(*cal)
                logging.debug(f"Встановлена дата народження {datetime}")
            except ValueError:
                logging.error("Такої дати не існує")
            except:
                logging.error(
                    'Сталася помилка у функціЇ recognition_birthday_date')
        elif re.findall(regex2, self.date):
            try:
                cal = re.findall(regex2, self.date)
                cal = [int(_) for _ in cal[0]]
                calendar_date = datetime(*cal)
                logging.debug(f" дата народження {datetime}")
            except ValueError:
                logging.error("Такої дати не існує")
            except:
                logging.error(
                    'Сталася помилка у функціЇ recognition_birthday_date')
        else:
            logging.error("Користувач ввів дату не за шаблоном")
        return calendar_date

    def datetime_in_str(self) -> [str, None]:
        user_birthday = self.recognition_birthday_date()
        if user_birthday is not None:
            return datetime.strftime(user_birthday, "%d-%m-%Y")
        else:
            return None

    def calculate_message_day_remind(self) -> [int, None]:
        format_date = self.datetime_in_str()
        if format_date is not None:
            date_for_settlement = format_date[:5]+'-'+str(datetime.now().year)
            calculate = datetime.now() - datetime.strptime(date_for_settlement, "%d-%m-%Y")
            return calculate.days
        else:
            return None


class DataBaseCommand:

    async def db_initialization() -> None:
        '''
        EN:Initializing the database and creating tables
        UA:Ініціалізація БД та створення таблиць
        '''

        async with aiosqlite.connect(db_path()) as db:
            cursor = await db.cursor()
            await cursor.execute(
                'CREATE TABLE IF NOT EXISTS users (\
                user_id INTEGER PRIMARY KEY,\
                user_nickname VARCHAR(50),\
                first_name VARCHAR(50), \
                last_name VARCHAR(50),\
                birthday_date VARCHAR(50)\
                )'
            )
            await db.commit()
            logging.debug("Встановлено з'єднання до БД")

    async def reg_new_user(
            first_name: str,
            last_name: str,
            user_id: int,
            user_nickname: str
    ) -> None:
        async with aiosqlite.connect(db_path()) as db:
            cursor = await db.cursor()
            try:
                await cursor.execute(
                    'INSERT OR IGNORE INTO users (first_name, last_name, user_id, user_nickname) VALUES ("%s", "%s"," %d","@%d")'
                    % (first_name, last_name, user_id, user_nickname))
                await db.commit()
                logging.debug('Запис у БД даних кристувача')
            except Error:
                print(Error)

    async def add_birthday_date(
            birthday_date: str,
            user_id: int
    ) -> None:
        async with aiosqlite.connect(db_path()) as db:
            cursor = await db.cursor()
            try:
                await cursor.execute(
                    'INSERT INTO users (birthday_date) VALUES ("%s") WHERE user_id = "%d"'
                    % (birthday_date, user_id))
                await db.commit()
                logging.debug(
                    f'Запис у БД день народження кристувача {user_id}')
            except Error:
                print(Error)

    async def update_birthday_date(
            birthday_date: str,
            user_id: int
    ):
        async with aiosqlite.connect(db_path()) as db:
            cursor = await db.cursor()
            try:
                await cursor.execute(
                    'UPDATE users SET birthday_date=("%s") WHERE user_id = "%d"' % (birthday_date, user_id))
                await db.commit()
                logging.debug(
                    f'Оновлення даних о дні народження кристувача {user_id}')
            except Error:
                print(Error)

    async def check_birthday_date() -> list:
        async with aiosqlite.connect(db_path()) as db:
            cursor = await db.cursor()
            await cursor.execute('SELECT birthday_date, user_id, first_name, user_nickname FROM users')
            return await cursor.fetchall()

    async def select_non_birthday_persons(user_id: int) -> list:
        async with aiosqlite.connect(db_path()) as db:
            cursor = await db.cursor()
            await cursor.execute('SELECT user_id FROM users WHERE NOT user_id = "%d"' % (user_id))
            return await cursor.fetchall()

    async def select_all() -> list:
        async with aiosqlite.connect(db_path()) as db:
            cursor = await db.cursor()
            await cursor.execute('SELECT * FROM users')
            return await cursor.fetchall()

    async def check_my_data(user_id: int) -> tuple:
        async with aiosqlite.connect(db_path()) as db:
            cursor = await db.cursor()
            await cursor.execute('SELECT birthday_date FROM users WHERE user_id = "%d"' % (user_id))
            return await cursor.fetchone()

    async def admin_delete_User_from_db(user_id) -> None:
        async with aiosqlite.connect(db_path()) as db:
            cursor = await db.cursor()
            await cursor.execute('DELETE FROM users WHERE user_id = "%d"' % (user_id))
            await db.commit()
            await cursor.close()
