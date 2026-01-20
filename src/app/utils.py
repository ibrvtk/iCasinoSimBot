from config import BOT
from database import db_create_user, db_read, db_update, db_get_language



async def switch_language(user_id: int, db_dont_write: bool = False) -> str | bool:
    '''
    :param db_dont_write: If `True`, then just don't write changes in DB
    :type db_dont_write: bool
    '''
    user_is_in_db = await db_read(
        arr=user_id,
        sql_from='user',
        user_is_in_db=True
    )
    if not user_is_in_db:
        if not db_dont_write:
            user = await BOT.get_chat(user_id)
            await db_create_user(user)
            return 'en'
        return None

    old_language_code = await db_get_language(user_id)
    new_language_code = ''

    match old_language_code:
        case 'en':
            new_language_code = 'ru'
            if not db_dont_write:
                await db_update(
                    arr_set=new_language_code,
                    arr_where=user_id,
                    sql_update='user',
                    sql_set='language_code'
                )
        case 'ru':
            new_language_code = 'en'
            if not db_dont_write:
                await db_update(
                    arr_set=new_language_code,
                    arr_where=user_id,
                    sql_update='user',
                    sql_set='language_code'
                )

    return new_language_code