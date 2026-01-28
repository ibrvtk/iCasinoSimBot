from aiogram.types import (
    #ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.utils.keyboard import InlineKeyboardBuilder#, ReplyKeyboardBuilder

from config import BOT
from database import db_read
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


async def kb_settings_chat(chat_id: int) -> InlineKeyboardMarkup:
    chat_data = await db_read(
        arr=chat_id,
        sql_from='chat',
        sql_select='emoji, language_code, cooldown, is_banned'
    )

    emoji = chat_data[0]
    l = chat_data[1]
    cooldown = chat_data[2]
    is_banned_text = phrases[f'isBannedFalse_{l}'] if chat_data[3] == 0 else phrases[f'isBannedTrue_{l}']

    inline_keyboard = InlineKeyboardBuilder()

    await button_switch_language(inline_keyboard, l, 'settingsChat')
    inline_keyboard.add(InlineKeyboardButton(
        text=f"{phrases[f'chatEmoji_{l}']}: {emoji}",
        callback_data=f'settings_chat_emoji'
    ))
    inline_keyboard.add(InlineKeyboardButton(
        text=f"{phrases[f'cooldown_{l}']}: {cooldown} {phrases[f'sec_{l}']}",
        callback_data=f'settings_chat_cooldown'
    ))
    inline_keyboard.add(InlineKeyboardButton(
        text=f"{is_banned_text}",
        callback_data=f'settings_chat_ban'
    ))

    return inline_keyboard.adjust(1).as_markup()


async def kb_my_chats(user_id: int) -> InlineKeyboardMarkup:
    chats_id = await db_read(
        arr=user_id,
        sql_from='user',
        sql_select='chats_id'
    )
    chats_id = chats_id[0]

    if not chats_id:
        text_tuple = ('У Вас нет чатов с ботом')
        return text_tuple

    chats_id = tuple(chats_id.split(','))

    inline_keyboard = InlineKeyboardBuilder()
    for cid in chats_id:
        try:
            chat = await BOT.get_chat(int(cid))
            text_chat = f"{chat.title} (@{chat.username})" if chat.username else chat.title
            inline_keyboard.add(InlineKeyboardButton(
                text=text_chat,
                callback_data=f'settings_chat_{cid}'
            ))
        except:
            pass
    return inline_keyboard.adjust(2).as_markup()