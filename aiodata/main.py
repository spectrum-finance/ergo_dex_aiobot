import os
import sys
import aiosqlite
from datetime import datetime
import asyncio
from PIL import Image

BASE_DIR = os.path.dirname(__file__)
STATE_DIR = sys.argv[1] if len(sys.argv) >= 2 else BASE_DIR

db_name = 'data'

def database_path(db_name):
    return os.path.join(STATE_DIR, f'{db_name}.sqlite')

def database_exists(db_name):
    #print(database_path(db_name))
    return os.path.exists(database_path(db_name))

##################################################
##############    USERS   ########################
##################################################

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
            await db.execute(f'''UPDATE users SET is_admin = 1 WHERE tg_id = {tg_id}''')
            await db.commit()

##################################################
##############   SOCIALS INFO    #################
##################################################


async def get_all_soc(db_name=db_name):
    if database_exists(db_name):
        #print(1)
        async with aiosqlite.connect(database_path(db_name)) as db:
            res = await db.execute(f'''SELECT * FROM socials ''')
            res = await res.fetchall()
            return res

async def get_soc_id_by_name(name, db_name=db_name):
    if database_exists(db_name):
        #print(1)
        async with aiosqlite.connect(database_path(db_name)) as db:
            res = await db.execute(f'''SELECT id FROM socials WHERE name_social="{name}" ''')
            res = await res.fetchone()
            if res == None:
                print("Не найдено ID социальной сети по имени")
                return 0
            #print(res[0])
            return res[0]

async def get_soc_name_by_id(id, db_name=db_name):
    if database_exists(db_name):
        #print(1)
        async with aiosqlite.connect(database_path(db_name)) as db:
            res = await db.execute(f'''SELECT name_social FROM socials WHERE id = {id} ''')
            res = await res.fetchone()
            if res is None:
                return None
            return res[0]

async def get_soc_info_by_name(name, db_name=db_name):
    if database_exists(db_name):
        #print(1)
        async with aiosqlite.connect(database_path(db_name)) as db:
            res = await db.execute(f'''SELECT * FROM backup_soc WHERE id_social = {await get_soc_id_by_name(name)} ORDER BY time_edit DESC''')
            res = await res.fetchone()
            return res

async def add_first_backup_soc_by_name_soc(name_soc, db_name=db_name):
    if database_exists(db_name):
        #print(1)
        #print((datetime.now().strftime('%Y-%m-%d %H:%M:%S')[:-3]))
        async with aiosqlite.connect(database_path(db_name)) as db:
            await db.execute(f'''INSERT INTO backup_soc(id_social, time_edit) VALUES
                ( {await get_soc_id_by_name(name_soc)}, CURRENT_TIMESTAMP -  1 )
            ''')
            
            await db.commit()

async def delete_all_backup_soc( db_name=db_name):
    if database_exists(db_name):
        #print(1)
        #print((datetime.now().strftime('%Y-%m-%d %H:%M:%S')[:-3]))
        async with aiosqlite.connect(database_path(db_name)) as db:
            await db.execute(f'''DELETE FROM backup_soc ''')
            
            await db.commit()

async def get_current_backup_by_time(name_soc, db_name=db_name):
    if database_exists(db_name):
        #print(1)
        async with aiosqlite.connect(database_path(db_name)) as db:
            res = await db.execute(f'''SELECT * FROM backup_soc WHERE id_social = {await get_soc_id_by_name(name_soc)}  ORDER BY time_edit DESC''')
            res = await res.fetchone()
            return res

async def get_all_current_backup_by_time_all_data(db_name=db_name):
    if database_exists(db_name):
        all = await get_all_soc()
        all_current = []
        for soc in all:
            current_soc = await get_current_backup_by_time(soc[1])
            all_current.append(current_soc)
        return all_current

async def get_all_current_backup_by_time_pretty(db_name=db_name):
    if database_exists(db_name):
        res = []
        all_data = await get_all_current_backup_by_time_all_data()
        #print(all_data)
        for data in all_data:
            data = list(data)
            #print(data)
            data[1] = await get_soc_name_by_id(data[1])
            res.append(data)
        return res



