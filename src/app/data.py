from aiogram.fsm.state import State, StatesGroup



class ChatSettings(StatesGroup):
    emoji = State()
    prefix = State()
    cooldown = State()