from aiogram.types import User, Chat

from datetime import datetime
from aiosqlite import connect

from config import BOT, DB_DB, DB_SQL



async def db_create_database() -> None:
    '''
    `/src/databasae/scheme.sql`
    '''
    try:
        async with connect(DB_DB) as db:
            with open(DB_SQL, 'r', encoding='utf-8') as file:
                sql_script = file.read()
            await db.executescript(sql_script)
            await db.commit()

    except Exception as e:
        print(f"error: database: db_create_database(): {e}")


async def db_create_user(user: User) -> None:
    user_id = user.id
    user_username = user.username

    try:
        async with connect(DB_DB) as db:
            await db.execute("INSERT OR IGNORE INTO user (id) VALUES (?)", (user_id,))
            await db.execute("""
                UPDATE user 
                SET registration_date = ?, language_code = ?
                WHERE id = ?
            """, (datetime.now().timestamp(), user.language_code, user_id,))
            await db.commit()

        if user_username != None:
            await db_update(
                arr_set=user_username,
                arr_where=user_id,
                sql_update='user',
                sql_set='username'
            )

    except Exception as e:
        print(f"error: database: db_create_user(): {e}")

async def db_create_chat(chat: Chat) -> None:
    chat_id = chat.id
    chat_username = chat.username
    owner_id = 0

    admins = await BOT.get_chat_administrators(chat_id)
    for admin in admins:
        if admin.status == 'creator':
            owner_id = admin.user.id

    try:
        async with connect(DB_DB) as db:
            await db.execute("INSERT OR IGNORE INTO chat (id) VALUES (?)", (chat_id,))
            await db.commit()

            await db_update(
                arr_set=owner_id,
                arr_where=chat_id,
                sql_update='chat',
                sql_set='owner_id'
            )
            if chat_username != None:
                await db_update(
                    arr_set=chat_username,
                    arr_where=chat_id,
                    sql_update='chat',
                    sql_set='username'
                )

            owner_is_in_db = await db_read(
                arr=owner_id,
                sql_from='user',
                user_is_in_db=True
            )

            if not owner_is_in_db:
                owner = await BOT.get_chat(owner_id)
                await db_create_user(owner)

            owner_chats_id = await db_read(
                arr=owner_id,
                sql_from='user',
                sql_select='chats_id'
            )

            if owner_chats_id == None:
                owner_chats_id = f"{chat_id}"
            else:
                owner_chats_id = f"{owner_chats_id},{chat_id}"

            await db_update(
                arr_set=owner_chats_id,
                arr_where=owner_id,
                sql_update='user',
                sql_set='chats_id'
            )

    except Exception as e:
        print(f"error: database: db_create_chat(): {e}")

async def db_read(arr, sql_from: str, sql_where: str = 'id', sql_select: str = '*', user_is_in_db: bool = False) -> tuple | bool | None:
    '''
    `SELECT {sql_select} FROM {sql_from} WHERE {sql_where} = ?(arr)`
    
    :param arr: Required value of the `sql_where` parameter
    :type arr: Any
    :param sql_from: In which table the operation needs to be performed
    :type sql_from: str
    :param sql_where: Which parameter needs to be read. By default, `id` *(because `PRIMARY KEY`)*
    :type sql_where: str
    :param sql_select: What parameters should be returned? By default, `*` *(will return everything)*
    :type sql_select: str
    :param user_is_in_db: If `True`, it will return the fact that a **user or chat** is in the table *(`True` if he is there. Otherwise `False`)*
    :type user_is_in_db: bool
    '''
    try:
        async with connect(DB_DB) as db:
            if not user_is_in_db:
                async with db.execute(f"SELECT {sql_select} FROM {sql_from} WHERE {sql_where} = ?", (arr,)) as cursor:
                    return await cursor.fetchone()

            else:
                async with db.execute(f"SELECT id FROM {sql_from} WHERE id = ?", (arr,)) as cursor:
                    user_data = await cursor.fetchone()

                    if not user_data:
                        return False
                    else:
                        return True

    except Exception as e:
        print(f"error: database: db_read(): {e}")
        return None

async def db_update(arr_set, arr_where, sql_update: str, sql_set: str, sql_where: str = 'id') -> None:
    '''
    `UPDATE {sql_update} SET {sql_set} = ?(arr_set) WHERE {sql_where} = ?(arr_where)`
    
    :param arr_set: Required value of the `sql_set` parameter
    :type arr_set: Any
    :param arr_where: Required value of the `sql_where` parameter
    :type arr_where: Any
    :param sql_update: In which table the operation needs to be performed
    :type sql_update: str
    :param sql_set: Which parameter needs to be updated
    :type sql_set: str
    :param sql_where: update all those with `sql_where` equal to `arr_where`. By default, `id` *(because `PRIMARY KEY`)*
    :type sql_where: str
    '''
    try:
        async with connect(DB_DB) as db:
            await db.execute(f"UPDATE {sql_update} SET {sql_set} = ? WHERE {sql_where} = ?", (arr_set, arr_where))
            await db.commit()

    except Exception as e:
        print(f"error: database: db_update(): {e}")

async def db_delete(arr, sql_from: str, sql_where: str = 'id') -> None:
    async with connect(DB_DB) as db:
        await db.execute(f"DELETE FROM {sql_from} WHERE {sql_where} = ?", (sql_from, sql_where, arr,))
        await db.commit()


async def db_get_all_users() -> list:
    try:
        async with connect(DB_DB) as db:
            async with db.execute("SELECT id FROM user",) as cursor:
                rows = await cursor.fetchall()
                return [row[0] for row in rows]

    except Exception as e:
        print(f"error: database: db_get_all_users(): {e}")
        return []

async def db_get_language(id: int, user_or_chat: bool) -> str:
    '''
    Reads the DB and returns string of language code param.
    
    :param user_or_chat: If `True` then reads the `user` table. Else reads the `chat` table
    :type user_or_chat: bool
    '''
    type_id = 'user' if user_or_chat else 'chat'

    data = await db_read(
        arr=id,
        sql_from=type_id,
        user_is_in_db=True
    )

    if data:
        try:
            async with connect(DB_DB) as db:
                async with db.execute(f"SELECT language_code FROM {type_id} WHERE id = ?", (id,)) as cursor:
                    raw_data = await cursor.fetchone()
                    language_code = raw_data[0]
                    return language_code

        except Exception as e:
            print(f"error: database: db_get_language(): {e}")
            return None

async def db_set_bonus(user_id: int, bonus_name: str) -> None:
    try:
        async with connect(DB_DB) as db:
            await db.execute("""
                UPDATE stat 
                SET bonus_name = ?
                WHERE user_id = ?
            """, (bonus_name, user_id,))
            await db.commit()

    except Exception as e:
        print(f"error: database: db_set_bonus(): {e}")

async def db_set_stage(user_id: int, stage: int) -> None:
    try:
        async with connect(DB_DB) as db:
            await db.execute("""
                UPDATE user 
                SET stage = ?
                WHERE id = ?
            """, (stage, user_id,))
            await db.commit()

    except Exception as e:
        print(f"error: database: db_set_stage(): {e}")