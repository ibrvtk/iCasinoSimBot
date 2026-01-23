from config import BOT
from database import db_create_user, db_read, db_update, db_get_language



async def update_username(id: int, user_or_chat: bool) -> None:
    '''
    :param user_or_chat: If `True` then reads the `user` table. Else reads the `chat` table
    :type user_or_chat: bool
    '''
    target = await BOT.get_chat(id)
    type_id = 'user' if user_or_chat else 'chat'

    is_in_db = await db_read(
        arr=target,
        sql_from=type_id,
        user_is_in_db=True
    )

    if is_in_db:
        await db_update(
            arr_set=target.username,
            arr_where=target,
            sql_update=type_id,
            sql_set='username'
        )


async def switch_language(id: int, user_or_chat: bool, db_dont_write: bool = False) -> str:
    '''
    :param user_or_chat: If `True` then reads the `user` table. Else reads the `chat` table
    :type user_or_chat: bool
    :param db_dont_write: If `True`, then just don't write switched language in DB
    :type db_dont_write: bool
    '''
    type_id = 'user' if user_or_chat else 'chat'

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

    old_language_code = await db_get_language(id, user_or_chat)
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

    await update_username(id, user_or_chat)

    return new_language_code


async def get_owner_id(chat_id: int) -> int:
    '''
    Returns the Telegram ID of owner of the chat.
    '''
    admins = await BOT.get_chat_administrators(chat_id)

    for admin in admins:
        if admin.status == 'creator':
            owner_id = admin.user.id
            await update_username(owner_id, True)
            return owner_id