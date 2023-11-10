from typing import Any
from aiogram.filters import BaseFilter
from aiogram.types import Message
import re


class Set_Bd(BaseFilter):
    async def __call__(self, message : Message) -> bool:
        try:
            regex = re.compile(r"(\d\d?).(\d\d?).(\d\d\d\d)")
            if re.findall(regex, message.text):
                return True
            else:
                return False
        except TypeError:
            pass

class Update_Bd(BaseFilter):
    async def __call__(self, message : Message) -> bool:
        try:
            regex = re.compile(r"(\d\d\d\d).(\d\d?).(\d\d?)")
            if re.findall(regex, message.text):
                return True
            else:
                return False
        except TypeError:
            pass
class Delete_User(BaseFilter):
    async def __call__(self, message :  Message) -> bool:
        try: 
            regex = re.compile(r"delete .*")
            if re.findall(regex, message.text):
                return True
            else:
                return False
        except TypeError:
            pass
        
class SQL_Command(BaseFilter):
    async def __call__(self, message :  Message) -> bool:
        try:
            regex = re.compile(r"SQL .*")
            if re.findall(regex, message.text):
                return True
            else:
                return False
        except TypeError:
            pass


