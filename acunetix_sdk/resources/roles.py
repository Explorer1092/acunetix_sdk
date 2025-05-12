from typing import List, Optional, Dict, Any, TYPE_CHECKING

from ..models.user import ( # Roles models are in user.py
    Role, # Used for create
    RoleUpdate, # Used for update
    RoleDetails,
    PermissionsList
)
from ..models.pagination import PaginatedList # For list method
from .base_resource import BaseResource
from ..errors import AcunetixError

if TYPE_CHECKING:
    from ..client_sync import AcunetixSyncClient
    from ..client_async import AcunetixAsyncClient

class RolesSyncResource(BaseResource["AcunetixSyncClient"]):
    """Handles synchronous operations related to Acunetix Roles."""

    def list(self, query: Optional[str] = None, sort: Optional[str] = None, cursor: Optional[str] = None, limit: Optional[int] = None, extended: Optional[bool] = None) -> PaginatedList[RoleDetails]:
        """
        Lists roles.
        Corresponds to GET /roles in API.
        API operationId: get_roles
        """
        params: Dict[str, Any] = {}
        if query: params["q"] = query
        if sort: params["s"] = sort
        if cursor: params["c"] = cursor
        if limit is not None: params["l"] = limit
        if extended is not None: params["extended"] = str(extended).lower()
        
        response = self._client._request("GET", "roles", params=params)
        # API spec RolesList has "roles" and "pagination"
        if not isinstance(response, dict) or "roles" not in response or "pagination" not in response:
             raise AcunetixError("Unexpected response structure for list roles. Expected 'roles' and 'pagination' keys.")
        return PaginatedList[RoleDetails](items=response.get("roles", []), pagination=response.get("pagination", {}))

    def create(self, role_data: Role) -> RoleDetails:
        """
        Creates a new role.
        Corresponds to POST /roles in API.
        API operationId: create_role
        """
        payload = role_data.model_dump(exclude_none=True, by_alias=True, mode='json')
        response_data = self._client._request("POST", "roles", json_data=payload)
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for create role.")
        return RoleDetails(**response_data) # API returns RoleDetails

    def get_permissions(self) -> PermissionsList:
        """
        Lists all available permissions.
        Corresponds to GET /roles/permissions in API.
        API operationId: get_permissions
        """
        response_data = self._client._request("GET", "roles/permissions")
        if isinstance(response_data, list):
            # If API returns a direct list of permissions
            return PermissionsList(permissions=response_data)
        elif isinstance(response_data, dict) and "permissions" in response_data:
            # If API returns an object with a "permissions" key
            return PermissionsList(**response_data)
        else:
            raise AcunetixError("Unexpected response structure for get permissions. Expected a list of permissions or a dict with a 'permissions' key.")

    def get(self, role_id: str) -> RoleDetails:
        """
        Retrieves a specific role by ID.
        Corresponds to GET /roles/{role_id} in API.
        API operationId: get_role
        """
        response_data = self._client._request("GET", f"roles/{role_id}")
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for get role.")
        return RoleDetails(**response_data)

    def update(self, role_id: str, role_data: RoleUpdate) -> None: # Changed Role to RoleUpdate
        """
        Modifies an existing role.
        Corresponds to PATCH /roles/{role_id} in API.
        API operationId: update_role
        """
        payload = role_data.model_dump(exclude_none=True, by_alias=True, mode='json')
        self._client._request("PATCH", f"roles/{role_id}", json_data=payload)
        # API returns 204 No Content

    def delete(self, role_id: str, force_delete: Optional[bool] = None) -> None:
        """
        Deletes a specific role.
        Corresponds to DELETE /roles/{role_id} in API.
        API operationId: remove_role
        """
        params: Dict[str, Any] = {}
        if force_delete is not None:
            params["force_delete"] = str(force_delete).lower()
        self._client._request("DELETE", f"roles/{role_id}", params=params)
        # API returns 204 No Content


class RolesAsyncResource(BaseResource["AcunetixAsyncClient"]):
    """Handles asynchronous operations related to Acunetix Roles."""

    async def list(self, query: Optional[str] = None, sort: Optional[str] = None, cursor: Optional[str] = None, limit: Optional[int] = None, extended: Optional[bool] = None) -> PaginatedList[RoleDetails]:
        params: Dict[str, Any] = {}
        if query: params["q"] = query
        if sort: params["s"] = sort
        if cursor: params["c"] = cursor
        if limit is not None: params["l"] = limit
        if extended is not None: params["extended"] = str(extended).lower()
        response = await self._client._arequest("GET", "roles", params=params)
        if not isinstance(response, dict) or "roles" not in response or "pagination" not in response:
             raise AcunetixError("Unexpected response structure for list roles.")
        return PaginatedList[RoleDetails](items=response.get("roles", []), pagination=response.get("pagination", {}))

    async def create(self, role_data: Role) -> RoleDetails:
        payload = role_data.model_dump(exclude_none=True, by_alias=True, mode='json')
        response_data = await self._client._arequest("POST", "roles", json_data=payload)
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for create role.")
        return RoleDetails(**response_data)

    async def get_permissions(self) -> PermissionsList:
        response_data = await self._client._arequest("GET", "roles/permissions")
        if isinstance(response_data, list):
            # If API returns a direct list of permissions
            return PermissionsList(permissions=response_data)
        elif isinstance(response_data, dict) and "permissions" in response_data:
            # If API returns an object with a "permissions" key
            return PermissionsList(**response_data)
        else:
            raise AcunetixError("Unexpected response structure for get permissions. Expected a list of permissions or a dict with a 'permissions' key.")

    async def get(self, role_id: str) -> RoleDetails:
        response_data = await self._client._arequest("GET", f"roles/{role_id}")
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for get role.")
        return RoleDetails(**response_data)

    async def update(self, role_id: str, role_data: RoleUpdate) -> None: # Changed Role to RoleUpdate
        payload = role_data.model_dump(exclude_none=True, by_alias=True, mode='json') # exclude_none for PATCH
        await self._client._arequest("PATCH", f"roles/{role_id}", json_data=payload)

    async def delete(self, role_id: str, force_delete: Optional[bool] = None) -> None:
        params: Dict[str, Any] = {}
        if force_delete is not None:
            params["force_delete"] = str(force_delete).lower()
        await self._client._arequest("DELETE", f"roles/{role_id}", params=params)