async def edit_backup_soc_by_atr(name_soc, atr, value, db_name=db_name):
    atrs = ["id","id_social","invite_text","url","img","time_edit"]
    atr_ind = atrs.index(atr)
    if database_exists(db_name):
        current_soc = list(await get_current_backup_by_time(name_soc))
        current_soc[atr_ind] = value
        editted_soc =current_soc[1:-1]
        exec_template = ""
        for inp_atr in editted_soc:
            print(type(inp_atr), inp_atr )
            if inp_atr is None or inp_atr == "None" :
                 exec_template += " NULL, "
            elif type(inp_atr) == str:
                exec_template += "\""+ str(inp_atr)+"\", "
            else:
                exec_template += str(inp_atr)+", "
        exec_template = exec_template[0:-2]
        #print(1)
        print((datetime.now().strftime('%Y-%m-%d %H:%M:%S')[:-3]))
        async with aiosqlite.connect(database_path(db_name)) as db:
            exec_text = f'''INSERT INTO backup_soc(id_social, invite_text, url, img, time_edit) VALUES
                ( {exec_template}, CURRENT_TIMESTAMP )
            '''
            print(exec_text)
            await db.execute(exec_text)
            
            await db.commit()


async def add_soc(db_name, name):
    if database_exists(db_name):
        #print(1)
        async with aiosqlite.connect(database_path(db_name)) as db:
            await db.execute(f'''INSERT INTO socials(name_social,is_work) VALUES
                ( "{name}", 1 )
            ''')
            await db.commit()

async def delete_soc_by_name(db_name, name):
    if database_exists(db_name):
        #print(1)
        async with aiosqlite.connect(database_path(db_name)) as db:
            await db.execute(f'''DELETE FROM socials WHERE name_social = "{name}"
            ''')
            await db.commit()

##################################################
############     WAIT CONTENT    #################
##################################################

async def add_wait_content_from(tg_id,for_, db_name=db_name):
    if database_exists(db_name):
        #print(1)
        async with aiosqlite.connect(database_path(db_name)) as db:
            await db.execute(f'''INSERT INTO wait_content(tg_id, for) VALUES
                ( {tg_id}, "{for_}" )
            ''')
            await db.commit()

async def delete_wait_content_from(tg_id, db_name=db_name):
    if database_exists(db_name):
        #print(1)
        async with aiosqlite.connect(database_path(db_name)) as db:
            await db.execute(f'''DELETE FROM wait_content WHERE tg_id = "{tg_id}"
            ''')
            await db.commit()

async def init_wait_content_from():
    async with aiosqlite.connect(database_path(db_name)) as db:
        await db.execute('''CREATE TABLE wait_content (
                tg_id integer not null,
                for varchar(200) not null
            )''')
        await db.commit()
            
##################################################
##############      TEXT         #################
##################################################

async def add_text_by_name(name,text, db_name=db_name):
    if database_exists(db_name):
        #print(1)
        async with aiosqlite.connect(database_path(db_name)) as db:
            await db.execute(f'''INSERT INTO text(name, text, time_edit) VALUES
                ( "{name}", "{text}", CURRENT_TIMESTAMP )
            ''')
            await db.commit()

async def get_current_text_by_name(name, db_name=db_name):
    if database_exists(db_name):
        #print(1)
        async with aiosqlite.connect(database_path(db_name)) as db:
            res = await db.execute(f'''SELECT * FROM text WHERE name = "{name}"  ORDER BY time_edit DESC''')
            res = await res.fetchone()
            return res

def convert_data(data, file_name):
     
    # Convert binary format to
    # images or files data
    with open(file_name, 'wb') as file:
        file.write(data)
    img = Image.open(file_name)
    print(img)

async def get_all_texts(db_name=db_name):
    if database_exists(db_name):
        #print(1)
        async with aiosqlite.connect(database_path(db_name)) as db:
            res = await db.execute(f'''SELECT name FROM text ORDER BY time_edit DESC''')
            res = await res.fetchall()
            return res

async def edit_text_by_atr(name, atr, value, db_name=db_name):
    if database_exists(db_name):
        async with aiosqlite.connect(database_path(db_name)) as db:
            await db.execute(f'''UPDATE text SET {atr} = "{value}" WHERE name = "{name}"
                    ''')
            await db.commit()

async def insertBLOBtext(name_text, photo, db_name=db_name):
    if database_exists(db_name):
        current_soc = list(await get_current_text_by_name(name_text))
        id_text = current_soc[0]
        #print(1)
        async with aiosqlite.connect(database_path(db_name)) as db:
            Photo = await convertToBinaryData(photo)
            await db.execute(f"""UPDATE text SET img = (?) WHERE id = {id_text}""",(Photo,))
            await db.commit()



#await db.execute(f"""UPDATE backup_soc SET img = (?) WHERE id = {id_soc}""",(Photo,))
#            await db.commit()

