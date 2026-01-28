from aiogram import Router, F
from aiogram.types import Message, ChatMemberUpdated#, LinkPreviewOptions
from aiogram.filters import Command
#from aiogram.fsm.context import FSMContext
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, JOIN_TRANSITION, LEAVE_TRANSITION

from random import choice, randint
from asyncio import sleep
#from datetime import datetime

from media import img_language_switch
from config import BOT
from database import db_create_user, db_create_chat, db_read, db_create_user_in_chat
from app.utils import check_ban, check_prefix_and_args, get_language, get_prefix, switch_language, delete_chat
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
        l = await get_language(user_id)
    else:
        await db_create_user(message.from_user)
        l = 'en'

    if await check_ban(user_id) == True:
        return await message.reply(phrases[f'youAreBanned_{l}'])

    # Output
    text_emoji = choice(('🟨', '🟡', '💛', '🟧', '🟠', '🧡', '🔶'))
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


@RT.chat_member(ChatMemberUpdatedFilter(JOIN_TRANSITION))
async def on_join_transition(event: ChatMemberUpdated) -> None:
    await db_create_user_in_chat(event.chat.id, event.from_user.id)

@RT.my_chat_member(ChatMemberUpdatedFilter(JOIN_TRANSITION))
async def on_my_join_transition(event: ChatMemberUpdated) -> None:
    chat = event.chat
    chat_id = chat.id
    await db_create_chat(chat)
    l = await get_language(chat_id)
    p = await get_prefix(chat_id)

    # Output
    text_emoji = choice(('🟨', '🟡', '💛', '🟧', '🟠', '🧡', '🔶'))
    text_greeting = choice((phrases[f'greeting1_{l}'], phrases[f'greeting2_{l}'], phrases[f'greeting3_{l}']))
    text = (
        f"{text_emoji} <b>{text_greeting}!</b> {phrases[f'Im_{l}']} — {phrases[f'botFullName_{l}']}.\n"
        f"{phrases[f'enterHelp_{l}']} <code>{p}{phrases[f'help_{l}']}</code>."
    )
    await event.answer(
        text=text,
        reply_markup=await kb_bot_added_in_chat(l)
    )

@RT.my_chat_member(ChatMemberUpdatedFilter(LEAVE_TRANSITION))
async def on_my_leave_transition(event: ChatMemberUpdated) -> None:
    await delete_chat(event.chat)


@RT.message(F.text.contains('help'))
@RT.message(F.text.contains('помощь'))
async def cmd_help(message: Message) -> None:
    if message.chat.type == 'private':
        return

    chat_id = message.chat.id
    l = await get_language(chat_id)

    if not await check_prefix_and_args(message, phrases[f'help_{l}']):
        return

    p = await get_prefix(chat_id)

    # Output
    text_emoji = choice(('🟨', '🟡', '💛', '🟧', '🟠', '🧡', '🔶'))
    text = (
        f"{text_emoji} <b>{phrases[f'briefReference_{l}']}</b>\n\n"
        f"⦁ <code>{p}{phrases[f'help_{l}']}</code> — {phrases[f'helpText_{l}']};\n"
        f"⦁ <code>{p}{phrases[f'settings_{l}']}</code> — {phrases[f'settingsText_{l}']}."
    )
    await message.answer(text)

@RT.message(F.text.contains('settings'))
@RT.message(F.text.contains('настройки'))
async def cmd_settings(message: Message) -> None:
    user_id = message.from_user.id

    if await check_ban(user_id):
        return await message.reply(phrases['youAreBanned_en'])

    chat = message.chat
    reply_markup = ""

    match chat.type:
        case 'private':
            return # Temporary
            #l = await get_language(user_id)
            #reply_markup = None
        case 'group' | 'supergroup':
            chat_id = chat.id
            l = await get_language(chat_id)
            reply_markup = await kb_settings_chat(chat_id)

            if not await check_prefix_and_args(message, phrases[f'settings_{l}']):
                return

    text = f"⚙️ <b>{phrases[f'settings_{l}'].title()}</b>\n{phrases[f'ifYouKickBot_{l}']}"

    # Output
    await message.reply(
        text=text,
        reply_markup=reply_markup
    )


@RT.message(F.text.contains('profile'))
@RT.message(F.text.contains('профиль'))
async def cmd_profile(message: Message) -> None:
    user = message.from_user
    user_id = user.id

    if await check_ban(user_id):
        return await message.reply(phrases['youAreBanned_en'])

    chat_id = message.chat.id
    l = await get_language(chat_id)

    if not await check_prefix_and_args(message, phrases[f'profile_{l}'], 2):
        return

    user_user_data = await db_read(
        arr=user_id,
        sql_from='user',
        sql_select='username, emoji, language_code, is_banned, is_pro'
    )
    bot = await BOT.get_me()
    user_username = user_user_data[0] if user_user_data[0] else bot.username
    user_emoji = user_user_data[1]
    u_l = user_user_data[2]
    user_is_banned = user_user_data[3]
    user_is_pro = user_user_data[4]
    user_is_banned =  "💀 " if user_is_banned == 1 else ""
    user_is_pro = "🎖️ " if user_is_pro == 1 else ""

    user_is_in_db = await db_read(
        arr=user_id,
        sql_from='stat',
        user_is_in_db=True
    )

    if not user_is_in_db:
        await db_create_user_in_chat(chat_id, user_id)

    user_stat_data = await db_read(
        arr=user_id,
        sql_from='stat',
        sql_where='user_id',
        sql_select='admin_level, balance, bonus, wins, loses, balance_without_loses, last_play'
    )
    admin_level = user_stat_data[0]
    balance = user_stat_data[1]
    bonus = user_stat_data[2]
    wins = user_stat_data[3]
    loses = user_stat_data[4]
    balance_without_loses = user_stat_data[5]
    last_play = user_stat_data[6]

    # Output
    user_title = f"{user_emoji} {user_is_pro}{user_is_banned}<b><a href='https://t.me/{user_username}'>{user.full_name}</a></b> {phrases[f'emojiFlag_{u_l}']} ⦁ 💵{balance}"
    text = (
        f"{user_title}\n{admin_level} {phrases[f'adminLevel_{l}']}\n\n"
        f"<b>{phrases[f'wins_{l}']}:</b> {wins} ⦁ <b>{phrases[f'loses_{l}']}:</b> {loses}\n"
        f"<i>{phrases[f'balanceWithoutLoses_{l}']} 💵{balance_without_loses}</i>\n\n"
        f"<b>{phrases[f'activeBonus_{l}']}:</b> {bonus} ⦁ <b>{phrases[f'lastPlay_{l}']}:</b> {last_play}"
    )
    await message.reply(
        text=text,
        disable_web_page_preview=True
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

    if message.chat.type != 'private':
        return

    if await check_ban(user_id):
        return await message.reply(phrases['youAreBanned_en'])

    await switch_language(user_id)
    l = await get_language(user_id)

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
    if message.chat.type != 'private':
        return

    l = await get_language(message.from_user.id)

    await message.answer(f"{phrases[f'mainDeveloper_{l}']}: @ibrvtk")