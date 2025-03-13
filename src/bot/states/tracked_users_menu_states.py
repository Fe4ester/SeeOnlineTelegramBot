from aiogram.fsm.state import State, StatesGroup


class DeleteTrackedUserStates(StatesGroup):
    waiting_for_user_number = State()


class GetDiagramStates(StatesGroup):
    waiting_for_user_number = State()
