from aiogram.dispatcher.filters.state import StatesGroup, State


class ErrorState(StatesGroup):
    make_pay = State()
    confirm_pay = State()
