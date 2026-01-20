from aiogram.types import (
    #ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.utils.keyboard import InlineKeyboardBuilder#, ReplyKeyboardBuilder

# from database import db_get_language
from app.localization import phrases



async def kb_add_to_chat(l: str) -> InlineKeyboardMarkup:
    '''
    :l: `language_code`
    '''
    switched_l = ""
    match l:
        case 'en':
            switched_l = "ru"
        case 'ru':
            switched_l = "en"

    inline_keyboard = InlineKeyboardBuilder()

    inline_keyboard.add(InlineKeyboardButton(
        text=phrases[f'addToChat_{l}'],
        url='https://t.me/iCasinoSimBot?startgroup'
    ))
    inline_keyboard.add(InlineKeyboardButton(
        text=f"{phrases[f'switchTo_{switched_l}']} {phrases[f'languageCode_{switched_l}']} {phrases[f'language_{switched_l}']}",
        callback_data=f'language_addToChat'
    ))

    return inline_keyboard.adjust(1).as_markup()