from typing import Optional
from datetime import datetime

from pydantic import BaseModel


class TrackerAccount(BaseModel):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    telegram_id: int
    api_id: int
    api_hash: str
    is_active: bool = False
    is_auth: bool = False


class TrackerSetting(BaseModel):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    tracker_account_id: int
    phone_number: str
    session_string: Optional[str] = None
    max_users: int = 0
    current_users: int = 0


class TelegramUser(BaseModel):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    telegram_id: int
    role: str = "user"
    current_users: int = 0
    max_users: int = 5


class TrackedUser(BaseModel):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    tracker_account_id: int
    telegram_user_id: int
    username: str
    visible_online: bool = True


class OnlineStatus(BaseModel):
    id: Optional[int]
    created_at: Optional[datetime]

    tracked_user_id: int
    is_online: bool
