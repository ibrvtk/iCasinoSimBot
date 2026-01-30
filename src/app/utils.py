from aiogram.types import Message, Chat

from aiosqlite import connect

from config import BOT, DB_DB
from database import db_read, db_update, db_delete, db_read_users



async def check_ban(id: int) -> bool:
    '''
    Reads the DB and returns string of language code param.
    '''
    sql_from = 'chat' if str(id).startswith('-100') else 'user'

    if not await db_read(id, sql_from, check_exist=True):
        return False

    is_banned = await db_read(
        arg=id,
        sql_from=sql_from,
        sql_select='is_banned'
    )

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
    sql_from = 'chat' if str(id).startswith('-100') else 'user'

    if not await db_read(id, sql_from, check_exist=True):
        return 'en'

    language_code = await db_read(
        arg=id,
        sql_from=sql_from,
        sql_select='language_code'
    )

    return language_code

async def get_prefix(chat_id: int) -> str:
    '''
    Reads the DB and returns string of chat prefix param.
    '''
    chat_prefix = await db_read(
        arg=chat_id,
        sql_from='chat',
        sql_select='prefix'
    )

    if not chat_prefix:
        return ""

    return chat_prefix

async def get_owner_id(chat_id: int) -> int:
    '''
    Returns the Telegram ID of owner of the chat.
    '''
    admins = await BOT.get_chat_administrators(chat_id)
    for admin in admins:
        if admin.status == 'creator':
            owner_id = admin.user.id
            return owner_id


async def switch_language(id: int) -> str:
    '''
    :param db_dont_write: If `True`, then just don't write switched language in DB
    :type db_dont_write: bool
    '''
    sql_from = 'chat' if str(id).startswith('-100') else 'user'

    old_language_code = await get_language(id)
    new_language_code = ''

    match old_language_code:
        case 'en':
            new_language_code = 'ru'
        case 'ru':
            new_language_code = 'en'

    await db_update(
        arg_set=new_language_code,
        arg_where=id,
        sql_update=sql_from,
        sql_set='language_code'
    )

    return new_language_code


async def delete_chat(chat: Chat) -> None:
    # W.I.P.
    chat_id = chat.id
    owner_id = await db_read(
        arg=chat_id,
        sql_from='chat',
        sql_select='owner_id'
    )

    chat_items = []
    async with connect(DB_DB) as db:
        async with db.execute("SELECT id FROM item WHERE chat_id = ?", (chat_id,)) as cursor:
            rows = await cursor.fetchall()
            chat_items = [str(row[0]) for row in rows]

    if owner_id:
        owner_chats = await db_read(
            arg=owner_id,
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
        users_id = await db_read_users()
        
        for user_id in users_id:
            user_items = await db_read(
                arg=user_id,
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
                        arg_set=new_items_str,
                        arg_where=user_id,
                        sql_update='user',
                        sql_set='items_id'
                    )

    await db_delete(
        arg=chat_id,
        sql_from='chat'
    )
    await db_delete(
        arg=chat_id,
        sql_from='stat',
        sql_where='chat_id'
    )
    await db_delete(
        arg=chat_id,
        sql_from='item',
        sql_where='chat_id'
    )
    await db_delete(
        arg=chat_id,
        sql_from='custom_role',
        sql_where='chat_id'
    )