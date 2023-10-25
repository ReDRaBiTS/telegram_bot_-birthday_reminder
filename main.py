import asyncio
from aiogram import Bot, Dispatcher, F
import logging
from app.handlers import hello_message, add_to_DB, start_bot, stop_bot, \
reminder, update_brthday,update_brthday_pre_message, help_func,view_func, admin_info, admin_see_all_users, admin_delete_user
from app.filters import Filter_Re, Filter_Re2, Filter_Re3
from core.classes import DataBaseCommand
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.commands import set_commands
from config import BOT_ID


bot = Bot(token=BOT_ID, parse_mode="HTML")
dp = Dispatcher()
scheduler = AsyncIOScheduler()


async def main() -> None:

    await set_commands(bot)
    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)
    dp.message.register(hello_message, F.text == "/start")
    dp.message.register(help_func, F.text == "/help")
    dp.message.register(view_func, F.text == "/view")
    dp.message.register(update_brthday_pre_message, F.text == "/update")
    dp.message.register(admin_info, F.text == "/admin")
    dp.message.register(admin_see_all_users, F.text == "/see")
    dp.message.register(add_to_DB, Filter_Re())
    dp.message.register(update_brthday, Filter_Re2())
    dp.message.register(admin_delete_user, Filter_Re3())
    # scheduler.add_job(reminder, 'interval', seconds=60, kwargs={'bot':bot})
    scheduler.add_job(reminder, 'interval', seconds=3600 *
                      24, kwargs={'bot': bot})
    scheduler.start()

    await asyncio.gather(DataBaseCommand.db_initialization(),
                         dp.start_polling(bot))


if __name__ == '__main__':
    logging.basicConfig(filename='log.txt', level=logging.DEBUG,
                        format='%(levelname)s: %(asctime)s - %(message)s')
    logging.debug("Бот запущений")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Вихід зпрограми")
        logging.debug("Ручне закритя бота")
