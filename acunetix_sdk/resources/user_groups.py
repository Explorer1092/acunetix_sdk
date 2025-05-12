from typing import List, Optional, Dict, Any, TYPE_CHECKING

from ..models.user import (
    UserGroup, # Used for create
    UserGroupUpdate, # Used for update
    UserGroupDetails,
    ChildUserIdList, # Used for adding/removing users from a group
    UserToUserGroupDetails,
    RoleMappingList, # Used as request body for adding roles
    RoleMappingIdList, # Used as request body for removing roles
    UserGroupRoleMappings # Used as response for adding roles
)
from ..models.pagination import PaginatedList # For list method
from .base_resource import BaseResource
from ..errors import AcunetixError

if TYPE_CHECKING:
    from ..client_sync import AcunetixSyncClient
    from ..client_async import AcunetixAsyncClient

class UserGroupsSyncResource(BaseResource["AcunetixSyncClient"]):
    """Handles synchronous operations related to Acunetix User Groups."""

    def list(self, query: Optional[str] = None, sort: Optional[str] = None, cursor: Optional[str] = None, limit: Optional[int] = None, extended: Optional[bool] = None) -> PaginatedList[UserGroupDetails]:
        """
        Lists user groups.
        Corresponds to GET /user_groups in API.
        API operationId: get_user_groups
        """
        params: Dict[str, Any] = {}
        if query: params["q"] = query
        if sort: params["s"] = sort
        if cursor: params["c"] = cursor
        if limit is not None: params["l"] = limit
        if extended is not None: params["extended"] = str(extended).lower()
        
        response = self._client._request("GET", "user_groups", params=params)
        # API spec UserGroupsList has "user_groups" and "pagination"
        if not isinstance(response, dict) or "user_groups" not in response or "pagination" not in response:
             raise AcunetixError("Unexpected response structure for list user groups. Expected 'user_groups' and 'pagination' keys.")
        return PaginatedList[UserGroupDetails](items=response.get("user_groups", []), pagination=response.get("pagination", {}))

    def create(self, group_data: UserGroup) -> UserGroupDetails:
        """
        Creates a new user group.
        Corresponds to POST /user_groups in API.
        API operationId: create_user_group
        """
        payload = group_data.model_dump(exclude_none=True, by_alias=True, mode='json')
        response_data = self._client._request("POST", "user_groups", json_data=payload)
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for create user group.")
        return UserGroupDetails(**response_data) # API returns UserGroupDetails

    def get(self, user_group_id: str) -> UserGroupDetails:
        """
        Retrieves a specific user group by ID.
        Corresponds to GET /user_groups/{user_group_id} in API.
        API operationId: get_user_group
        """
        response_data = self._client._request("GET", f"user_groups/{user_group_id}")
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for get user group.")
        return UserGroupDetails(**response_data)

    def update(self, user_group_id: str, group_data: UserGroupUpdate) -> None: # Changed UserGroup to UserGroupUpdate
        """
        Modifies an existing user group.
        Corresponds to PATCH /user_groups/{user_group_id} in API.
        API operationId: update_user_group
        """
        payload = group_data.model_dump(exclude_none=True, by_alias=True, mode='json')
        self._client._request("PATCH", f"user_groups/{user_group_id}", json_data=payload)
        # API returns 204 No Content

    def delete(self, user_group_id: str, force_delete: Optional[bool] = None) -> None:
        """
        Deletes a specific user group.
        Corresponds to DELETE /user_groups/{user_group_id} in API.
        API operationId: remove_user_group
        """
        params: Dict[str, Any] = {}
        if force_delete is not None:
            params["force_delete"] = str(force_delete).lower()
        self._client._request("DELETE", f"user_groups/{user_group_id}", params=params)
        # API returns 204 No Content

    def add_users_to_group(self, user_group_id: str, user_id_list: ChildUserIdList) -> UserToUserGroupDetails:
        """
        Adds users to a user group.
        Corresponds to POST /user_groups/{user_group_id}/users in API.
        API operationId: add_users_to_user_group
        """
        payload = user_id_list.model_dump(exclude_none=True, by_alias=True, mode='json')
        response_data = self._client._request("POST", f"user_groups/{user_group_id}/users", json_data=payload)
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for add users to group.")
        return UserToUserGroupDetails(**response_data)

    def remove_users_from_group(self, user_group_id: str, user_id_list: ChildUserIdList) -> None:
        """
        Removes users from a user group.
        Corresponds to DELETE /user_groups/{user_group_id}/users in API.
        API operationId: remove_users_from_user_group
        """
        payload = user_id_list.model_dump(exclude_none=True, by_alias=True, mode='json')
        self._client._request("DELETE", f"user_groups/{user_group_id}/users", json_data=payload)
        # API returns 204 No Content

    def get_role_mappings(self, user_group_id: str) -> UserGroupRoleMappings: # Assuming response is UserGroupRoleMappings
        """
        Lists all role mappings for the user group.
        Corresponds to GET /user_groups/{user_group_id}/roles in API.
        API operationId: get_user_group_role_mappings
        Note: API spec does not explicitly define response model for this GET, assuming UserGroupRoleMappings.
        """
        response_data = self._client._request("GET", f"user_groups/{user_group_id}/roles")
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for get role mappings for group.")
        return UserGroupRoleMappings(**response_data)


    def add_role_mappings_to_group(self, user_group_id: str, role_mapping_list: RoleMappingList) -> UserGroupRoleMappings:
        """
        Adds role mappings to a user group.
        Corresponds to POST /user_groups/{user_group_id}/roles in API.
        API operationId: add_role_mappings_to_user_group
        """
        payload = role_mapping_list.model_dump(exclude_none=True, by_alias=True, mode='json')
        response_data = self._client._request("POST", f"user_groups/{user_group_id}/roles", json_data=payload)
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for add role mappings to group.")
        return UserGroupRoleMappings(**response_data)

    def remove_role_mappings_from_group(self, user_group_id: str, role_mapping_id_list: RoleMappingIdList) -> None:
        """
        Removes role mappings from a user group.
        Corresponds to DELETE /user_groups/{user_group_id}/roles in API.
        API operationId: remove_role_mappings_from_user_group
        """
        payload = role_mapping_id_list.model_dump(exclude_none=True, by_alias=True, mode='json')
        self._client._request("DELETE", f"user_groups/{user_group_id}/roles", json_data=payload)
        # API returns 204 No Content


