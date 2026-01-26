from aiogram import Router, F
from aiogram.types import Message, ChatMemberUpdated#, LinkPreviewOptions
from aiogram.filters import Command
#from aiogram.fsm.context import FSMContext
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, JOIN_TRANSITION

from random import choice, randint
from asyncio import sleep
#from datetime import datetime

from media import img_language_switch
from config import BOT
from database import db_create_user, db_create_chat, db_read
from app.data import text_emoji
from app.utils import check_ban, check_prefix_and_args, get_language, get_prefix, switch_language
from app.keyboards import kb_start, kb_bot_added_in_chat, kb_settings_chat, kb_my_chats
from app.localization import phrases


RT = Router()



@RT.message(Command('start'))
async def cmd_start(message: Message) -> None:
    user_id = message.from_user.id

    if message.chat.type != "private":
        return

    user_is_in_db = await db_read(
        arr=user_id,
        sql_from='user',
        user_is_in_db=True
    )

    if user_is_in_db:
        l = await get_language(user_id, True)
    else:
        await db_create_user(message.from_user)
        l = 'en'

    if await check_ban(user_id, True) == True:
        return await message.reply(phrases[f'youAreBanned_{l}'])

    # Output
    text = (
        f"{text_emoji} <b>{phrases[f'botFullName_{l}']}</b>\n\n"
        f"{phrases[f'asAdminYouCanList_{l}']}\n\n"
        f"{phrases[f'asUserYouCanList_{l}']}\n\n"
        f"🌠 <b>{phrases[f'justTryIt_{l}']}!</b>"
    )
    await message.answer(
        text=text,
        reply_markup=await kb_start(l)
    )


@RT.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=JOIN_TRANSITION))
async def on_bot_added_in_chat(event: ChatMemberUpdated) -> None:
    chat = event.chat
    chat_id = chat.id
    await db_create_chat(chat)
    l = await get_language(chat_id, False)
    p = await get_prefix(chat_id)

    # Output
    text_greeting = choice((phrases[f'greeting1_{l}'], phrases[f'greeting2_{l}'], phrases[f'greeting3_{l}']))
    text = (
        f"{text_emoji} <b>{text_greeting}!</b> {phrases[f'Im_{l}']} — {phrases[f'botFullName_{l}']}.\n"
        f"{phrases[f'enterHelp_{l}']} <code>{p}{phrases[f'help_{l}']}</code>."
    )
    await event.answer(
        text=text,
        reply_markup=await kb_bot_added_in_chat(l)
    )


@RT.message(F.text == 'help')
@RT.message(F.text == 'помощь')
async def cmd_help(message: Message) -> None:
    pass

@RT.message(F.text.contains('settings'))
@RT.message(F.text.contains('настройки'))
async def cmd_settings(message: Message) -> None:
    user_id = message.from_user.id

    if await check_ban(user_id, True):
        return await message.reply(phrases['youAreBanned_en'])

    chat = message.chat
    reply_markup = ""

    match chat.type:
        case 'private':
            return # Temporary
            #l = await get_language(user_id, True)
            #reply_markup = None
        case 'group' | 'supergroup':
            chat_id = chat.id
            l = await get_language(chat_id, False)
            reply_markup = await kb_settings_chat(l, chat_id)

            if not await check_prefix_and_args(message, phrases[f'settings_{l}']):
                return

    text = f"⚙️ <b>{phrases[f'settings_{l}'].title()}</b>"

    # Output
    await message.reply(
        text=text,
        reply_markup=reply_markup
    )


@RT.message(F.text == 'my chats')
@RT.message(F.text == 'мои чаты')
async def cmd_my_chats(message: Message) -> None:
    if message.chat.type != "private":
        return

    await message.answer(
        text=message.from_user.full_name,
        reply_markup=await kb_my_chats(message.from_user.id)
    )


@RT.message(Command('switch_language'))
async def cmd_switch_language(message: Message) -> None:
    user_id = message.from_user.id

    if await check_ban(user_id, True):
        return await message.reply(phrases['youAreBanned_en'])

    await switch_language(user_id, True)
    l = await get_language(user_id, True)

    # Output
    text = f"{phrases[f'languageSwitched_{l}']} <b>{phrases[f'languageCode_{l}']}</b>."
    chance = randint(0, 100)

    if chance == 0: 
        # Easter egg
        bot_msg = await message.answer_photo(
            caption=text,
            photo=img_language_switch
        )
    else:
        bot_msg = await message.answer(text)

    await message.delete()
    await sleep(5)
    await BOT.delete_message(
        chat_id=message.from_user.id,
        message_id=bot_msg.message_id
    )

@RT.message(Command('developer_info'))
async def cmd_developer_info(message: Message) -> None:
    l = await get_language(message.from_user.id, True)

    await message.answer(f"{phrases[f'mainDeveloper_{l}']}: @ibrvtk")