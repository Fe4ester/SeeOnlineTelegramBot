import aiohttp
import urllib.parse
from typing import Any, Dict, Optional, Union


class SeeOnlineAPIError(Exception):
    """
    Кастомное исключения для ловли ошибок внешнего сервиса.
    """
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        super().__init__(f"[{status_code}] {message}")


class SeeOnlineAPI:
    def __init__(self, base_url: str) -> None:
        """
        :param base_url: Например, 'https://45.197.17.155/api'
        """
        self.base_url = base_url.rstrip("/")
        self._session = aiohttp.ClientSession()

    async def close(self) -> None:
        """
        Закрытие сессии, для завершения работы с апи.
        """
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
        url = self._build_url(endpoint, pk, query_params)
        async with self._session.request(method=method.upper(), url=url, json=data) as response:
            return await self._handle_response(response)

    async def _handle_response(
            self,
            response: aiohttp.ClientResponse
    ) -> Any:
        """
        Проверяем статус код. Если 2xx — пытаемся вернуть JSON.
        Иначе поднимаем ошибку SeeOnlineAPIError.
        """
        if 200 <= response.status < 300:
            try:
                return await response.json()
            except aiohttp.ContentTypeError:
                text = await response.text()
                raise SeeOnlineAPIError(
                    response.status,
                    f"Ответ не в формате JSON или пустой. Тело ответа: {text}"
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
        """
        Собирает URL. Пример:
            endpoint='monitors' -> {base_url}/monitors/
            pk=123 -> {base_url}/monitors/123/
            query_params={'user_id': 777} -> {base_url}/monitors/123/?user_id=777
        """
        url = f"{self.base_url}/{endpoint}/"
        if pk is not None:
            url += f"{pk}/"
        if query_params:
            # убираем None, чтобы не добавлять "param=None" в URL
            filtered_params = {k: v for k, v in query_params.items() if v is not None}
            if filtered_params:
                url += "?" + urllib.parse.urlencode(filtered_params)
        return url

    #
    # =========== MonitorAccount ===========
    #
    async def get_monitor_account(
        self,
        pk: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> Any:
        """
        GET /api/monitors/
        """
        query_params = {}
        if user_id is not None:
            query_params["user_id"] = user_id
        return await self._request("GET", "monitors", pk=pk, query_params=query_params)

    async def create_monitor_account(self, data: Dict[str, Any]) -> Any:
        """
        POST /api/monitors/
        """
        return await self._request("POST", "monitors", data=data)

    async def update_monitor_account(
        self,
        data: Dict[str, Any],
        pk: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> Any:
        """
        PATCH /api/monitors/
        """
        query_params = {}
        if user_id is not None:
            query_params["user_id"] = user_id
        return await self._request("PATCH", "monitors", pk=pk, query_params=query_params, data=data)

    async def delete_monitor_account(
        self,
        pk: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> Any:
        """
        DELETE /api/monitors/
        """
        query_params = {}
        if user_id is not None:
            query_params["user_id"] = user_id
        return await self._request("DELETE", "monitors", pk=pk, query_params=query_params)

    #
    # =========== AccountSession ===========
    #
    async def get_account_session(
        self,
        pk: Optional[int] = None,
        monitor_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> Any:
        """
        GET /api/sessions/
        """
        query_params = {}
        if monitor_id is not None:
            query_params["monitor_id"] = monitor_id
        if user_id is not None:
            query_params["user_id"] = user_id
        return await self._request("GET", "sessions", pk=pk, query_params=query_params)

    async def create_account_session(self, data: Dict[str, Any]) -> Any:
        """
        POST /api/sessions/
        """
        return await self._request("POST", "sessions", data=data)

    async def update_account_session(
        self,
        data: Dict[str, Any],
        pk: Optional[int] = None,
        monitor_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> Any:
        """
        PATCH /api/sessions/
        """
        query_params = {}
        if monitor_id is not None:
            query_params["monitor_id"] = monitor_id
        if user_id is not None:
            query_params["user_id"] = user_id
        return await self._request("PATCH", "sessions", pk=pk, query_params=query_params, data=data)

    async def delete_account_session(
        self,
        pk: Optional[int] = None,
        monitor_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> Any:
        """
        DELETE /api/sessions/
        """
        query_params = {}
        if monitor_id is not None:
            query_params["monitor_id"] = monitor_id
        if user_id is not None:
            query_params["user_id"] = user_id
        return await self._request("DELETE", "sessions", pk=pk, query_params=query_params)

    #
    # =========== MonitorSetting ===========
    #
    async def get_monitor_setting(
        self,
        pk: Optional[int] = None,
        monitor_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> Any:
        """
        GET /api/settings/
        """
        query_params = {}
        if monitor_id is not None:
            query_params["monitor_id"] = monitor_id
        if user_id is not None:
            query_params["user_id"] = user_id
        return await self._request("GET", "settings", pk=pk, query_params=query_params)

    async def create_monitor_setting(self, data: Dict[str, Any]) -> Any:
        """
        POST /api/settings/
        """
        return await self._request("POST", "settings", data=data)

    async def update_monitor_setting(
        self,
        data: Dict[str, Any],
        pk: Optional[int] = None,
        monitor_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> Any:
        """
        PATCH /api/settings/
        """
        query_params = {}
        if monitor_id is not None:
            query_params["monitor_id"] = monitor_id
        if user_id is not None:
            query_params["user_id"] = user_id
        return await self._request("PATCH", "settings", pk=pk, query_params=query_params, data=data)

    async def delete_monitor_setting(
        self,
        pk: Optional[int] = None,
        monitor_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> Any:
        """
        DELETE /api/settings/
        """
        query_params = {}
        if monitor_id is not None:
            query_params["monitor_id"] = monitor_id
        if user_id is not None:
            query_params["user_id"] = user_id
        return await self._request("DELETE", "settings", pk=pk, query_params=query_params)

    #
    # =========== MonitoredAccount ===========
    #
    async def get_monitored_account(
        self,
        pk: Optional[int] = None,
        username: Optional[str] = None,
        monitor_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> Any:
        """
        GET /api/monitored/
        """
        query_params = {}
        if username is not None:
            query_params["username"] = username
        if monitor_id is not None:
            query_params["monitor_id"] = monitor_id
        if user_id is not None:
            query_params["user_id"] = user_id
        return await self._request("GET", "monitored", pk=pk, query_params=query_params)

    async def create_monitored_account(self, data: Dict[str, Any]) -> Any:
        """
        POST /api/monitored/
        """
        return await self._request("POST", "monitored", data=data)

    async def update_monitored_account(
        self,
        data: Dict[str, Any],
        pk: Optional[int] = None,
        username: Optional[str] = None
    ) -> Any:
        """
        PATCH /api/monitored/
        """
        query_params = {}
        if username is not None:
            query_params["username"] = username
        return await self._request("PATCH", "monitored", pk=pk, query_params=query_params, data=data)

    async def delete_monitored_account(
        self,
        pk: Optional[int] = None,
        username: Optional[str] = None
    ) -> Any:
        """
        DELETE /api/monitored/
        """
        query_params = {}
        if username is not None:
            query_params["username"] = username
        return await self._request("DELETE", "monitored", pk=pk, query_params=query_params)

    #
    # =========== OnlineStatus ===========
    #
    async def get_online_status(
        self,
        pk: Optional[int] = None,
        monitored_id: Optional[int] = None,
        username: Optional[str] = None
    ) -> Any:
        """
        GET /api/statuses/
        """
        query_params = {}
        if monitored_id is not None:
            query_params["monitored_id"] = monitored_id
        if username is not None:
            query_params["username"] = username
        return await self._request("GET", "statuses", pk=pk, query_params=query_params)