class UserGroupsAsyncResource(BaseResource["AcunetixAsyncClient"]):
    """Handles asynchronous operations related to Acunetix User Groups."""

    async def list(self, query: Optional[str] = None, sort: Optional[str] = None, cursor: Optional[str] = None, limit: Optional[int] = None, extended: Optional[bool] = None) -> PaginatedList[UserGroupDetails]:
        params: Dict[str, Any] = {}
        if query: params["q"] = query
        if sort: params["s"] = sort
        if cursor: params["c"] = cursor
        if limit is not None: params["l"] = limit
        if extended is not None: params["extended"] = str(extended).lower()
        response = await self._client._arequest("GET", "user_groups", params=params)
        if not isinstance(response, dict) or "user_groups" not in response or "pagination" not in response:
             raise AcunetixError("Unexpected response structure for list user groups.")
        return PaginatedList[UserGroupDetails](items=response.get("user_groups", []), pagination=response.get("pagination", {}))

    async def create(self, group_data: UserGroup) -> UserGroupDetails:
        payload = group_data.model_dump(exclude_none=True, by_alias=True, mode='json')
        response_data = await self._client._arequest("POST", "user_groups", json_data=payload)
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for create user group.")
        return UserGroupDetails(**response_data)

    async def get(self, user_group_id: str) -> UserGroupDetails:
        response_data = await self._client._arequest("GET", f"user_groups/{user_group_id}")
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for get user group.")
        return UserGroupDetails(**response_data)

    async def update(self, user_group_id: str, group_data: UserGroupUpdate) -> None: # Changed UserGroup to UserGroupUpdate
        payload = group_data.model_dump(exclude_none=True, by_alias=True, mode='json') # exclude_none is important for PATCH
        await self._client._arequest("PATCH", f"user_groups/{user_group_id}", json_data=payload)

    async def delete(self, user_group_id: str, force_delete: Optional[bool] = None) -> None:
        params: Dict[str, Any] = {}
        if force_delete is not None:
            params["force_delete"] = str(force_delete).lower()
        await self._client._arequest("DELETE", f"user_groups/{user_group_id}", params=params)

    async def add_users_to_group(self, user_group_id: str, user_id_list: ChildUserIdList) -> UserToUserGroupDetails:
        payload = user_id_list.model_dump(exclude_none=True, by_alias=True, mode='json')
        response_data = await self._client._arequest("POST", f"user_groups/{user_group_id}/users", json_data=payload)
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for add users to group.")
        return UserToUserGroupDetails(**response_data)

    async def remove_users_from_group(self, user_group_id: str, user_id_list: ChildUserIdList) -> None:
        payload = user_id_list.model_dump(exclude_none=True, by_alias=True, mode='json')
        await self._client._arequest("DELETE", f"user_groups/{user_group_id}/users", json_data=payload)

    async def get_role_mappings(self, user_group_id: str) -> UserGroupRoleMappings:
        response_data = await self._client._arequest("GET", f"user_groups/{user_group_id}/roles")
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for get role mappings for group.")
        return UserGroupRoleMappings(**response_data)

    async def add_role_mappings_to_group(self, user_group_id: str, role_mapping_list: RoleMappingList) -> UserGroupRoleMappings:
        payload = role_mapping_list.model_dump(exclude_none=True, by_alias=True, mode='json')
        response_data = await self._client._arequest("POST", f"user_groups/{user_group_id}/roles", json_data=payload)
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for add role mappings to group.")
        return UserGroupRoleMappings(**response_data)

    async def remove_role_mappings_from_group(self, user_group_id: str, role_mapping_id_list: RoleMappingIdList) -> None:
        payload = role_mapping_id_list.model_dump(exclude_none=True, by_alias=True, mode='json')
        await self._client._arequest("DELETE", f"user_groups/{user_group_id}/roles", json_data=payload)
