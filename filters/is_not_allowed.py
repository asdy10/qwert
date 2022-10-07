
from aiogram.types import Message
from aiogram.dispatcher.filters import BoundFilter
from data.config import ALLOWSED_USERS, ADMINS, COURIER


class IsNotAllowedUser(BoundFilter):

    async def check(self, message: Message):
        return message.from_user.id not in ALLOWSED_USERS + ADMINS + COURIER
