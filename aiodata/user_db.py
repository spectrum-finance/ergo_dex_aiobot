import os
import sys
import aiosqlite


BASE_DIR = os.path.dirname(__file__)
STATE_DIR = sys.argv[1] if len(sys.argv) >= 2 else BASE_DIR

db_name = 'data'

def database_path(db_name):
    return os.path.join(STATE_DIR, f'{db_name}.sqlite')

def database_exists(db_name):
    #print(database_path(db_name))
    return os.path.exists(database_path(db_name))

#######################################


async def is_admin(tg_id, db_name=db_name):
    if database_exists(db_name):
        #print(1)
        async with aiosqlite.connect(database_path(db_name)) as db:
            res = await db.execute(f'''SELECT is_admin FROM users WHERE tg_id = {tg_id}''')
            res = await res.fetchone()
            if res == None:
                return 0
            return res[0]

async def add_user(db_name, tg_id, name, username, is_admin = 0):
    if database_exists(db_name):
        #print(1)
        async with aiosqlite.connect(database_path(db_name)) as db:
            await db.execute(f'''INSERT INTO users(tg_id, is_admin, name, username) VALUES
                ( {tg_id}, {is_admin}, "{name}", "{username}" )
            ''')
            await db.commit()

async def get_all_users(db_name=db_name):
    if database_exists(db_name):
        #print(1)
        async with aiosqlite.connect(database_path(db_name)) as db:
            res = await db.execute(f'''SELECT * FROM users ''')
            res = await res.fetchall()
            return res

async def get_user(tg_id, db_name=db_name):
    if database_exists(db_name):
        #print(1)
        async with aiosqlite.connect(database_path(db_name)) as db:
            res = await db.execute(f'''SELECT * FROM users WHERE tg_id = {tg_id}''')
            res = await res.fetchone()
            return res

async def get_most_active_user( db_name=db_name):
    if database_exists(db_name):
        #print(1)
        async with aiosqlite.connect(database_path(db_name)) as db:
            res = await db.execute(f'''SELECT * FROM users ORDER BY chat_count_mess DESC''')
            res = await res.fetchone()
            return res

async def count_mess_user(tg_id, name, username, db_name=db_name):
    user = await get_user(tg_id)
    if user is None:
        async with aiosqlite.connect(database_path(db_name)) as db:
            await db.execute(f'''INSERT INTO users(tg_id, is_admin, name, username, chat_count_mess) VALUES
                ( {tg_id}, 0, "{name}", "{username}", 1 )
            ''')
            await db.commit()
    else:
        async with aiosqlite.connect(database_path(db_name)) as db:
            await db.execute(f'''UPDATE users SET chat_count_mess = chat_count_mess + 1 WHERE tg_id = {tg_id}
            ''')
            await db.commit()

async def make_admin(tg_id, db_name=db_name):
    user = await get_user(tg_id)
    if user is None:
        print(f"Юзер не найден {tg_id}")
    else:
        async with aiosqlite.connect(database_path(db_name)) as db:
            await db.execute(f'''UPDATE users SET is_admin = 1 WHERE tg_id = {tg_id}
            ''')
            await db.commit()