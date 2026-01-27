from aiogram import Router, F
from aiogram.types import CallbackQuery
# from aiogram.fsm.context import FSMContext

from random import choice

from app.data import text_emoji
from app.utils import get_language, get_prefix, switch_language
from app.keyboards import kb_start, kb_bot_added_in_chat
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
            await switch_language(user_id, True)
            l = await get_language(user_id)
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
            text_greeting = choice((phrases[f'greeting1_{l}'], phrases[f'greeting2_{l}'], phrases[f'greeting3_{l}']))
            text = (
                f"{text_emoji} <b>{text_greeting}!</b> {phrases[f'Im_{l}']} — {phrases[f'botFullName_{l}']}.\n"
                f"{phrases[f'enterHelp_{l}']} <code>{p}{phrases[f'help_{l}']}</code>."
            )
            reply_markup = await kb_bot_added_in_chat(l)

    # Output
    await callback.message.edit_text(
        text=text,
        reply_markup=reply_markup
    )