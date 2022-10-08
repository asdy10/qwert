from datetime import datetime

from loader import db

"""users"""


async def is_user_exist(cid):
    if db.fetchone('SELECT * FROM users WHERE cid=?', (cid,)):
        return True
    else:
        return False


async def create_user(cid, user_name='no username', balance=0, referal=0, buyouts=0, reviews=0, b_price=0, r_price=0, ref_percent=5, ref_bonus=0):
    db.query('INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (cid, user_name,
             balance, referal, buyouts, reviews, b_price, r_price, ref_percent, ref_bonus))


async def get_user_cid(cid):
    try:
        return db.fetchone('SELECT * FROM users WHERE cid=?', (cid,))
    except:
        return ''


async def get_referer(cid):
    return db.fetchone('SELECT referal FROM users WHERE cid=?', (cid,))[0]


async def get_balance(cid):
    return db.fetchone('SELECT balance FROM users WHERE cid=?', (cid,))[0]


async def set_balance(cid, x):
    db.query('UPDATE users SET balance=? WHERE cid=?', (x, cid))


async def get_buyouts(cid):
    return db.fetchone('SELECT buyouts FROM users WHERE cid=?', (cid,))[0]


async def set_buyouts(cid, x):
    db.query('UPDATE users SET buyouts=? WHERE cid=?', (x, cid))


async def get_reviews(cid):
    return db.fetchone('SELECT reviews FROM users WHERE cid=?', (cid,))[0]


async def set_reviews(cid, x):
    db.query('UPDATE users SET reviews=? WHERE cid=?', (x, cid))


async def get_discount_cid(cid):
    return db.fetchone('SELECT discount FROM users WHERE cid=?', (cid,))[0]


async def set_discount_cid(cid, x):
    db.query('UPDATE users SET discount=? WHERE cid=?', (x, cid))


async def get_b_r_price(cid):
    return db.fetchall('SELECT buyout_price, review_price FROM users WHERE cid=?', (cid,))[0]


async def set_b_r_price(cid, b_price, r_price):
    db.query('UPDATE users SET buyout_price=?, review_price=? WHERE cid=?', (b_price, r_price, cid))


async def get_ref_percent_cid(cid):
    return db.fetchone('SELECT ref_percent FROM users WHERE cid=?', (cid,))[0]


async def set_ref_percent_cid(cid, x):
    db.query('UPDATE users SET ref_percent=? WHERE cid=?', (x, cid))


async def get_ref_bonus_cid(cid):
    return db.fetchone('SELECT ref_bonus FROM users WHERE cid=?', (cid,))[0]


async def set_ref_bonus_cid(cid, x):
    db.query('UPDATE users SET ref_bonus=? WHERE cid=?', (x, cid))

"""buyouts"""


async def create_buyout(cid, idx, link, keywords, count, address, date_buyouts, status, review, bid, price=0, receipt=0):
    db.query('INSERT INTO buyouts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
             (cid, idx, link, keywords, count, address, date_buyouts, status, review, bid, price, receipt))


async def get_all_buyouts():
    return db.fetchall('SELECT * FROM buyouts')


def get_all_buyouts_not_async():
    return db.fetchall('SELECT * FROM buyouts')


async def get_all_buyouts_of_user(user_id_):
    try:
        return db.fetchall('SELECT * FROM buyouts WHERE cid=?', (user_id_,))
    except:
        return ''


async def get_buyout_idx(idx):
    try:
        return db.fetchone('SELECT * FROM buyouts WHERE idx=?', (idx,))
    except:
        return ''


async def get_all_archive_buyouts():
    try:
        return db.fetchall('SELECT * FROM buyouts WHERE status=?', ('complete', ))
    except:
        return ''


async def get_archive_buyouts(user_id_):
    try:
        return db.fetchall('SELECT * FROM buyouts WHERE (cid=? and status=?)', (user_id_, 'complete'))
    except:
        return ''


