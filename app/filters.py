
from typing import Any
from aiogram.filters import BaseFilter
from aiogram.types import Message
import re

class Filter_Re(BaseFilter):
    async def __call__(self, message : Message) -> bool:
        regex = re.compile(r"(\d\d?).(\d\d?).(\d\d\d\d)")
        if re.findall(regex, message.text):
            return True
        else:
            return False
        

class Filter_Re2(BaseFilter):
    async def __call__(self, message : Message) -> bool:
        regex = re.compile(r"(\d\d\d\d).(\d\d?).(\d\d?)")
        if re.findall(regex, message.text):
            return True
        else:
            return False
        
class Filter_Re3(BaseFilter):
    async def __call__(self, message :  Message) -> bool:
        regex = re.compile(r"delete.*")
        if re.findall(regex, message.text):
            return True
        else:
            return False
