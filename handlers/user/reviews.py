import asyncio
import os
from datetime import datetime

from aiogram.types import Message, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, \
    CallbackQuery, ContentType
from aiogram.dispatcher import FSMContext
from aiogram.utils.callback_data import CallbackData

from handlers.user.buyout_menu import process_buyout
from handlers.user.utils import save_image
from keyboards.default.markups import *
from loader import dp, db, bot
from filters import IsUser
from states import ReviewsState
from utils.connect_tg_with_browser.aggregator import agg
from utils.db_get_info.get_set_info_db import get_archive_buyouts, get_review_of_buyout, create_review, \
    change_review_of_buyout_to_true, get_review_of_user, get_reviews, set_reviews, get_buyout_idx, \
    get_all_archive_buyouts, get_all_browsers
from utils.wb_api.work_wb_api import get_image_url_product


@dp.message_handler(IsUser(), text=reviews)
async def process_reviews(message: Message, state: FSMContext):
    await ReviewsState.start.set()
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(my_reviews, make_review)
    markup.add(back_message)
    await message.answer('Вы хотите заказать отзыв или посмотреть уже опубликованные отзывы?', reply_markup=markup)


@dp.message_handler(IsUser(), text=back_message, state=ReviewsState.start)
async def process_reviews_back(message: Message, state: FSMContext):
    await state.finish()
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(buyout, reviews)
    markup.add(balance, info)
    await message.answer('Меню', reply_markup=markup)


@dp.message_handler(IsUser(), text=my_reviews, state=ReviewsState.start)
async def process_my_reviews(message: Message, state: FSMContext):
    res = await get_review_of_user(message.from_user.id)
    if res:
        for i in res:
            await message.answer(f'<b>Заказ №{i[1].split("_")[1]}\nОтзыв:</b>\n{i[2]}\n<b>Дата отзыва:</b> {i[3]}')
    else:
        await message.answer('У вас пока нет отзывов')


review_cb = CallbackData('somearg', 'pid', 'action', 'man', 'woman')


@dp.message_handler(IsUser(), text=make_review, state=ReviewsState.start)
async def process_make_review(message: Message, state: FSMContext):
    count_rev = 0
    if await get_reviews(message.from_user.id) > 0:
        buyouts = await get_all_archive_buyouts()
        if buyouts:
            links = []
            result = {}
            browsers = await get_all_browsers()
            browsers_dict = {}
            for b in browsers:
                browsers_dict[str(b[0])] = b[4]
            for i in buyouts:
                if i[9] not in [2, '2']:
                    err = False
                    if browsers_dict[str(i[9])] == 'man':
                        m, w = 1, 0
                    else:
                        m, w = 0, 1
                    if i[8] in [True, 1, '1']:
                        err = True
                    if not err:
                        if i[2] not in links:
                            links.append(i[2])
                            result[i[2]] = {'keywords': i[3], 'review_man': m, 'review_woman': w}
                        else:
                            result[i[2]]['review_man'] = result[i[2]]['review_man'] + m
                            result[i[2]]['review_woman'] = result[i[2]]['review_woman'] + w
            if result:
                for i in result:
                    markup = InlineKeyboardMarkup()
                    pid = i.split('/')[-2]
                    btn = InlineKeyboardButton('Оставить отзыв', callback_data=review_cb.new(pid=pid, action='make_review',
                                               man=result[i]['review_man'], woman=result[i]['review_woman']))
                    markup.add(btn)
                    img = f"product_images\\{pid}.png"
                    try:
                        open(img, 'r')
                    except:

                        url = get_image_url_product(pid)
                        save_image(url)
                    await message.answer_photo(open(img, 'rb'), caption=f'Ссылка: {i}\nКлючевая фраза: {result[i]["keywords"]}'
                                         f'\nМужских: {result[i]["review_man"]}\nЖенских: {result[i]["review_woman"]}', reply_markup=markup)
                    # await message.answer(f'Ссылка: {i}\nКлючевая фраза: {result[i]["keywords"]}'
                    #                      f'\nМужских: {result[i]["review_man"]}\nЖенских: {result[i]["review_woman"]}', reply_markup=markup)
                await ReviewsState.next()
            else:
                await message.answer('На данный момент у вас нет выкупов на которые можно оставить отзыв')



        else:
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(buyout, back_message)
            await message.answer('На данный момент у вас нет выкупов', reply_markup=markup)
    else:
        await message.answer('Для того чтобы заказать отзыв, необходимо купить "Отзыв" в разделе баланса')


@dp.message_handler(IsUser(), text=buyout, state=ReviewsState.review_check_buyout)
async def process_make_review_buyout(message: Message, state: FSMContext):
    await process_buyout(message, state)


@dp.message_handler(IsUser(), text=back_message, state=ReviewsState.review_check_buyout)
async def process_make_review_back(message: Message, state: FSMContext):
    await ReviewsState.start.set()
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(my_reviews, make_review)
    markup.add(back_message)
    await message.answer('Выберите интересующий пункт', reply_markup=markup)


