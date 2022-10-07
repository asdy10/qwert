import sqlite3 as lite
import threading

lock = threading.Lock()

class DatabaseManager(object):

    def __init__(self, path):
        self.conn = lite.connect(path, check_same_thread=False)
        self.conn.execute('pragma foreign_keys = on')
        self.conn.commit()
        self.cur = self.conn.cursor()

    def create_tables(self):
        self.query('CREATE TABLE IF NOT EXISTS users (cid int, user_name text, balance float,'
                   'referal int, buyouts int, reviews int, buyout_price float, review_price float,'
                   ' ref_percent float, ref_bonus float)')
        self.query('CREATE TABLE IF NOT EXISTS buyout_templates (cid int, idt text, link text,'
                   'keywords text, count_products int, address text, date_buyouts text)')
        self.query('CREATE TABLE IF NOT EXISTS buyouts (cid int, idx text,'
                   'link text, keywords text, count_products int, '
                   'address text, date_buyouts text, status text, review bool, bid int)')
        self.query('CREATE TABLE IF NOT EXISTS reviews (cid int, idx text, message text,'
                   ' date_review text, images text)')
        self.query('CREATE TABLE IF NOT EXISTS browsers (bid int, phone text, proxy text'
                   ' user_agent text)')
        self.query('CREATE TABLE IF NOT EXISTS bot_data (payment text, token text,'
                   ' buyout_price float, review_price float)')
        self.query('CREATE TABLE IF NOT EXISTS graph (cid int, idt text, gid text,'
                   ' count int, date text)')
        self.query('CREATE TABLE IF NOT EXISTS referals (cid int, idx text, profit text, date text)')
        self.query('CREATE TABLE IF NOT EXISTS buffer (cid TEXT, text TEXT)')

    def query(self, arg, values=None):
        with lock:
            if values == None:
                self.cur.execute(arg)
            else:
                self.cur.execute(arg, values)
            self.conn.commit()

    def fetchone(self, arg, values=None):
        with lock:
            if values == None:
                self.cur.execute(arg)
            else:
                self.cur.execute(arg, values)
            return self.cur.fetchone()

    def fetchall(self, arg, values=None):
        with lock:
            if values == None:
                self.cur.execute(arg)
            else:
                self.cur.execute(arg, values)
            return self.cur.fetchall()

    def __del__(self):
        self.conn.close()


'''

users: cid int, user_name text, balance float, referal int, buyouts int, reviews int, discount int, ref_percent float, ref_bonus float

buyout templates: cid int, idt int, link text, keywords text, count_products int, address text, date_buyouts text

buyouts: cid int, idx int, link text, keywords text, count_products int, cost float,
         address text, date_buyouts text, status text, review bool, bid int, new_price float

reviews: idx int, message text, date_review text, images text

browsers: bid int, phone text, proxy text, user_agent text, payment text, token text, discount float

graph: cid int, idt text, gid text, count int, date text, price float, completed bool

bot_data: discount float, payment text, token text

referals: cid int, idx text, profit text, date text

'''
