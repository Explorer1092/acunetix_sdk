from typing import List, Optional, Dict, Any, TYPE_CHECKING

from ..models.user import User, UserBrief, UserCreate, UserUpdate, ChildUserIdList
from ..models.pagination import PaginatedList
from .base_resource import BaseResource
from ..errors import AcunetixError

# 仅用于类型提示，使用下划线前缀规避未使用警告
if TYPE_CHECKING:  # pragma: no cover
    from ..client_sync import AcunetixSyncClient as _AcunetixSyncClient  # noqa: F401
    from ..client_async import AcunetixAsyncClient as _AcunetixAsyncClient  # noqa: F401

class UsersSyncResource(BaseResource["_AcunetixSyncClient"]):
    """Handles synchronous operations related to Acunetix users."""

    def list(self, cursor: Optional[str] = None, limit: Optional[int] = None, query: Optional[str] = None, sort: Optional[str] = None) -> PaginatedList[UserBrief]:
        """
        Lists users.
        Corresponds to GET /users in API.
        """
        params: Dict[str, Any] = {}
        if cursor:
            params["c"] = cursor
        if limit is not None:
            params["l"] = limit
        if query:
            params["q"] = query
        if sort:
            params["s"] = sort
        response = self._client._request("GET", "users", params=params)
        # API doc uses ChildUserListResponse which contains 'users' and 'pagination'
        # SDK PaginatedList expects 'items' and 'pagination'
        # Assuming API response structure is {"users": [...], "pagination": {...}}
        # We need to adapt this if the actual API response key for items is different.
        # For now, let's assume the API response is {"items": [...], "pagination": {...}} or it's adapted by _request
        if not isinstance(response, dict) or "users" not in response or "pagination" not in response:
             raise AcunetixError("Unexpected response structure for list users. Expected 'users' and 'pagination' keys.")
        return PaginatedList[UserBrief](items=response.get("users", []), pagination=response.get("pagination", {}))

    def create(self, user_data: UserCreate, send_email: Optional[bool] = None) -> User:
        """
        Creates a new user.
        Corresponds to POST /users in API.
        API operationId: add_user
        """
        params: Dict[str, Any] = {}
        if send_email is not None:
            params["send_email"] = send_email
        
        response_data = self._client._request("POST", "users", json_data=user_data.model_dump(exclude_none=True, by_alias=True, mode='json'), params=params)
        if not isinstance(response_data, dict): 
            raise AcunetixError("Unexpected response type for create user. Expected a dictionary.")
        return User(**response_data) # API returns 201 with ChildUser

    def get(self, user_id: str) -> User:
        """
        Retrieves a specific user by ID.
        Corresponds to GET /users/{user_id} in API.
        API operationId: get_user
        """
        response_data = self._client._request("GET", f"users/{user_id}")
        if not isinstance(response_data, dict): 
            raise AcunetixError("Unexpected response type for get user. Expected a dictionary.")
        return User(**response_data) # API returns ChildUser

    # def get_me(self) -> User:
    #     """
    #     Retrieves the current authenticated user.
    #     Note: Endpoint /me or /users/me is not explicitly defined in the provided OpenAPI spec.
    #     This method assumes such an endpoint exists.
    #     """
    #     # Common practice, but verify if Acunetix API supports /me or similar
    #     response_data = self._client._request("GET", "me")
    #     if not isinstance(response_data, dict):
    #         raise AcunetixError("Unexpected response type for get_me. Expected a dictionary.")
    #     return User(**response_data)

    def update(self, user_id: str, update_data: UserUpdate) -> None:
        """
        Modifies an existing user.
        Corresponds to PATCH /users/{user_id} in API.
        API operationId: update_user
        API returns 204 No Content on success.
        """
        self._client._request("PATCH", f"users/{user_id}", json_data=update_data.model_dump(exclude_none=True, by_alias=True, mode='json'))
        # No return value as API returns 204

    def delete(self, user_id: str) -> None:
        """
        Deletes a specific user.
        Corresponds to DELETE /users/{user_id} in API.
        API operationId: remove_user
        API returns 204 No Content on success.
        """
        self._client._request("DELETE", f"users/{user_id}")

    def delete_many(self, user_ids: List[str]) -> None:
        """
        Removes multiple users.
        Corresponds to POST /users/delete in API.
        API operationId: remove_users
        """
        payload = ChildUserIdList(user_id_list=user_ids)
        self._client._request("POST", "users/delete", json_data=payload.model_dump(exclude_none=True, by_alias=True, mode='json'))

    def enable_many(self, user_ids: List[str]) -> None:
        """
        Enables multiple users.
        Corresponds to POST /users/enable in API.
        API operationId: enable_users
        """
        payload = ChildUserIdList(user_id_list=user_ids)
        self._client._request("POST", "users/enable", json_data=payload.model_dump(exclude_none=True, by_alias=True, mode='json'))

    def disable_many(self, user_ids: List[str]) -> None:
        """
        Disables multiple users.
        Corresponds to POST /users/disable in API.
        API operationId: disable_users
        """
        payload = ChildUserIdList(user_id_list=user_ids)
        self._client._request("POST", "users/disable", json_data=payload.model_dump(exclude_none=True, by_alias=True, mode='json'))


