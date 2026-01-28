from aiogram.types import Message, Chat

from aiosqlite import connect

from config import BOT, DB_DB
from database import db_create_user, db_read, db_update, db_delete, db_get_all_users



async def check_ban(id: int) -> bool:
    '''
    Reads the DB and returns string of language code param.
    '''
    type_id = 'chat' if str(id).startswith('-100') else 'user'

    user_is_in_db = await db_read(
        arr=id,
        sql_from=type_id,
        user_is_in_db=True
    )

    if not user_is_in_db:
        return False

    is_banned = await db_read(
        arr=id,
        sql_from=type_id,
        sql_select='is_banned'
    )

    is_banned = True if is_banned[0] == 1 else False
    return is_banned

async def check_prefix_and_args(message: Message, command: str, args_needed: int = 1) -> bool | None:
    if args_needed < 1:
        raise ValueError("src/app/utils.py: check_prefix_and_args(): args_needed can not be smaller than zero")

    message_text = message.text
    args = message_text.split(' ')

    if len(args) > args_needed:
        return False

    p = await get_prefix(message.chat.id)

    if args[0] != f"{p}{command}":
        return False

    return True


async def get_language(id: int) -> str:
    '''
    Reads the DB and returns string of language code param.
    '''
    type_id = 'chat' if str(id).startswith('-100') else 'user'

    user_is_in_db = await db_read(
        arr=id,
        sql_from=type_id,
        user_is_in_db=True
    )

    if not user_is_in_db:
        return 'en'

    language_code = await db_read(
        arr=id,
        sql_from=type_id,
        sql_select='language_code'
    )

    language_code = language_code[0]
    return language_code

async def get_prefix(chat_id: int) -> str:
    '''
    Reads the DB and returns string of chat prefix param.
    '''
    chat_prefix = await db_read(
        arr=chat_id,
        sql_from='chat',
        sql_select='prefix'
    )

    if not chat_prefix[0]:
        return ""

    chat_prefix = chat_prefix[0]
    return chat_prefix

async def get_owner_id(chat_id: int) -> int:
    '''
    Returns the Telegram ID of owner of the chat.
    '''
    admins = await BOT.get_chat_administrators(chat_id)

    for admin in admins:
        if admin.status == 'creator':
            owner_id = admin.user.id
            await update_username(owner_id)
            return owner_id


async def update_username(id: int) -> None:
    target = await BOT.get_chat(id)
    type_id = 'chat' if str(id).startswith('-100') else 'user'

    is_in_db = await db_read(
        arr=id,
        sql_from=type_id,
        user_is_in_db=True
    )

    if is_in_db:
        await db_update(
            arr_set=target.username,
            arr_where=id,
            sql_update=type_id,
            sql_set='username'
        )

async def switch_language(id: int, db_dont_write: bool = False) -> str:
    '''
    :param db_dont_write: If `True`, then just don't write switched language in DB
    :type db_dont_write: bool
    '''
    type_id = 'chat' if str(id).startswith('-100') else 'user'

    is_in_db = await db_read(
        arr=id,
        sql_from=type_id,
        user_is_in_db=True
    )

    if not is_in_db:
        if not db_dont_write and type_id != 'chat':
            user = await BOT.get_chat(id)
            await db_create_user(user)
        return 'en'

    old_language_code = await get_language(id)
    new_language_code = ''

    match old_language_code:
        case 'en':
            new_language_code = 'ru'
        case 'ru':
            new_language_code = 'en'

    if not db_dont_write:
        await db_update(
            arr_set=new_language_code,
            arr_where=id,
            sql_update=type_id,
            sql_set='language_code'
        )

    return new_language_code


async def delete_chat(chat: Chat) -> None:
    chat_id = chat.id
    owner_id = await db_read(
        arr=chat_id,
        sql_from='chat',
        sql_select='owner_id'
    )
    owner_id = owner_id[0]

    chat_items = []
    async with connect(DB_DB) as db:
        async with db.execute("SELECT id FROM item WHERE chat_id = ?", (chat_id,)) as cursor:
            rows = await cursor.fetchall()
            chat_items = [str(row[0]) for row in rows]

    if owner_id:
        owner_chats = await db_read(
            arr=owner_id,
            sql_from='user',
            sql_select='chats_id'
        )
        owner_chats = owner_chats[0]

        if owner_chats != None:
            new_owner_chats = ','.join([
                c for c in owner_chats.split(',')
                if int(c) != chat_id
            ])
            await db_update(
                new_owner_chats if new_owner_chats else None,
                owner_id,
                'user',
                'chats_id'
            )

    if chat_items:
        users_id = await db_get_all_users()
        
        for user_id in users_id:
            user_items = await db_read(
                arr=user_id,
                sql_from='user',
                sql_select='items_id'
            )
            user_items = user_items[0]

            if user_items != None:
                items_list = user_items.split(',')
                new_items_list = [item for item in items_list if item not in chat_items]
                
                if len(new_items_list) != len(items_list):
                    new_items_str = ','.join(new_items_list) if new_items_list else None
                    await db_update(
                        arr_set=new_items_str,
                        arr_where=user_id,
                        sql_update='user',
                        sql_set='items_id'
                    )

    await db_delete(
        arr=chat_id,
        sql_from='chat'
    )
    await db_delete(
        arr=chat_id,
        sql_from='stat',
        sql_where='chat_id'
    )
    await db_delete(
        arr=chat_id,
        sql_from='item',
        sql_where='chat_id'
    )
    await db_delete(
        arr=chat_id,
        sql_from='custom_role',
        sql_where='chat_id'
    )