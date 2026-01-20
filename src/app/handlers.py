from aiogram import Router, F
from aiogram.types import Message#, LinkPreviewOptions
from aiogram.filters import Command
#from aiogram.fsm.context import FSMContext

from random import choice, randint
#from datetime import datetime

from media import img_language_switch
# from config import BOT
from database import db_create_user, db_read, db_get_language
from app.utils import switch_language
from app.keyboards import kb_add_to_chat
from app.localization import phrases


RT = Router()



@RT.message(Command('start'))
async def cmd_start(message: Message):
    user_id = message.from_user.id

    user_is_in_db = await db_read(
        arr=user_id,
        sql_from='user',
        user_is_in_db=True
    )

    if user_is_in_db:
        l = await db_get_language(user_id)
    else:
        await db_create_user(message.from_user)
        l = 'en'

    # Output (answer)
    emoji = choice(('🟨', '🟡', '💛', '🟧', '🟠', '🧡', '🔶'))
    text = (
        f"{emoji} <b>{phrases[f'botFullName_{l}']}</b>\n\n"
        f"{phrases[f'asAdminYouCanList_{l}']}\n\n"
        f"{phrases[f'asUserYouCanList_{l}']}\n\n"
        f"🌠 <b>{phrases[f'justTryIt_{l}']}!</b>"
    )
    await message.answer(
        text=text,
        reply_markup=await kb_add_to_chat(l)
    )


@RT.message(Command('switch_language'))
async def cmd_switch_language(message: Message):
    user_id = message.from_user.id

    await switch_language(user_id)
    l = await db_get_language(user_id)

    # Output (answer)
    text = f"{phrases[f'languageSwitched_{l}']} <b>{phrases[f'languageCode_{l}']}</b>."
    chance = randint(0, 100)

    if chance == 0: 
        # Easter egg
        await message.answer_photo(
            caption=text,
            photo=img_language_switch
        )
    else:
        await message.answer(text)

@RT.message(Command('developer_info'))
async def cmd_developer_info(message: Message):
    l = await db_get_language(message.from_user.id)

    await message.answer(f"{phrases[f'mainDeveloper_{l}']}: @ibrvtk")