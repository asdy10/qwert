from aiogram.dispatcher.filters.state import StatesGroup, State


class BalanceState(StatesGroup):
    start = State()
    balance_buyout_count = State()
    balance_buyout_count_confirm = State()
    balance_reviews_count = State()
    balance_reviews_count_confirm = State()
    add_balance_count = State()
    add_balance_count_confirm = State()
    add_balance_check_payment = State()