async def get_buyouts_in_delivery(user_id_):
    try:
        arr = db.fetchall('SELECT * FROM buyouts WHERE (cid=? and status!=?)', (user_id_, 'complete'))
        new_arr = []
        for i in arr:
            if i[7] not in ['Готов к выдаче', 'complete', 'Платеж не удался, заказ отменен', 'process', 'Готов к получению', 'new'] and 'error' not in i[7]:
                new_arr.append(i)
        return new_arr
    except:
        return ''


def get_buyouts_in_delivery_all():
    try:
        arr = db.fetchall('SELECT * FROM buyouts WHERE status!=?', ('complete',))
        new_arr = []
        for i in arr:
            if i[7] not in ['Готов к выдаче', 'complete', 'Платеж не удался, заказ отменен', 'process', 'Готов к получению', 'new'] and 'error' not in i[7]:
                new_arr.append(i)
        return new_arr
    except:
        return ''


def get_buyouts_paid_all():
    try:
        arr = db.fetchall('SELECT * FROM buyouts WHERE status!=? ORDER BY date_buyouts', ('new',))
        new_arr = []
        for i in arr:
            if i[7] not in ['Платеж не удался, заказ отменен', 'process', 'new'] and 'error' not in i[7]:
                new_arr.append(i)
        return new_arr
    except Exception as e:
        print(e)
        return ''


def get_buyouts_paid_bid(bid):
    try:
        arr = db.fetchall('SELECT * FROM buyouts WHERE (status!=? and bid=?) ORDER BY date_buyouts', ('new', bid))
        new_arr = []
        for i in arr:
            if i[7] not in ['Платеж не удался, заказ отменен', 'process', 'new'] and 'error' not in i[7]:
                new_arr.append(i)
        return new_arr
    except Exception as e:
        print(e)
        return ''


def get_all_buyouts_in_delivery_bid(bid):
    try:
        arr = db.fetchall('SELECT * FROM buyouts WHERE (bid=? and status!=?)', (bid, 'complete'))
        #arr = db.fetchall('SELECT * FROM buyouts WHERE bid=?', (bid,))
        new_arr = []
        for i in arr:
            if i[7] not in ['Готов к выдаче', 'complete', 'Платеж не удался, заказ отменен', 'process', 'Готов к получению', 'new'] and 'error' not in i[7]:#
                new_arr.append(i)
        return new_arr
    except:
        return ''


async def get_buyouts_error(user_id_):
    try:
        arr = db.fetchall('SELECT * FROM buyouts WHERE (cid=? and status!=?)', (user_id_, 'complete'))
        new_arr = []
        for i in arr:
            if 'error' in i[7] or 'Платеж не удался, заказ отменен' in i[7]:
                new_arr.append(i)
        return new_arr
    except:
        return ''


def get_buyouts_error_all():
    try:
        arr = db.fetchall('SELECT * FROM buyouts WHERE status!=?', ('complete',))
        new_arr = []
        for i in arr:
            if 'error' in i[7] or 'Платеж не удался, заказ отменен' in i[7]:
                new_arr.append(i)
        return new_arr
    except:
        return ''


async def get_buyouts_ready_to_get(user_id_):
    try:
        return db.fetchall('SELECT * FROM buyouts WHERE (cid=? and status=? or cid=? and status=?)', (user_id_, 'Готов к выдаче', user_id_, 'Готов к получению'))
    except Exception as e:
        print(e)
        return ''


def get_buyouts_ready_to_get_all():
    try:
        return db.fetchall('SELECT * FROM buyouts WHERE (status=? or status=?)', ('Готов к выдаче', 'Готов к получению'))
    except Exception as e:
        print(e)
        return ''


def get_buyouts_ready_to_get_bid(bid):
    try:
        return db.fetchall('SELECT * FROM buyouts WHERE (bid=? and status=? or bid=? and status=?)', (bid, 'Готов к выдаче', bid, 'Готов к получению'))
    except Exception as e:
        print(e)
        return ''


def get_buyouts_process_cid(cid):
    try:
        return db.fetchall('SELECT * FROM buyouts WHERE (cid=? and status=? or cid=? and status=?)', (cid, 'process', cid, 'new'))
    except Exception as e:
        print(e)
        return ''