@dp.callback_query_handler(IsUser(), review_cb.filter(action='make_review'), state=ReviewsState.review_check_buyout)
async def process_make_review_callback(query: CallbackQuery, callback_data: dict, state: FSMContext):
    await ReviewsState.next()
    async with state.proxy() as data:
        data['pid'] = callback_data['pid']
        data['man'] = callback_data['man']
        data['woman'] = callback_data['woman']

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(man_acc, woman_acc)
    markup.add(cancel_message)
    await query.message.answer('Мужской или женский аккаунт использовать для отзыва?', reply_markup=markup)


@dp.message_handler(IsUser(), lambda message: message.text not in [cancel_message], state=ReviewsState.review_male)
async def process_make_review_male(message: Message, state: FSMContext):
    if message.text in [man_acc, woman_acc]:
        male = 'man' if message.text == man_acc else 'woman'
        async with state.proxy() as data:
            data['male'] = male
            man = data['man']
            woman = data['woman']
        err = 0
        if male == 'man':
            if int(man) < 1:
                await message.answer('Мужских аккаунтов нет')
                err = 1
        if male == 'woman':
            if int(woman) < 1:
                await message.answer('Женских аккаунтов нет')
                err = 1
        if err == 0:
            await message.answer('Введите текст отзыва', reply_markup=cancel_markup())
            await ReviewsState.next()
    else:
        await message.answer('Такого варианта нет', reply_markup=cancel_markup())


@dp.message_handler(IsUser(), text=cancel_message, state=ReviewsState.review_text)
async def process_make_review_text_cancel(message: Message, state: FSMContext):
    await process_reviews(message, state)


@dp.message_handler(IsUser(), lambda message: message.text not in [cancel_message], state=ReviewsState.review_text)
async def process_make_review_text(message: Message, state: FSMContext):
    text = message.text
    if len(text) > 10:
        async with state.proxy() as data:
            data['text'] = text
            pid = data['pid']
            data['images'] = '0'
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(ready_message, back_message)
        await message.answer('Отправьте фотографии для отзыва и нажмите "Готово". Возможно отправить до 5 фото.', reply_markup=markup)
        await ReviewsState.next()
    else:
        await message.answer('Длина отзыва должна быть больше 10 символов')


@dp.message_handler(IsUser(), content_types=ContentType.PHOTO, state=ReviewsState.review_image)
async def process_image_photo(message: Message, state: FSMContext):
    async with state.proxy() as data:
        pid = data['pid']
    fileID = message.photo[-1].file_id
    file_info = await bot.get_file(fileID)
    downloaded_file = (await bot.download_file(file_info.file_path)).read()
    dir = os.path.abspath(os.curdir)
    img_name = f'{dir}\\data\\review_images\\image_{pid}{round(datetime.timestamp(datetime.now()))}.png'
    with open(img_name, 'wb') as f:
        f.write(downloaded_file)
    async with state.proxy() as data:
        try:
            if img_name not in data['images']:
                data['images'] = f'{data["images"]};{img_name}'
        except:
            data['images'] = img_name


@dp.message_handler(IsUser(), text=ready_message, state=ReviewsState.review_image)
async def process_make_review_image(message: Message, state: FSMContext):
    async with state.proxy() as data:
        text = data['text']
        pid = data['pid']

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(confirm_message, change_message)
    await message.answer(f'Проверьте данные', reply_markup=markup)
    await ReviewsState.next()


@dp.message_handler(IsUser(), text=back_message, state=ReviewsState.review_image)
async def process_make_review_image(message: Message, state: FSMContext):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(cancel_message)
    await message.answer('Введите текст отзыва', reply_markup=markup)
    await ReviewsState.review_text.set()


@dp.message_handler(IsUser(), text=confirm_message, state=ReviewsState.review_confirm)
async def process_make_review_text_confirm(message: Message, state: FSMContext):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('/menu')
    async with state.proxy() as data:
        text = data['text']
        pid = data['pid']
        images = data['images']
        male = data['male']
    cid = message.from_user.id
    buyouts = await get_all_archive_buyouts()
    links = []
    result = {}
    browsers = await get_all_browsers()
    browsers_dict = {}
    for b in browsers:
        browsers_dict[str(b[0])] = b[4]
    for b in buyouts:
        try:
            if pid in b[2] and browsers_dict[str(b[9])] == male and b[8] not in [1, '1', True]:
                idx = b[1]
                break
        except:
            pass
    await create_review(cid, idx, text, datetime.today().strftime("%d.%m.%Y %H:%M:%S"), images)
    link = (await get_buyout_idx(idx))[2]
    await agg.make_review_task(idx, link, text, images, stars=5)
    await message.answer('Заказ принят', reply_markup=markup)
    await state.finish()


@dp.message_handler(IsUser(), text=change_message, state=ReviewsState.review_confirm)
async def process_make_review_text_change(message: Message, state: FSMContext):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(cancel_message)
    await message.answer('Введите текст отзыва', reply_markup=markup)
    await ReviewsState.review_text.set()
