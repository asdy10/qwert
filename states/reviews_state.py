from aiogram.dispatcher.filters.state import StatesGroup, State


class ReviewsState(StatesGroup):
    start = State()
    review_check_buyout = State()
    review_male = State()
    review_text = State()
    review_image = State()
    review_confirm = State()
