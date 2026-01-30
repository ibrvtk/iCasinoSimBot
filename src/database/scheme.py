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
    '''Creates user in `user` table. Also updates `username` param _(even if the user already exists)_'''
    user_id = user.id
    user_username = user.username

    if not await db_read(user_id, 'user', check_exist=True):
        try:
            async with connect(DB_DB) as db:
                await db.execute("INSERT INTO user (id) VALUES (?)", (user_id,))
                await db.execute("""
                    UPDATE user 
                    SET registration_date = ?
                    WHERE id = ?
                """, (datetime.now().timestamp(), user_id,))
                await db.commit()

        except Exception as e:
            print(f"error: database: db_create_user(): {e}")

    await db_update(
        arg_set=user_username,
        arg_where=user_id,
        sql_update='user',
        sql_set='username'
    )

async def db_create_chat(chat: Chat) -> None:
    chat_id = chat.id

    if not await db_read(chat_id, 'chat', check_exist=True):
        try:
            async with connect(DB_DB) as db:
                await db.execute("INSERT INTO chat (id) VALUES (?)", (chat_id,))
                await db.commit()

        except Exception as e:
            print(f"error: database: db_create_chat(): {e}")

    chat_username = chat.username
    owner_id = 0

    admins = await BOT.get_chat_administrators(chat_id)
    for admin in admins:
        if admin.status == 'creator':
            owner_id = admin.user.id

    # Updating chat owner_id and chat username
    await db_update(
        arg_set=owner_id,
        arg_where=chat_id,
        sql_update='chat',
        sql_set='owner_id'
    )

    await db_update(
        arg_set=chat_username,
        arg_where=chat_id,
        sql_update='chat',
        sql_set='username'
    )

    # Updating owner chats_id. Creating him if not exists
    # TODO: Remove chat_id from past owner's chats_id param, promoting new owner and demoting past
    if not await db_read(owner_id, 'user', check_exist=True):
        owner = await BOT.get_chat(owner_id)
        await db_create_user(owner)

    owner_chats_id = await db_read(
        arg=owner_id,
        sql_from='user',
        sql_select='chats_id'
    )

    if owner_chats_id == None:
        owner_chats_id = f"{chat_id}"
    else:
        owner_chats_id = f"{owner_chats_id},{chat_id}"

    await db_update(
        arg_set=owner_chats_id,
        arg_where=owner_id,
        sql_update='user',
        sql_set='chats_id'
    )

async def db_read(arg, sql_from: str, sql_select: str = '*', sql_where: str = 'id', arg_and = None, sql_and: str = None, check_exist: bool = False) -> tuple | bool | None:
    if sql_select != '*' and sql_where != 'id' and check_exist:
        raise ValueError("src/database: db_read(): check_existence doesn't work with sql_select and sql_where")
    if (arg_and is not None and sql_and is None) or (arg_and is None and sql_and is not None):
        raise ValueError("src/database: db_read(): arg_and and sql_and must both be None or not None")

    sql_and_params = ""
    params = (arg,)

    if arg_and is not None and sql_and is not None:
        sql_and_params = f" AND {sql_and} = ?"
        params = (arg, arg_and)

    try:
        async with connect(DB_DB) as db:
            if not check_exist:
                async with db.execute(f"SELECT {sql_select} FROM {sql_from} WHERE {sql_where} = ?{sql_and_params}", params) as cursor:
                    data = await cursor.fetchone()

                    if sql_select.__contains__(','):
                        return data

                    return data[0] if data else None

            else:
                async with db.execute(f"SELECT id FROM {sql_from} WHERE id = ?{sql_and_params}", params) as cursor:
                    data = await cursor.fetchone()

                    if not data:
                        return False

                    return True

    except Exception as e:
        print(f"error: database: db_read(): {e}")
        return None

async def db_update(arg_set, arg_where, sql_update: str, sql_set: str, sql_where: str = 'id', arg_and = None, sql_and: str = None) -> None:
    if arg_and and not sql_and or not arg_and and sql_and:
        raise ValueError("src/database: db_read(): arg_and and sql_and must both be None or not None")

    sql_and_params = ""
    params = (arg_set, arg_where)

    if arg_and is not None and sql_and is not None:
        sql_and_params = f" AND {sql_and} = ?"
        params = (arg_set, arg_where, arg_and)

    try:
        async with connect(DB_DB) as db:
            await db.execute(f"UPDATE {sql_update} SET {sql_set} = ? WHERE {sql_where} = ?{sql_and_params}", params)
            await db.commit()

    except Exception as e:
        print(f"error: database: db_update(): {e}")

async def db_delete(arg, sql_from: str, sql_where: str = 'id', arg_and = None, sql_and = None) -> None:
    if arg_and and not sql_and or not arg_and and sql_and:
        raise ValueError("src/database: db_read(): arg_and and sql_and must both be None or not None")

    sql_and_params = ""
    params = (arg,)

    if arg_and is not None and sql_and is not None:
        sql_and_params = f" AND {sql_and} = ?"
        params = (arg, arg_and)

    async with connect(DB_DB) as db:
        await db.execute(f"DELETE FROM {sql_from} WHERE {sql_where} = ?{sql_and_params}", params)
        await db.commit()


async def db_create_user_in_chat(chat_id: int, user_id: int) -> None:
    if not await db_read(arg=chat_id, arg_and=user_id, sql_where='chat_id', sql_and='user_id', sql_from='stat', check_exist=True):
        try:
            async with connect(DB_DB) as db:
                await db.execute("INSERT INTO stat (chat_id, user_id) VALUES (?, ?)", (chat_id, user_id,))
                await db.commit()

        except Exception as e:
            print(f"error: database: db_create_user_in_chat(): {e}")
            return

async def db_read_users() -> list | None:
    try:
        async with connect(DB_DB) as db:
            async with db.execute("SELECT id FROM user",) as cursor:
                rows = await cursor.fetchall()
                return [row[0] for row in rows]

    except Exception as e:
        print(f"error: database: db_get_all_users(): {e}")
        return None

async def db_set_bonus(chat_id: int, user_id: int, bonus_name: str) -> None:
    try:
        async with connect(DB_DB) as db:
            await db.execute("""
                UPDATE stat 
                SET bonus_name = ?
                WHERE chat_id = ? AND user_id = ?
            """, (bonus_name, chat_id, user_id,))
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