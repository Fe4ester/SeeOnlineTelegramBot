from aiogram.fsm.state import State, StatesGroup


class AddTrackedUserStates(StatesGroup):
    waiting_for_username = State()