def get_buyouts_process_all():
    try:
        return db.fetchall('SELECT * FROM buyouts WHERE (status=? or status=?)', ('process', 'new'))
    except Exception as e:
        print(e)
        return ''


def get_all_buyouts_in_delivery():
    try:
        arr = db.fetchall('SELECT * FROM buyouts WHERE status!=?', ('complete',))
        new_arr = []
        for i in arr:
            if i[7] not in ['Готов к выдаче', 'complete', 'Платеж не удался, заказ отменен', 'process', 'Готов к получению', 'new'] and 'error' not in i[7]:#
                new_arr.append(i)
        return new_arr
    except:
        return ''


async def get_all_buyouts_after_error():
    try:
        return db.fetchall('SELECT * FROM buyouts WHERE status=?', ('after error',))
    except:
        return ''


async def get_all_buyouts_new():
    try:
        return db.fetchall('SELECT * FROM buyouts WHERE status=?', ('new',))
    except:
        return ''


def get_all_receipts():
    try:
        res = db.fetchall('SELECT receipt FROM buyouts')
        result = []
        for i in res:
            if i[0] not in result and i[0] not in [None, '0']:
                result.append(i[0])
        return result
    except:
        return ''


async def get_count_of_buyouts_user(user_id_):
    return len(db.fetchall('SELECT idx FROM buyouts WHERE cid=?', (user_id_,)))


def get_last_num_buyout_user(user_id_):
    res = db.fetchall('SELECT * FROM buyouts WHERE cid=?', (user_id_,))
    return int(res[-1][1].split('_')[1])


async def get_status_of_buyout(idx_):
    try:
        return db.fetchone('SELECT status FROM buyouts WHERE idx=?', (idx_,))[0]
    except:
        return ''


def set_status_of_buyout(idx_, status_):
    try:
        if type(status_) != str:

            if status_['receipt'] not in [0]:
                db.query('UPDATE buyouts SET status=?, price=?, receipt=?, date_buyouts=? WHERE idx=?', (status_['status'], status_['price'], status_['receipt'], status_['order_date'], idx_))
            else:
                db.query('UPDATE buyouts SET status=?, price=?, date_buyouts=? WHERE idx=?', (status_['status'], status_['price'], status_['order_date'], idx_))
            return True
        else:
            db.query('UPDATE buyouts SET status=? WHERE idx=?', (status_, idx_))
    except Exception as e:
        print(e)
        return False


def set_date_buyout(idx):
    db.query('UPDATE buyouts SET date_buyouts=? WHERE idx=?', (datetime.today().strftime("%d.%m.%Y %H:%M:%S"), idx))


async def set_free_bid_of_buyout(idx_, bid):
    try:
        db.query('UPDATE buyouts SET bid=? WHERE idx=?', (bid, idx_))
    except:
        pass


async def get_price_of_buyout(idx_):
    try:
        return db.fetchall('SELECT bot_price, user_price FROM buyouts WHERE idx=?', (idx_,))[0]
    except:
        return ''


async def set_price_of_buyout(idx_, bot_price, user_price):
    try:
        db.query('UPDATE buyouts SET bot_price=?, user_price=? WHERE idx=?', (bot_price, user_price, idx_))
    except:
        pass


async def change_review_of_buyout_to_true(idx_):
    try:
        db.query('UPDATE buyouts SET review=? WHERE idx=?', (True, idx_))
        return True
    except:
        return False


async def get_bid_buyouts_of_user():
    try:
        res = db.fetchall('SELECT bid FROM buyouts')
        return [str(i[0]) for i in res]
    except:
        return ''


async def get_bid_of_buyout(idx):
    try:
        return db.fetchone('SELECT bid FROM buyouts WHERE idx=?', (idx,))[0]
    except:
        return ''


def delete_buyout(idx):
    db.query('DELETE FROM buyouts WHERE idx=?', (idx,))


def get_addresses():
    res = db.fetchall('SELECT address FROM buyouts GROUP BY address')
    return [i[0] for i in res]

