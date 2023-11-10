from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command='update',
            description='Оновити вашу дату народження'
        ),
        BotCommand(
            command='help',
            description='Опис роботи бота'
        ),
        BotCommand(
            command='view',
            description='Переглянути дату свого ДР'
        ),
        BotCommand(
            command='donate',
            description='Допомогти розробнику копіїчкою'
        )
    ]
    await bot.set_my_commands(commands, BotCommandScopeDefault())
