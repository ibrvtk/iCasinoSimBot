from aiogram.types import (
    #ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.utils.keyboard import InlineKeyboardBuilder#, ReplyKeyboardBuilder

#from database import db_read
#from app.utils import get_language
from app.localization import phrases



async def button_switch_language(inline_keyboard: InlineKeyboardBuilder, l: str, callback_data_suffix: str) -> InlineKeyboardButton:
    '''
    :param l: `language_code`
    :type l: str
    :param callback_data_suffix: Creating the unique callback data 
    :type callback_data_suffix: str
    '''
    switched_l = ""
    match l:
        case 'en':
            switched_l = "ru"
        case 'ru':
            switched_l = "en"

    return inline_keyboard.add(InlineKeyboardButton(
        text=f"{phrases[f'switchTo_{switched_l}']} {phrases[f'languageCode_{switched_l}']} {phrases[f'language_{switched_l}']}",
        callback_data=f'language_{callback_data_suffix}'
    ))


async def kb_start(l: str) -> InlineKeyboardMarkup:
    '''
    :param l: `language_code`
    :type l: str
    '''
    inline_keyboard = InlineKeyboardBuilder()

    inline_keyboard.add(InlineKeyboardButton(
        text=phrases[f'addToChat_{l}'],
        url='https://t.me/iCasinoSimBot?startgroup'
    ))
    await button_switch_language(inline_keyboard, l, 'start')

    return inline_keyboard.adjust(1).as_markup()

async def kb_bot_added_in_chat(l: str) -> InlineKeyboardMarkup:
    '''
    :param l: `language_code`
    :type l: str
    '''
    inline_keyboard = InlineKeyboardBuilder()
    await button_switch_language(inline_keyboard, l, 'chat')
    return inline_keyboard.as_markup()


# async def kb_my_chats(user_id: int) -> InlineKeyboardMarkup:
#     l = await db_get_language(user_id)
#     raw_data = await db_read(
#         arr=user_id,
#         sql_from='user',
#         sql_select='chats_id'
#     )

#     if not raw_data[0]:
#         return

#     inline_keyboard = InlineKeyboardBuilder()
#     raw_chats_id = raw_data[0].split(',')
#     for chat_id in raw_chats_id:
#         try:
#             chat = await BOT.get_chat(int(chat_id))
#             text_chat = f"{chat.title} (@{chat.username})" if chat.username else chat.title
#             inline_keyboard.add(InlineKeyboardButton(
#                 text=text_chat,
#                 callback_game=f'settings_{chat_id}'
#             ))
#         except:
#             pass

#     return inline_keyboard.adjust(2).as_markup()