from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from emoji import is_emoji
from random import choice

from config import BOT
from database import db_read, db_update
from app.data import ChatSettings
from app.utils import get_language, get_prefix, switch_language
from app.keyboards import kb_start, kb_bot_added_in_chat, kb_settings_chat
from app.localization import phrases


RT = Router()



@RT.callback_query(F.data.startswith('language'))
async def cb_language(callback: CallbackQuery) -> None:
    special_data = callback.data.split('_')[1]
    l = ''
    text = ""
    reply_markup = ""

    match special_data:
        case 'start':
            user_id = callback.from_user.id
            await switch_language(user_id)
            l = await get_language(user_id)
            text_emoji = choice(('🟨', '🟡', '💛', '🟧', '🟠', '🧡', '🔶'))
            text = (
                f"{text_emoji} <b>{phrases[f'botFullName_{l}']}</b>\n\n"
                f"{phrases[f'asAdminYouCanList_{l}']}\n\n"
                f"{phrases[f'asUserYouCanList_{l}']}\n\n"
                f"🌠 <b>{phrases[f'justTryIt_{l}']}!</b>"
            )
            reply_markup = await kb_start(l)

        case 'chat':
            chat_id = callback.message.chat.id
            await switch_language(chat_id)
            l = await get_language(chat_id)
            p = await get_prefix(chat_id)
            text_emoji = choice(('🟨', '🟡', '💛', '🟧', '🟠', '🧡', '🔶'))
            text_greeting = choice((phrases[f'greeting1_{l}'], phrases[f'greeting2_{l}'], phrases[f'greeting3_{l}']))
            text = (
                f"{text_emoji} <b>{text_greeting}!</b> {phrases[f'Im_{l}']} — {phrases[f'botFullName_{l}']}.\n"
                f"{phrases[f'enterHelp_{l}']} <code>{p}{phrases[f'help_{l}']}</code>."
            )
            reply_markup = await kb_bot_added_in_chat(l)
        case 'settingsChat':
            chat_id = callback.message.chat.id
            await switch_language(chat_id)
            l = await get_language(chat_id)
            text = f"⚙️ <b>{phrases[f'settings_{l}'].title()}</b>\n{phrases[f'ifYouKickBot_{l}']}"
            reply_markup = await kb_settings_chat(chat_id)

    # Output
    await callback.message.edit_text(
        text=text,
        reply_markup=reply_markup
    )


@RT.callback_query(F.data.startswith('settings'))
async def cb_settings(callback: CallbackQuery, state: FSMContext) -> None:
    callback_data = callback.data.split('_')
    chat_id = callback.message.chat.id
    text = ""
    reply_markup = None
    l = await get_language(chat_id)

    match callback_data[1]:
        case 'chat':
            match callback_data[2]:
                case 'emoji':
                    text = phrases[f'fsmChatSettingsEmoji_{l}']
                    await state.set_state(ChatSettings.emoji)
                case 'prefix':
                    text = phrases[f'fsmChatSettingsPrefix_{l}']
                    await state.set_state(ChatSettings.prefix)
                case 'cooldown':
                    text = phrases[f'fsmChatSettingsCooldown_{l}']
                    await state.set_state(ChatSettings.cooldown)
                case 'ban':
                    is_banned = await db_read(
                        arr=chat_id,
                        sql_from='chat',
                        sql_select='is_banned'
                    )
                    is_banned = 1 if is_banned[0] == 0 else 0
                    await db_update(
                        arr_set=is_banned,
                        arr_where=chat_id,
                        sql_update='chat',
                        sql_set='is_banned'
                    )
                    text = f"⚙️ <b>{phrases[f'settings_{l}'].title()}</b>\n{phrases[f'ifYouKickBot_{l}']}"
                    reply_markup=await kb_settings_chat(chat_id)

    # Output
    msg = await callback.message.edit_text(
        text=text,
        reply_markup=reply_markup
    )
    await state.update_data(bot_msg_id=msg.message_id)

@RT.message(ChatSettings.emoji)
async def fsm_emoji(message: Message, state: FSMContext) -> None:
    chat_id = message.chat.id
    message_text = message.text
    data = await state.get_data()
    text = ""
    reply_markup = None
    l = await get_language(chat_id)

    if not is_emoji(message_text):
        return await message.reply(f"<b>{phrases[f'fsmChatSettingsEmojiError_{l}']}</b> {phrases[f'tryAgain_{l}']}.")

    await db_update(
        arr_set=message_text,
        arr_where=chat_id,
        sql_update='chat',
        sql_set='emoji'
    )

    text = f"⚙️ <b>{phrases[f'settings_{l}'].title()}</b>\n{phrases[f'ifYouKickBot_{l}']}"
    reply_markup=await kb_settings_chat(chat_id)

    # Output
    await BOT.edit_message_text(
        chat_id=chat_id,
        message_id=data['bot_msg_id'],
        text=text,
        reply_markup=reply_markup
    )

    await state.clear()

@RT.message(ChatSettings.prefix)
async def fsm_emoji(message: Message, state: FSMContext) -> None:
    chat_id = message.chat.id
    message_text = message.text
    data = await state.get_data()
    text = ""
    reply_markup = None
    l = await get_language(chat_id)

    if message_text.casefold() == "reset" or message_text.casefold() == "убрать":
        message_text = ""

    if len(message_text) > 1:
        return await message.reply(f"<b>{phrases[f'fsmChatSettingsPrefixError_{l}']}</b> {phrases[f'tryAgain_{l}']}.")

    if is_emoji(message_text):
        return await message.reply(f"<b>{phrases[f'fsmChatSettingsPrefixEmojiError_{l}']}</b> {phrases[f'tryAgain_{l}']}.")

    await db_update(
        arr_set=message_text,
        arr_where=chat_id,
        sql_update='chat',
        sql_set='prefix'
    )

    text = f"⚙️ <b>{phrases[f'settings_{l}'].title()}</b>\n{phrases[f'ifYouKickBot_{l}']}"
    reply_markup=await kb_settings_chat(chat_id)

    # Output
    await BOT.edit_message_text(
        chat_id=chat_id,
        message_id=data['bot_msg_id'],
        text=text,
        reply_markup=reply_markup
    )

    await state.clear()

@RT.message(ChatSettings.cooldown)
async def fsm_emoji(message: Message, state: FSMContext) -> None:
    chat_id = message.chat.id
    message_text = message.text
    data = await state.get_data()
    text = ""
    reply_markup = None
    l = await get_language(chat_id)

    if not message_text.isdigit():
        return await message.reply(f"<b>{phrases[f'fsmChatSettingsCooldownValueError_{l}']}</b> {phrases[f'tryAgain_{l}']}.")

    message_text = int(message_text)

    if message_text > 60 or message_text < 0:
        return await message.reply(f"<b>{phrases[f'fsmChatSettingsCooldownWrongRangeError_{l}']}</b> {phrases[f'tryAgain_{l}']}.")

    await db_update(
        arr_set=message_text,
        arr_where=chat_id,
        sql_update='chat',
        sql_set='cooldown'
    )

    text = f"⚙️ <b>{phrases[f'settings_{l}'].title()}</b>\n{phrases[f'ifYouKickBot_{l}']}"
    reply_markup=await kb_settings_chat(chat_id)

    # Output
    await BOT.edit_message_text(
        chat_id=chat_id,
        message_id=data['bot_msg_id'],
        text=text,
        reply_markup=reply_markup
    )

    await state.clear()