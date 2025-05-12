from typing import Optional, TYPE_CHECKING

from ..models.excluded_hours import ExcludedHoursProfile, ExcludedHoursProfilesList
from .base_resource import BaseResource
from ..errors import AcunetixError

if TYPE_CHECKING:
    from ..client_sync import AcunetixSyncClient
    from ..client_async import AcunetixAsyncClient

class ExcludedHoursSyncResource(BaseResource["AcunetixSyncClient"]):
    """
    Handles synchronous operations related to Acunetix Excluded Hours Profiles.
    """

    def list(self) -> ExcludedHoursProfilesList:
        """
        Lists all excluded hours profiles.
        Corresponds to GET /excluded_hours_profiles in API.
        API operationId: get_excluded_hours_profiles
        """
        response_data = self._client._request("GET", "excluded_hours_profiles")
        if not isinstance(response_data, dict): # API returns ExcludedHoursProfilesList directly
            raise AcunetixError("Unexpected response type for list excluded hours profiles.")
        return ExcludedHoursProfilesList(**response_data)

    def create(self, profile_data: ExcludedHoursProfile) -> ExcludedHoursProfile:
        """
        创建新的排除时段配置。
        对应API中的 POST /excluded_hours_profiles。
        API operationId: create_excluded_hours_profile。
        API返回201 Created，创建成功后返回配置详情。
        """
        payload = profile_data.model_dump(exclude={"excluded_hours_id"}, exclude_none=True, by_alias=True, mode='json')
        response_data = self._client._request("POST", "excluded_hours_profiles", json_data=payload)
        
        # 创建后立即获取详情
        if isinstance(response_data, dict) and "excluded_hours_id" in response_data:
            return ExcludedHoursProfile(**response_data)
        elif isinstance(response_data, dict) and "location" in response_data:
            # 如果API返回location字段
            location = response_data["location"]
            profile_id = location.split("/")[-1] if location else None
            if profile_id:
                return self.get(profile_id)
        
        # 成功创建但无法获取详情，返回原始配置
        return profile_data

    def get(self, excluded_hours_id: str) -> ExcludedHoursProfile:
        """
        Retrieves a specific excluded hours profile by ID.
        Corresponds to GET /excluded_hours_profiles/{excluded_hours_id} in API.
        API operationId: get_excluded_hours_profile
        """
        response_data = self._client._request("GET", f"excluded_hours_profiles/{excluded_hours_id}")
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for get excluded hours profile.")
        return ExcludedHoursProfile(**response_data)

    def update(self, excluded_hours_id: str, profile_data: ExcludedHoursProfile) -> ExcludedHoursProfile: 
        """
        修改现有的排除时段配置。
        对应API中的 PATCH /excluded_hours_profiles/{excluded_hours_id}。
        API operationId: modify_excluded_hours_profile。
        API返回203 Accepted，更新成功后返回更新后的配置详情。
        """
        # 对于PATCH请求，excluded_hours_id不应包含在载荷中
        payload = profile_data.model_dump(exclude={"excluded_hours_id"}, exclude_none=True, by_alias=True, mode='json')
        self._client._request("PATCH", f"excluded_hours_profiles/{excluded_hours_id}", json_data=payload)
        # 更新后立即获取详情
        return self.get(excluded_hours_id)

    def delete(self, excluded_hours_id: str) -> None:
        """
        Deletes a specific excluded hours profile.
        Corresponds to DELETE /excluded_hours_profiles/{excluded_hours_id} in API.
        API operationId: remove_excluded_hours_profile
        """
        self._client._request("DELETE", f"excluded_hours_profiles/{excluded_hours_id}")
        # API returns 204 No Content


class ExcludedHoursAsyncResource(BaseResource["AcunetixAsyncClient"]):
    """
    Handles asynchronous operations related to Acunetix Excluded Hours Profiles.
    """

    async def list(self) -> ExcludedHoursProfilesList:
        response_data = await self._client._arequest("GET", "excluded_hours_profiles")
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for list excluded hours profiles.")
        return ExcludedHoursProfilesList(**response_data)

    async def create(self, profile_data: ExcludedHoursProfile) -> ExcludedHoursProfile:
        """
        异步创建新的排除时段配置。
        API返回201 Created，创建成功后返回配置详情。
        """
        payload = profile_data.model_dump(exclude={"excluded_hours_id"}, exclude_none=True, by_alias=True, mode='json')
        response_data = await self._client._arequest("POST", "excluded_hours_profiles", json_data=payload)
        
        # 创建后立即获取详情
        if isinstance(response_data, dict) and "excluded_hours_id" in response_data:
            return ExcludedHoursProfile(**response_data)
        elif isinstance(response_data, dict) and "location" in response_data:
            # 如果API返回location字段
            location = response_data["location"]
            profile_id = location.split("/")[-1] if location else None
            if profile_id:
                return await self.get(profile_id)
        
        # 成功创建但无法获取详情，返回原始配置
        return profile_data

    async def get(self, excluded_hours_id: str) -> ExcludedHoursProfile:
        response_data = await self._client._arequest("GET", f"excluded_hours_profiles/{excluded_hours_id}")
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for get excluded hours profile.")
        return ExcludedHoursProfile(**response_data)

    async def update(self, excluded_hours_id: str, profile_data: ExcludedHoursProfile) -> ExcludedHoursProfile:
        payload = profile_data.model_dump(exclude={"excluded_hours_id"}, exclude_none=True, by_alias=True, mode='json')
        await self._client._arequest("PATCH", f"excluded_hours_profiles/{excluded_hours_id}", json_data=payload)
        # 更新后立即获取详情
        return await self.get(excluded_hours_id)

    async def delete(self, excluded_hours_id: str) -> None:
        await self._client._arequest("DELETE", f"excluded_hours_profiles/{excluded_hours_id}")