##################################################
##############                   #################
##################################################

async def convertToBinaryData(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        blobData = file.read()
    return blobData

async def insertBLOBsoc(name_soc, photo, db_name=db_name):
    if database_exists(db_name):
        current_soc = list(await get_current_backup_by_time(name_soc))
        id_soc = current_soc[0]
        #print(1)
        async with aiosqlite.connect(database_path(db_name)) as db:
            Photo = await convertToBinaryData(photo)
            await db.execute(f"""UPDATE backup_soc SET img = (?) WHERE id = {id_soc}""",(Photo,))
            await db.commit()




async def init_database(db_name):
    
    if database_exists(db_name):
        return

    async with aiosqlite.connect(database_path(db_name)) as db:
        await db.execute('''CREATE TABLE socials (
            id integer primary key autoincrement not null,
            name_social varchar(200) not null unique,
            is_work integer not null
        )''')
        await db.execute('''CREATE TABLE backup_soc (
            id integer primary key autoincrement not null,
            id_social integer not null,
            invite_text varchar(400),
            url varchar(200) ,
            img blob,
            time_edit timestamp not null
        )''')
        await db.execute('''CREATE TABLE text (
            id integer primary key autoincrement not null,
            text varchar(1023),
            name varchar(200) ,
            img blob,
            time_edit timestamp not null
        )''')
        await db.execute('''CREATE TABLE metrics (
            id integer primary key autoincrement not null,
            tvl varchar(510),
            total_volume varchar(510) ,
            transactions varchar(510),
            max_transactions_volume varchar(510),
            wallets_count varchar(510)
        )''')
        await db.execute('''CREATE TABLE users (
            id integer primary key autoincrement not null,
            tg_id integer not null unique,
            name varchar(510),
            username varchar(510),
            is_admin integer ,
            chat_count_mess integer DEFAULT 0,
            reputation real default 0
        )''')
        await db.execute('''CREATE TABLE wait_content (
                tg_id integer not null,
                for varchar(200) not null
            )''')
        await db.execute(f'''INSERT INTO socials VALUES
            (1, 'Twitter', 1 ),
            (2, 'Discord', 1 ),
            (3, 'Reddit', 1 ),
            (4, 'Github', 1 ),
            (5, 'Medium', 1 )
        ''')
        await db.commit()

def get_database_connection(user_id):
    return aiosqlite.connect(database_path(user_id))

if __name__ == "__main__":
    #asyncio.run(init_database(db_name))
    #asyncio.run(make_admin(196887301))
    #asyncio.run(insertBLOBsoc("Twitter", "test_23_22_21.jpg"))
    #print(asyncio.run(get_all_texts()))
    #blob_data = asyncio.run(get_current_text_by_name("warning"))[3]
    #convert_data(blob_data, "image.jpg")
    #asyncio.run(add_user(db_name, tg_id=670354986, is_admin = 1))
    #print(asyncio.run(get_soc_info_by_name(name="Twitter")))
    #asyncio.run(add_first_backup_soc_by_name_soc("Twitter"))
    #asyncio.run(add_wait_content_from(2534767278,"img soc Discord"))
    #asyncio.run(delete_wait_content_from(2534767278))
    #asyncio.run(get_all_current_backup_by_time_pretty())
    #print(asyncio.run(get_current_text_by_name("warning"))[1])
    #print(asyncio.run(get_soc_name_by_id(3)))
    #print(asyncio.run(get_current_backup_by_time("Github")))
    #print(asyncio.run(get_current_text_by_name("join_soc")))
    #asyncio.run(add_text_by_name("warning","⚠️ Warning: this service is not responsible for your transactions and possible fraud - be careful!"))
    #print(asyncio.run(get_all_users()))
    #asyncio.run(edit_backup_soc_by_atr(name_soc="Twitter",atr="invite_text", value="Заходите к нам в Твиттер"))
    #asyncio.run(init_wait_content_from())
    #print(asyncio.run(get_all_soc()))
    #print(asyncio.run(is_admin(tg_id=253476728)))
    #asyncio.run(insertBLOBsoc( "test_23_22_21.jpg" ))
    #asyncio.run(add_soc(db_name,"VK"))
    #asyncio.run(delete_soc_by_name(db_name, "VK"))
    #print(asyncio.run(get_user(253476738)))
    #asyncio.run(count_mess_user(253476728))
    #print(asyncio.run(get_most_active_user()))
    pass
