from aiogram import Router, F
from aiogram.types import CallbackQuery
# from aiogram.fsm.context import FSMContext

from random import choice

from database import db_get_language
from app.utils import switch_language
from app.keyboards import kb_add_to_chat
from app.localization import phrases


RT = Router()



@RT.callback_query(F.data.startswith('language'))
async def cb_language(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id

    await switch_language(user_id)

    special_data = callback.data.split('_')[1]
    l = await db_get_language(user_id)
    emoji = ""
    text = ""

    match special_data:
        case 'addToChat':
            emoji = choice(('🟨', '🟡', '💛', '🟧', '🟠', '🧡', '🔶'))
            text = (
                f"{emoji} <b>{phrases[f'botFullName_{l}']}</b>\n\n"
                f"{phrases[f'asAdminYouCanList_{l}']}\n\n"
                f"{phrases[f'asUserYouCanList_{l}']}\n\n"
                f"🌠 <b>{phrases[f'justTryIt_{l}']}!</b>"
            )

    # Output (answer)
    await callback.message.edit_text(
        text=text,
        reply_markup=await kb_add_to_chat(l)
    )