"""templates"""


async def create_buyout_template(cid: int, idt: str, link: str, keywords: str,
                                 count_products: int, address: str, date_buyouts: str):
    db.query('INSERT INTO buyout_templates VALUES (?, ?, ?, ?, ?, ?, ?)',
             (cid, idt, link, keywords, count_products, address, date_buyouts))


async def get_all_templates_of_user(cid):
    try:
        return db.fetchall('SELECT * FROM buyout_templates WHERE cid=?', (cid,))
    except:
        return ''


async def get_count_of_buyout_templates_user(cid):
    return len(db.fetchall('SELECT idt FROM buyout_templates WHERE cid=?', (cid,)))


async def get_template(idt_):
    try:
        return db.fetchone('SELECT * FROM buyout_templates WHERE idt=?', (idt_,))
    except:
        return ''


async def delete_template(idt_):
    try:
        db.query('DELETE FROM buyout_templates WHERE idt=?', (idt_,))
        return True
    except:
        return False


async def get_number_of_last_template(cid):
    try:
        return db.fetchall('SELECT * FROM buyout_templates WHERE cid=?', (cid,))[-1][1].split('_')[1]
    except:
        return 0


"""reviews"""


async def create_review(cid: int, idx: str, message: str, date_review: str, images):
    db.query('INSERT INTO reviews VALUES (?, ?, ?, ?, ?)', (cid, idx, message, date_review, images))


async def get_all_reviews():
    return db.fetchall('SELECT * FROM reviews')


async def get_review_of_buyout(idx_):
    try:
        return db.fetchone('SELECT * FROM reviews WHERE idx=?', (idx_,))
    except:
        return ''


async def get_review_of_user(cid_):
    try:
        return db.fetchall('SELECT * FROM reviews WHERE cid=?', (cid_,))
    except:
        return ''


def delete_review(idx):
    db.query('DELETE FROM reviews WHERE idx=?', (idx,))




"""Bot data"""


async def get_discount():
    return db.fetchone('SELECT discount FROM bot_data')[0]


async def set_discount(value):
    db.query('UPDATE bot_data SET discount=?', (value,))


async def get_payment_default():
    return db.fetchone('SELECT payment FROM bot_data')[0]


async def set_payment_default(value):
    db.query('UPDATE bot_data SET payment=?', (value,))


async def get_token_default():
    return db.fetchone('SELECT token FROM bot_data')[0]


async def set_token_default(value):
    db.query('UPDATE bot_data SET token=?', (value,))


async def get_b_r_price_default():
    return db.fetchall('SELECT buyout_price, review_price FROM bot_data')[0]


async def set_b_r_price_default(b, r):
    db.query('UPDATE bot_data SET buyout_price=?, review_price=?', (b, r))


"""Graph"""


async def create_graph(cid, idt, gid, count, date, male):
    db.query('INSERT INTO graph VALUES (?, ?, ?, ?, ?, ?)', (cid, idt, gid, count, date, male))


async def get_all_graphs():
    return db.fetchall('SELECT * FROM graph')


async def get_graph_cid(cid):
    try:
        return db.fetchall('SELECT * FROM graph WHERE cid=?', (cid,))
    except:
        return ''


async def get_graph_idt(idt):
    try:
        return db.fetchall('SELECT * FROM graph WHERE idt=?', (idt,))
    except:
        return ''


async def get_graph_gid(gid):
    try:
        return db.fetchone('SELECT * FROM graph WHERE gid=?', (gid,))
    except:
        return ''


async def update_date_graph(gid, date):
    db.query('UPDATE graph SET date=? WHERE gid=?', (date, gid))


async def delete_graph_gid(gid):
    try:
        db.query('DELETE FROM graph WHERE gid=?', (gid,))
    except:
        pass


async def get_number_of_last_graph(cid):
    try:
        return db.fetchall('SELECT * FROM graph WHERE cid=?', (cid,))[-1][2].split('_')[1]
    except:
        return 0


"""Browsers"""


