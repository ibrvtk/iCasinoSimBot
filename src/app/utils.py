from aiogram.types import Message

from config import BOT
from database import db_create_user, db_read, db_update



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