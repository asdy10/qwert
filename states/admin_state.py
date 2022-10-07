from aiogram.dispatcher.filters.state import StatesGroup, State


class AdminState(StatesGroup):
    start = State()
    set_discount = State()
    set_payment = State()
    set_token = State()
    get_user_id = State()
    set_user_discount = State()
    set_b_r_price_user_id = State()
    set_buyout_price = State()
    set_review_price = State()
    set_status_buyout_idx = State()
    set_status_buyout_status = State()
    get_buyout_idx = State()
    get_cid = State()
    set_ref_cid = State()
    set_ref_bonus = State()


class AddAccountState(StatesGroup):
    count_mw = State()
    # phone = State()
    # proxy = State()
    # user_agent = State()
    # code_check = State()
    # resend_code = State()


class AddProxyState(StatesGroup):
    proxy = State()
    proxy_key = State()
