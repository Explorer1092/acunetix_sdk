from typing import List, Optional, Any, Dict
from acunetix_sdk.http_clients import SyncHTTPClient, AsyncHTTPClient
from acunetix_sdk.models.target_group import (
    TargetGroup,
    TargetGroupIdList,
    TargetGroupListResponse
)
from acunetix_sdk.models.target import TargetIdList, GroupChangeTargetIdList  # 确保 GroupChangeTargetIdList 被导入
from acunetix_sdk.resources.base_resource import BaseResource


class TargetGroupsBaseResource(BaseResource):
    def __init__(self, client: Any): # Changed parameters
        super().__init__(client=client)
        # self.resource_url is not needed here if using self._client._request with relative paths
        # or if BaseResource handles path joining.
        # For now, assuming paths passed to _request will be relative to base_url.

    def _prepare_list_params(self, query: Optional[str] = None, cursor: Optional[str] = None,
                             limit: Optional[int] = None, sort: Optional[str] = None) -> Dict[str, Any]:
        params = {}
        if query:
            params['q'] = query
        if cursor:
            params['c'] = cursor
        if limit:
            params['l'] = limit
        if sort:
            params['s'] = sort
        return params

    def _prepare_modify_targets_payload(self, add_target_ids: Optional[List[str]] = None,
                                        remove_target_ids: Optional[List[str]] = None) -> Dict[str, List[str]]:
        payload: Dict[str, List[str]] = {}
        if add_target_ids:
            payload["add"] = add_target_ids
        if remove_target_ids:
            payload["remove"] = remove_target_ids
        return payload


class TargetGroupsSyncResource(TargetGroupsBaseResource):
    def __init__(self, client: Any): # Changed signature
        super().__init__(client)

    def list(self, query: Optional[str] = None, cursor: Optional[str] = None,
             limit: Optional[int] = None, sort: Optional[str] = None) -> TargetGroupListResponse:
        params = self._prepare_list_params(query, cursor, limit, sort)
        response_data = self._client._request("GET", "target_groups", params=params) # Use client._request
        return TargetGroupListResponse.model_validate(response_data) # Use model_validate

    def create(self, target_group: TargetGroup) -> TargetGroup: # Assuming TargetGroup is used for create payload
        response_data = self._client._request(
            "POST",
            "target_groups",
            json_data=target_group.model_dump(exclude_none=True, by_alias=True, mode='json')
        )
        return TargetGroup.model_validate(response_data)

    def get(self, group_id: str) -> TargetGroup:
        response_data = self._client._request("GET", f"target_groups/{group_id}")
        return TargetGroup.model_validate(response_data)

    def update(self, group_id: str, target_group_update: TargetGroup) -> None: # Assuming TargetGroup for update
        self._client._request(
            "PATCH",
            f"target_groups/{group_id}",
            json_data=target_group_update.model_dump(exclude_none=True, by_alias=True, mode='json')
        ) # API might return 204 No Content or the updated object. Adjust if needed.

    def delete(self, group_id: str) -> None:
        self._client._request("DELETE", f"target_groups/{group_id}") # Removed expect_json_response

    def delete_multiple(self, group_ids: List[str]) -> None:
        payload = TargetGroupIdList(group_id_list=group_ids)
        self._client._request("POST", "target_groups/delete", json_data=payload.model_dump(exclude_none=True, by_alias=True, mode='json')) # Removed expect_json_response

    def list_targets_in_group(self, group_id: str) -> TargetIdList: # Return type might be PaginatedList[TargetBrief]
        response_data = self._client._request("GET", f"target_groups/{group_id}/targets")
        return TargetIdList.model_validate(response_data) # Or PaginatedList[TargetBrief].model_validate

    def assign_targets_to_group(self, group_id: str, target_ids: List[str]) -> None:
        payload = TargetIdList(target_id_list=target_ids)
        self._client._request("POST", f"target_groups/{group_id}/targets", json_data=payload.model_dump(exclude_none=True, by_alias=True, mode='json')) # Removed expect_json_response

    def modify_targets_in_group(self, group_id: str, add_target_ids: Optional[List[str]] = None,
                               remove_target_ids: Optional[List[str]] = None) -> None:
        payload_dict = self._prepare_modify_targets_payload(add_target_ids, remove_target_ids)
        self._client._request("PATCH", f"target_groups/{group_id}/targets", json_data=payload_dict) # Removed expect_json_response


class TargetGroupsAsyncResource(TargetGroupsBaseResource):
    def __init__(self, client: Any): # Changed signature
        super().__init__(client)

    async def list(self, query: Optional[str] = None, cursor: Optional[str] = None,
                   limit: Optional[int] = None, sort: Optional[str] = None) -> TargetGroupListResponse:
        params = self._prepare_list_params(query, cursor, limit, sort)
        response_data = await self._client._arequest("GET", "target_groups", params=params)
        return TargetGroupListResponse.model_validate(response_data)

    async def create(self, target_group: TargetGroup) -> TargetGroup:
        response_data = await self._client._arequest(
            "POST",
            "target_groups",
            json_data=target_group.model_dump(exclude_none=True, by_alias=True, mode='json')
        )
        return TargetGroup.model_validate(response_data)

    async def get(self, group_id: str) -> TargetGroup:
        response_data = await self._client._arequest("GET", f"target_groups/{group_id}")
        return TargetGroup.model_validate(response_data)

    async def update(self, group_id: str, target_group_update: TargetGroup) -> None:
        await self._client._arequest(
            "PATCH",
            f"target_groups/{group_id}",
            json_data=target_group_update.model_dump(exclude_none=True, by_alias=True, mode='json')
        )

    async def delete(self, group_id: str) -> None:
        await self._client._arequest("DELETE", f"target_groups/{group_id}") # Removed expect_json_response

    async def delete_multiple(self, group_ids: List[str]) -> None:
        payload = TargetGroupIdList(group_id_list=group_ids)
        await self._client._arequest("POST", "target_groups/delete", json_data=payload.model_dump(exclude_none=True, by_alias=True, mode='json')) # Removed expect_json_response

    async def list_targets_in_group(self, group_id: str) -> TargetIdList:
        response_data = await self._client._arequest("GET", f"target_groups/{group_id}/targets")
        return TargetIdList.model_validate(response_data)

    async def assign_targets_to_group(self, group_id: str, target_ids: List[str]) -> None:
        payload = TargetIdList(target_id_list=target_ids)
        await self._client._arequest("POST", f"target_groups/{group_id}/targets", json_data=payload.model_dump(exclude_none=True, by_alias=True, mode='json')) # Removed expect_json_response

    async def modify_targets_in_group(self, group_id: str, add_target_ids: Optional[List[str]] = None,
                                     remove_target_ids: Optional[List[str]] = None) -> None:
        payload_dict = self._prepare_modify_targets_payload(add_target_ids, remove_target_ids)
        await self._client._arequest("PATCH", f"target_groups/{group_id}/targets", json_data=payload_dict) # Removed expect_json_response
