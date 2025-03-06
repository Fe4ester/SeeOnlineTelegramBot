import aiohttp
import urllib.parse
from typing import Any, Dict, Optional, Union, List

from pydantic import BaseModel

from .tracker_service_models import (
    TrackerAccount,
    TrackerSetting,
    TrackedUser,
    OnlineStatus,
    TelegramUser
)


class SeeOnlineAPIError(Exception):
    """Кастомное исключение для ловли ошибок внешнего сервиса"""

    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        super().__init__(f"[{status_code}] {message}")


class SeeOnlineAPI:
    """
    Клиент для взаимодействия с "Tracker API", c поддержкой контекстного менеджера
    и валидацией ответов через Pydantic.
    """

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self) -> "SeeOnlineAPI":
        self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.close()

    async def _request(
            self,
            method: str,
            endpoint: str,
            pk: Optional[Union[int, str]] = None,
            query_params: Optional[Dict[str, Any]] = None,
            data: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Универсальный метод для отправки запросов.
        Собирает итоговый URL, шлёт запрос и обрабатывает ответ.
        Поднимает SeeOnlineAPIError, если что-то пошло не так.
        """
        if not self._session:
            raise RuntimeError("ClientSession is not initialized. Use 'async with SeeOnlineAPI(...)'")

        url = self._build_url(endpoint, pk, query_params)
        async with self._session.request(method=method.upper(), url=url, json=data) as response:
            return await self._handle_response(response)

    async def _handle_response(self, response: aiohttp.ClientResponse) -> Any:
        """
        Если статус-код в диапазоне 2xx:
          - Если 204 No Content, возвращаем None
          - Иначе пробуем .json()
            * если не получается (пустой ответ) -> возвращаем None
        Иначе поднимаем исключение SeeOnlineAPIError.
        """
        if 200 <= response.status < 300:
            # 204 - "No Content", нечего парсить
            if response.status == 204:
                return None
            try:
                return await response.json()
            except aiohttp.ContentTypeError:
                # Иногда приходит пустое тело с 200 OK и Content-Type не JSON
                text = await response.text()
                if not text.strip():
                    return None
                raise SeeOnlineAPIError(
                    response.status,
                    f"Ответ не в формате JSON. Тело ответа: {text}"
                )
        else:
            text = await response.text()
            raise SeeOnlineAPIError(
                response.status,
                f"Запрос не удался. Тело ответа: {text}"
            )

    def _build_url(
            self,
            endpoint: str,
            pk: Optional[Union[int, str]] = None,
            query_params: Optional[Dict[str, Any]] = None
    ) -> str:
        url = f"{self.base_url}/{endpoint}/"
        if pk is not None:
            url += f"{pk}/"
        if query_params:
            filtered_params = {k: v for k, v in query_params.items() if v is not None}
            if filtered_params:
                url += "?" + urllib.parse.urlencode(filtered_params)
        return url

    # ----------------------------------------------------------------
    # Вспомогательный метод для валидации (Pydantic, V2)
    # ----------------------------------------------------------------
    def _parse_as(
            self,
            raw_json: Any,
            schema_class: BaseModel,
            many: bool = False
    ) -> Union[BaseModel, List[BaseModel], None]:
        """
        Преобразует raw_json в модель (или список моделей) с помощью Pydantic.
        :param schema_class: Класс Pydantic, например TrackerAccount.
        :param many: True, если ожидаем список объектов.
        :return: Объект модели, список объектов или None
        """
        if raw_json is None:
            # Если тело ответа пустое, а мы ждём объекты, вернём None или пустой список
            return [] if many else None

        if many:
            if not isinstance(raw_json, list):
                raise TypeError(f"Ожидался список, но пришёл: {type(raw_json)}")
            return [schema_class.model_validate(obj) for obj in raw_json]

        # Ситуация, когда API вернул массив в ответ, а мы ожидаем один объект.
        # Можно взять первый объект или бросить ошибку — зависит от ваших бизнес-требований.
        if isinstance(raw_json, list):
            if not raw_json:
                # Пустой массив
                return None
            return schema_class.model_validate(raw_json[0])

        return schema_class.model_validate(raw_json)

    # ----------------------------
    # TrackerAccount
    # ----------------------------

    async def get_tracker_account(
            self,
            pk: Optional[int] = None,
            telegram_id: Optional[int] = None,
            is_active: Optional[bool] = None,
            is_auth: Optional[bool] = None
    ) -> Union[TrackerAccount, List[TrackerAccount], None]:
        query_params = {}
        if telegram_id is not None:
            query_params["telegram_id"] = telegram_id
        if is_active is not None:
            query_params["is_active"] = str(is_active).lower()
        if is_auth is not None:
            query_params["is_auth"] = str(is_auth).lower()

        raw = await self._request("GET", "tracker-accounts", pk=pk, query_params=query_params)
        if pk is not None:
            return self._parse_as(raw, TrackerAccount, many=False)
        else:
            return self._parse_as(raw, TrackerAccount, many=True)

    async def create_tracker_account(self, data: Dict[str, Any]) -> TrackerAccount:
        raw = await self._request("POST", "tracker-accounts", data=data)
        return self._parse_as(raw, TrackerAccount, many=False)  # type: ignore

    async def update_tracker_account(self, data: Dict[str, Any], pk: int) -> TrackerAccount:
        raw = await self._request("PATCH", "tracker-accounts", pk=pk, data=data)
        return self._parse_as(raw, TrackerAccount, many=False)  # type: ignore

    async def delete_tracker_account(self, pk: int) -> None:
        # 204 No Content -> вернётся None
        await self._request("DELETE", "tracker-accounts", pk=pk)

    async def update_tracker_account_by_telegram_id(self, tg_id: int, data: Dict[str, Any]) -> TrackerAccount:
        endpoint = f"tracker-accounts/by-telegram-id/{tg_id}"
        raw = await self._request("PATCH", endpoint, data=data)
        return self._parse_as(raw, TrackerAccount, many=False)  # type: ignore

    async def delete_tracker_account_by_telegram_id(self, tg_id: int) -> None:
        endpoint = f"tracker-accounts/by-telegram-id/{tg_id}"
        await self._request("DELETE", endpoint)

    # ----------------------------
    # TrackerSetting
    # ----------------------------

    async def get_tracker_setting(
            self,
            pk: Optional[int] = None,
            phone_number: Optional[str] = None,
            tracker_telegram_id: Optional[int] = None
    ) -> Union[TrackerSetting, List[TrackerSetting], None]:
        query_params = {}
        if phone_number is not None:
            query_params["phone_number"] = phone_number
        if tracker_telegram_id is not None:
            query_params["tracker_account__telegram_id"] = tracker_telegram_id

        raw = await self._request("GET", "tracker-settings", pk=pk, query_params=query_params)
        if pk is not None:
            return self._parse_as(raw, TrackerSetting, many=False)
        else:
            return self._parse_as(raw, TrackerSetting, many=True)

    async def create_tracker_setting(self, data: Dict[str, Any]) -> TrackerSetting:
        raw = await self._request("POST", "tracker-settings", data=data)
        return self._parse_as(raw, TrackerSetting, many=False)  # type: ignore

    async def update_tracker_setting(self, data: Dict[str, Any], pk: int) -> TrackerSetting:
        raw = await self._request("PATCH", "tracker-settings", pk=pk, data=data)
        return self._parse_as(raw, TrackerSetting, many=False)  # type: ignore

    async def delete_tracker_setting(self, pk: int) -> None:
        await self._request("DELETE", "tracker-settings", pk=pk)

    async def update_tracker_setting_by_phone_number(self, phone: str, data: Dict[str, Any]) -> TrackerSetting:
        endpoint = f"tracker-settings/by-phone-number/{phone}"
        raw = await self._request("PATCH", endpoint, data=data)
        return self._parse_as(raw, TrackerSetting, many=False)  # type: ignore

    async def delete_tracker_setting_by_phone_number(self, phone: str) -> None:
        endpoint = f"tracker-settings/by-phone-number/{phone}"
        await self._request("DELETE", endpoint)

    async def update_tracker_setting_by_tracker_telegram_id(self, tg_id: int, data: Dict[str, Any]) -> TrackerSetting:
        endpoint = f"tracker-settings/by-tracker-telegram-id/{tg_id}"
        raw = await self._request("PATCH", endpoint, data=data)
        return self._parse_as(raw, TrackerSetting, many=False)  # type: ignore

    async def delete_tracker_setting_by_tracker_telegram_id(self, tg_id: int) -> None:
        endpoint = f"tracker-settings/by-tracker-telegram-id/{tg_id}"
        await self._request("DELETE", endpoint)

    # ----------------------------
    # TelegramUser
    # ----------------------------

    async def get_telegram_user(
            self,
            pk: Optional[int] = None,
            telegram_id: Optional[int] = None,
            role: Optional[str] = None
    ) -> Union[TelegramUser, List[TelegramUser], None]:
        query_params = {}
        if telegram_id is not None:
            query_params["telegram_id"] = telegram_id
        if role is not None:
            query_params["role"] = role

        raw = await self._request("GET", "telegram-users", pk=pk, query_params=query_params)
        if pk is not None:
            return self._parse_as(raw, TelegramUser, many=False)
        else:
            return self._parse_as(raw, TelegramUser, many=True)

    async def create_telegram_user(self, data: Dict[str, Any]) -> TelegramUser:
        raw = await self._request("POST", "telegram-users", data=data)
        return self._parse_as(raw, TelegramUser, many=False)  # type: ignore

    async def update_telegram_user(self, data: Dict[str, Any], pk: int) -> TelegramUser:
        raw = await self._request("PATCH", "telegram-users", pk=pk, data=data)
        return self._parse_as(raw, TelegramUser, many=False)  # type: ignore

    async def delete_telegram_user(self, pk: int) -> None:
        await self._request("DELETE", "telegram-users", pk=pk)

    async def update_telegram_user_by_telegram_id(self, tg_id: int, data: Dict[str, Any]) -> TelegramUser:
        endpoint = f"telegram-users/by-telegram-id/{tg_id}"
        raw = await self._request("PATCH", endpoint, data=data)
        return self._parse_as(raw, TelegramUser, many=False)  # type: ignore

    async def delete_telegram_user_by_telegram_id(self, tg_id: int) -> None:
        endpoint = f"telegram-users/by-telegram-id/{tg_id}"
        await self._request("DELETE", endpoint)

    async def update_telegram_user_by_role(self, role: str, data: Dict[str, Any]) -> List[TelegramUser]:
        endpoint = f"telegram-users/by-role/{role}"
        raw = await self._request("PATCH", endpoint, data=data)
        # Предположим, возвращается список
        parsed = self._parse_as(raw, TelegramUser, many=True)
        return parsed if parsed else []

    async def delete_telegram_user_by_role(self, role: str) -> None:
        endpoint = f"telegram-users/by-role/{role}"
        await self._request("DELETE", endpoint)

    # ----------------------------
    # TrackedUser
    # ----------------------------

    async def get_tracked_user(
            self,
            pk: Optional[int] = None,
            username: Optional[str] = None,
            visible_online: Optional[bool] = None,
            tracker_telegram_id: Optional[int] = None,
            telegram_user_id: Optional[int] = None
    ) -> Union[TrackedUser, List[TrackedUser], None]:
        query_params = {}
        if username is not None:
            query_params["username"] = username
        if visible_online is not None:
            query_params["visible_online"] = str(visible_online).lower()
        if tracker_telegram_id is not None:
            query_params["tracker_account__telegram_id"] = tracker_telegram_id
        if telegram_user_id is not None:
            query_params["telegram_user__telegram_id"] = telegram_user_id

        raw = await self._request("GET", "tracked-users", pk=pk, query_params=query_params)
        if pk is not None:
            return self._parse_as(raw, TrackedUser, many=False)
        else:
            return self._parse_as(raw, TrackedUser, many=True)

    async def create_tracked_user(self, data: Dict[str, Any]) -> TrackedUser:
        raw = await self._request("POST", "tracked-users", data=data)
        return self._parse_as(raw, TrackedUser, many=False)  # type: ignore

    async def update_tracked_user(self, data: Dict[str, Any], pk: int) -> TrackedUser:
        raw = await self._request("PATCH", "tracked-users", pk=pk, data=data)
        return self._parse_as(raw, TrackedUser, many=False)  # type: ignore

    async def delete_tracked_user(self, pk: int) -> None:
        await self._request("DELETE", "tracked-users", pk=pk)

    async def update_tracked_user_by_username(self, uname: str, data: Dict[str, Any]) -> TrackedUser:
        endpoint = f"tracked-users/by-username/{uname}"
        raw = await self._request("PATCH", endpoint, data=data)
        return self._parse_as(raw, TrackedUser, many=False)  # type: ignore

    async def delete_tracked_user_by_username(self, uname: str) -> None:
        endpoint = f"tracked-users/by-username/{uname}"
        await self._request("DELETE", endpoint)

    # ----------------------------
    # OnlineStatus
    # ----------------------------

    async def get_online_status(
            self,
            pk: Optional[int] = None,
            username: Optional[str] = None,
            is_online: Optional[bool] = None
    ) -> Union[OnlineStatus, List[OnlineStatus], None]:
        query_params = {}
        if username is not None:
            query_params["username"] = username
        if is_online is not None:
            query_params["is_online"] = str(is_online).lower()

        raw = await self._request("GET", "online-statuses", pk=pk, query_params=query_params)
        if pk is not None:
            return self._parse_as(raw, OnlineStatus, many=False)
        else:
            return self._parse_as(raw, OnlineStatus, many=True)

    async def create_online_status(self, data: Dict[str, Any]) -> OnlineStatus:
        raw = await self._request("POST", "online-statuses", data=data)
        return self._parse_as(raw, OnlineStatus, many=False)  # type: ignore

    async def update_online_status(self, data: Dict[str, Any], pk: int) -> OnlineStatus:
        raw = await self._request("PATCH", "online-statuses", pk=pk, data=data)
        return self._parse_as(raw, OnlineStatus, many=False)  # type: ignore

    async def delete_online_status(self, pk: int) -> None:
        await self._request("DELETE", "online-statuses", pk=pk)

    async def delete_online_statuses_by_tracked_user_id(self, tuid: int) -> None:
        endpoint = f"online-statuses/by-tracked-user-id/{tuid}"
        await self._request("DELETE", endpoint)

    async def delete_online_statuses_by_tracked_username(self, uname: str) -> None:
        endpoint = f"online-statuses/by-tracked-username/{uname}"
        await self._request("DELETE", endpoint)
