from typing import Optional, Dict, Any, TYPE_CHECKING, List

from ..models.notification import (
    Notification,  # This is now the Notification Configuration model
    NotificationList, # Added for listing notification configurations
    NotificationCreateRequest,
    NotificationUpdateRequest,
    NotificationIdList,
    SystemEventNotification # If needed for other endpoints that list system events
)
# from ..models.pagination import PaginatedList # No longer needed directly for list()
from .base_resource import BaseResource
from ..errors import AcunetixError

if TYPE_CHECKING:
    from ..client_sync import AcunetixSyncClient
    from ..client_async import AcunetixAsyncClient

class NotificationsSyncResource(BaseResource["AcunetixSyncClient"]):
    """同步通知资源。"""

    def list(self, cursor: Optional[str] = None, limit: Optional[int] = None, query: Optional[str] = None, sort: Optional[str] = None, unread: Optional[bool] = None) -> NotificationList: # Changed return type
        params: Dict[str, Any] = {}
        if cursor: params["c"] = cursor
        if limit is not None: params["l"] = limit
        if query: params["q"] = query
        if sort: params["s"] = sort
        if unread is not None: params["unread"] = str(unread).lower() # Note: 'unread' param is for system events, not for notification configurations.
                                                                    # Listing configurations does not support 'unread'.
                                                                    # This parameter should ideally be removed or handled if this method is intended for system events.
                                                                    # For now, we assume this 'list' is for configurations.

        response = self._client._request("GET", "me/notifications", params=params) # Changed path to "me/notifications"
        if not isinstance(response, dict):
            raise AcunetixError("Unexpected response structure for list notification configurations.")
        return NotificationList(**response) # Use NotificationList to parse

    def mark_as_read(self, notification_id: str) -> None:
        self._client._request("POST", f"notifications/{notification_id}/read")

    def mark_many_as_read(self, notification_ids: Optional[List[str]] = None) -> None:
        payload_data: Optional[Dict[str, Any]] = None
        if notification_ids is not None:
            payload = NotificationIdList(notification_id_list=notification_ids)
            payload_data = payload.model_dump(exclude_none=True, by_alias=True, mode='json')
        self._client._request("POST", "notifications/read", json_data=payload_data)

    # This delete method is for system event notifications.
    # To delete a notification configuration, use delete_configuration below.
    # def delete(self, notification_id: str) -> None:
    #     self._client._request("DELETE", f"notifications/{notification_id}")

    def create(self, notification_data: NotificationCreateRequest) -> Notification:
        """创建新的通知配置。"""
        response = self._client._request("POST", "me/notifications", json_data=notification_data.model_dump(exclude_none=True, by_alias=True, mode='json'))
        if not isinstance(response, dict):
            raise AcunetixError("Unexpected response structure for create notification configuration.")
        return Notification.model_validate(response)

    def get(self, notification_id: str) -> Notification:
        """获取单个通知配置的详细信息。"""
        response = self._client._request("GET", f"me/notifications/{notification_id}") # Changed path
        if not isinstance(response, dict):
            raise AcunetixError("Unexpected response structure for get notification configuration.")
        return Notification.model_validate(response)

    def update(self, notification_id: str, notification_data: NotificationUpdateRequest) -> Notification:
        """更新现有通知配置。"""
        response = self._client._request("PUT", f"me/notifications/{notification_id}", json_data=notification_data.model_dump(exclude_none=True, by_alias=True, mode='json')) # Changed path
        if not isinstance(response, dict):
            raise AcunetixError("Unexpected response structure for update notification configuration.")
        return Notification.model_validate(response)

    def delete_configuration(self, notification_id: str) -> None: # Renamed from delete to be specific
        """删除通知配置。"""
        self._client._request("DELETE", f"me/notifications/{notification_id}") # Changed path


class NotificationsAsyncResource(BaseResource["AcunetixAsyncClient"]):
    """异步通知资源。"""

    async def list(self, cursor: Optional[str] = None, limit: Optional[int] = None, query: Optional[str] = None, sort: Optional[str] = None, unread: Optional[bool] = None) -> NotificationList: # Changed return type
        params: Dict[str, Any] = {}
        if cursor: params["c"] = cursor
        if limit is not None: params["l"] = limit
        if query: params["q"] = query
        if sort: params["s"] = sort
        if unread is not None: params["unread"] = str(unread).lower() # See note above for sync version.

        response = await self._client._arequest("GET", "me/notifications", params=params) # Changed path to "me/notifications"
        if not isinstance(response, dict):
            raise AcunetixError("Unexpected response structure for list notification configurations.")
        return NotificationList(**response) # Use NotificationList to parse

    async def mark_as_read(self, notification_id: str) -> None:
        await self._client._arequest("POST", f"notifications/{notification_id}/read")

    async def mark_many_as_read(self, notification_ids: Optional[List[str]] = None) -> None:
        payload_data: Optional[Dict[str, Any]] = None
        if notification_ids is not None:
            payload = NotificationIdList(notification_id_list=notification_ids)
            payload_data = payload.model_dump(exclude_none=True, by_alias=True, mode='json')
        await self._client._arequest("POST", "notifications/read", json_data=payload_data)

    # This delete method is for system event notifications.
    # async def delete(self, notification_id: str) -> None:
    #     await self._client._arequest("DELETE", f"notifications/{notification_id}")

    async def create(self, notification_data: NotificationCreateRequest) -> Notification:
        """异步创建新的通知配置。"""
        response = await self._client._arequest("POST", "me/notifications", json_data=notification_data.model_dump(exclude_none=True, by_alias=True, mode='json'))
        if not isinstance(response, dict):
            raise AcunetixError("Unexpected response structure for create notification configuration.")
        return Notification.model_validate(response)

    async def get(self, notification_id: str) -> Notification:
        """异步获取单个通知配置的详细信息。"""
        response = await self._client._arequest("GET", f"me/notifications/{notification_id}") # Changed path
        if not isinstance(response, dict):
            raise AcunetixError("Unexpected response structure for get notification configuration.")
        return Notification.model_validate(response)

    async def update(self, notification_id: str, notification_data: NotificationUpdateRequest) -> Notification:
        """异步更新现有通知配置。"""
        response = await self._client._arequest("PUT", f"me/notifications/{notification_id}", json_data=notification_data.model_dump(exclude_none=True, by_alias=True, mode='json')) # Changed path
        if not isinstance(response, dict):
            raise AcunetixError("Unexpected response structure for update notification configuration.")
        return Notification.model_validate(response)

    async def delete_configuration(self, notification_id: str) -> None: # Renamed from delete
        """异步删除通知配置。"""
        await self._client._arequest("DELETE", f"me/notifications/{notification_id}") # Changed path