class UsersAsyncResource(BaseResource["_AcunetixAsyncClient"]):
    """Handles asynchronous operations related to Acunetix users."""

    async def list(self, cursor: Optional[str] = None, limit: Optional[int] = None, query: Optional[str] = None, sort: Optional[str] = None) -> PaginatedList[UserBrief]:
        """Lists users asynchronously."""
        params: Dict[str, Any] = {}
        if cursor:
            params["c"] = cursor
        if limit is not None:
            params["l"] = limit
        if query:
            params["q"] = query
        if sort:
            params["s"] = sort
        response = await self._client._arequest("GET", "users", params=params)
        if not isinstance(response, dict) or "users" not in response or "pagination" not in response:
             raise AcunetixError("Unexpected response structure for list users. Expected 'users' and 'pagination' keys.")
        return PaginatedList[UserBrief](items=response.get("users", []), pagination=response.get("pagination", {}))

    async def create(self, user_data: UserCreate, send_email: Optional[bool] = None) -> User:
        """Creates a new user asynchronously."""
        params: Dict[str, Any] = {}
        if send_email is not None:
            params["send_email"] = send_email
        response_data = await self._client._arequest("POST", "users", json_data=user_data.model_dump(exclude_none=True, by_alias=True, mode='json'), params=params)
        if not isinstance(response_data, dict): 
            raise AcunetixError("Unexpected response type for create user. Expected a dictionary.")
        return User(**response_data)

    async def get(self, user_id: str) -> User:
        """Retrieves a specific user by ID asynchronously."""
        response_data = await self._client._arequest("GET", f"users/{user_id}")
        if not isinstance(response_data, dict): 
            raise AcunetixError("Unexpected response type for get user. Expected a dictionary.")
        return User(**response_data)
    
    # async def get_me(self) -> User:
    #     """
    #     Retrieves the current authenticated user asynchronously.
    #     Note: Endpoint /me or /users/me is not explicitly defined in the provided OpenAPI spec.
    #     """
    #     response_data = await self._client._arequest("GET", "me")
    #     if not isinstance(response_data, dict):
    #         raise AcunetixError("Unexpected response type for get_me. Expected a dictionary.")
    #     return User(**response_data)

    async def update(self, user_id: str, update_data: UserUpdate) -> None:
        """Modifies an existing user asynchronously."""
        await self._client._arequest("PATCH", f"users/{user_id}", json_data=update_data.model_dump(exclude_none=True, by_alias=True, mode='json'))

    async def delete(self, user_id: str) -> None:
        """Deletes a specific user asynchronously."""
        await self._client._arequest("DELETE", f"users/{user_id}")

    async def delete_many(self, user_ids: List[str]) -> None:
        """Removes multiple users asynchronously."""
        payload = ChildUserIdList(user_id_list=user_ids)
        await self._client._arequest("POST", "users/delete", json_data=payload.model_dump(exclude_none=True, by_alias=True, mode='json'))

    async def enable_many(self, user_ids: List[str]) -> None:
        """Enables multiple users asynchronously."""
        payload = ChildUserIdList(user_id_list=user_ids)
        await self._client._arequest("POST", "users/enable", json_data=payload.model_dump(exclude_none=True, by_alias=True, mode='json'))

    async def disable_many(self, user_ids: List[str]) -> None:
        """Disables multiple users asynchronously."""
        payload = ChildUserIdList(user_id_list=user_ids)
        await self._client._arequest("POST", "users/disable", json_data=payload.model_dump(exclude_none=True, by_alias=True, mode='json'))