def create_browser(bid, phone, proxy, user_agent, male, name, qr):
    db.query('INSERT INTO browsers VALUES (?, ?, ?, ?, ?, ?, ?)', (bid, phone, str(proxy), user_agent, male, name, qr))


async def get_all_browsers():
    return db.fetchall('SELECT * FROM browsers')


async def get_browser_bid(bid):
    return db.fetchone('SELECT * FROM browsers WHERE bid=?', (bid,))


def get_browser_bid_not_async(bid):
    return db.fetchone('SELECT * FROM browsers WHERE bid=?', (bid,))


async def get_phones():
    return db.fetchall('SELECT phone FROM browsers')


async def get_bid():
    return [i[0] for i in db.fetchall('SELECT bid FROM browsers')]


def get_bid_():
    return [i[0] for i in db.fetchall('SELECT bid FROM browsers')]


async def get_discount_browser(bid):
    return db.fetchone('SELECT discount FROM browsers WHERE bid=?', (bid,))[0]


async def set_discount_browser(bid, dis):
    db.query('UPDATE browsers SET discount=? WHERE bid=?', (dis, bid))


async def set_proxy(bid, proxy):
    db.query('UPDATE browsers SET proxy=? WHERE bid=?', (proxy, bid))


def set_qr(bid, qr):
    db.query('UPDATE browsers SET qr=? WHERE bid=?', (qr, bid))


def get_qr(bid):
    return db.fetchone('SELECT qr FROM browsers WHERE bid=?', (bid,))[0]




"""Referals"""


async def create_referal(cid, idx, profit, date):
    db.query('INSERT INTO referals VALUES (?, ?, ?, ?)', (cid, idx, profit, date))


async def get_referals_cid(cid):
    return db.fetchall('SELECT * FROM referals WHERE cid=?', (cid,))


async def get_referals_idx(idx):
    return db.fetchall('SELECT * FROM referals WHERE idx=?', (idx,))[0]


"""Buffer"""


def create_message(cid, text):
    db.query(f'INSERT INTO buffer (cid, text) VALUES ("{cid}", "{text}")')


async def get_new_message():
    return db.fetchall('SELECT * FROM buffer')


def get_all_messages():
    return db.fetchall('SELECT * FROM buffer')


async def delete_message(cid):
    db.query(f'DELETE FROM buffer WHERE cid="{cid}"')


def delete_message_(cid):
    db.query(f'DELETE FROM buffer WHERE cid="{cid}"')


def set_login_status(cid, status):
    db.query(f'INSERT INTO buffer (cid, text) VALUES ("login{cid}", "{status}")')


def update_login_status(cid, status):
    db.query(f'UPDATE buffer SET text="{status}" WHERE cid="login{cid}"')


def get_login_status(cid):
    return db.fetchone(f'SELECT text FROM buffer WHERE cid="login{cid}"')[0]


def create_proxy(proxy, proxy_key):
    pid = len(db.fetchall('SELECT * FROM proxy')) + 1
    db.query('INSERT INTO proxy VALUES (?, ?, ?)', (pid, proxy, proxy_key))


def get_proxy_pid(pid):
    return db.fetchone('SELECT ip, proxy_key FROM proxy WHERE pid=?', (pid,))


def get_pids_proxy():

    return [i[0] for i in db.fetchall('SELECT pid FROM proxy')]


"""Images"""


def create_product_image(pid, url):
    db.query('INSERT INTO product_images VALUES (?, ?)', (pid, url))


def get_product_image_pid(pid):
    try:
        return db.fetchone('SELECT url FROM product_images WHERE pid=?', (pid,))[0]
    except:
        return ''


"""Seller"""


def create_seller_info(arg: dict):
    pid = arg['pid']
    inn = arg['inn']
    ogrn = 0
    name = arg['supplierName']
    db.query('INSERT INTO seller VALUES (?, ?, ?, ?)', (pid, name, ogrn, inn))


def get_seller_info(pid):
    return db.fetchone('SELECT * FROM seller WHERE pid=?', (pid,))


