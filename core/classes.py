import re
from datetime import datetime
import aiosqlite
from sqlite3 import Error
import logging
import os

# import tracemalloc
# tracemalloc.start()


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
        if re.findall(regex1, self.date):
            try:
                cal = re.findall(regex1, self.date)
                cal = [int(_) for _ in cal[0][::-1]]
                calendar_date = datetime(*cal)
                logging.debug(f"Встановлена дата народження {datetime}")
            except ValueError:
                logging.error("Такої дати не існує")
                return False
            except:
                logging.error(
                    'Сталася помилка у функціЇ recognition_birthday_date')
                return False
        else:
            logging.error("Користувач ввів дату не за шаблоном")
            return False
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
            await cursor.execute(
                'CREATE TABLE IF NOT EXISTS chats (chat_id INTEGER PRIMARY KEY)'
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
                    'INSERT OR IGNORE INTO users (first_name, last_name, user_id, user_nickname) VALUES ("%s", "%s"," %d","@%s")'
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
                    'UPDATE users SET birthday_date = "%s" WHERE user_id = "%d"'% (birthday_date, user_id)
                    )
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
                    'UPDATE users SET birthday_date=("%s") WHERE user_id = "%d"' % (birthday_date, user_id)
                    )
                await db.commit()
                logging.debug(
                    f'Оновлення даних о дні народження кристувача {user_id}')
            except Error:
                print(Error)

    async def check_birthday_date() -> list:
        async with aiosqlite.connect(db_path()) as db:
            cursor = await db.cursor()
            await cursor.execute(
                'SELECT birthday_date, user_id, first_name, user_nickname FROM users'
                )
            return await cursor.fetchall()
        
    async def select_all() -> list:
        async with aiosqlite.connect(db_path()) as db:
            cursor = await db.cursor()
            await cursor.execute(
                'SELECT * FROM users'
                )
            return await cursor.fetchall()

    async def check_my_data(user_id: int) -> tuple:
        async with aiosqlite.connect(db_path()) as db:
            cursor = await db.cursor()
            await cursor.execute(
                'SELECT birthday_date FROM users WHERE user_id = "%d"' % (user_id)
                )
            return await cursor.fetchone()

    async def admin_delete_User_from_db(user_id) -> None:
        async with aiosqlite.connect(db_path()) as db:
            cursor = await db.cursor()
            await cursor.execute(
                'DELETE FROM users WHERE user_id = "%d"' % (user_id)
                )
            await db.commit()
            await cursor.close()
    
    async def sql_commads_admin(command:str)-> None:
        async with aiosqlite.connect(db_path()) as db:
            cursor = await db.cursor()
            await cursor.execute(command)
            await db.commit()

    async def add_new_chats_in_db(chats_id : int) -> None:
        async with aiosqlite.connect(db_path()) as db:
            cursor = await db.cursor()
            await cursor.execute(
                'INSERT OR IGNORE INTO chats (chat_id) VALUES ("%d")'%chats_id
                )
            await db.commit()

    async def select_non_birthday_persons(birshday_user_id: int) -> list:
        async with aiosqlite.connect(db_path()) as db:
            cursor = await db.cursor()
            await cursor.execute(
                'SELECT EXISTS(SELECT user_id FROM users WHERE NOT user_id = %d)' %(birshday_user_id)
                )
            exist_user = await cursor.fetchone()
            
            if exist_user[0] == 1:
                correct_list_of_users = []
                await cursor.execute(
                    'SELECT user_id FROM users WHERE NOT user_id = %d' % (birshday_user_id)
                    )
                list_user = []
                async for row in cursor:
                    list_user.append(row[0])
                return set(list_user)
        
    async def select_all_chats_id() -> list:
        async with aiosqlite.connect(db_path()) as db:
            cursor = await db.cursor()
            await cursor.execute(
                'SELECT chat_id FROM chats'
                )            # chat_ids = await cursor.fetchone()
            chat_ids = []
            async for row in cursor:
                chat_ids.append(row[0])
            return set(chat_ids)
        
    async def delete_old_chat(chat_id: int) -> None:
        async with aiosqlite.connect(db_path()) as db:
            cursor = await db.cursor()
            await cursor.execute(
                'DELETE FROM chats WHERE chat_id = "%d"' % (chat_id)
                )
            await db.commit()
            await cursor.close()
        

    
 
            
                
