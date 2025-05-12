from typing import Optional, Dict, Any, TYPE_CHECKING, List # Added List

from ..models.scan_profile import ScanningProfile
from .base_resource import BaseResource
from ..errors import AcunetixError

if TYPE_CHECKING:
    from ..client_sync import AcunetixSyncClient
    from ..client_async import AcunetixAsyncClient

class ScanProfilesSyncResource(BaseResource["AcunetixSyncClient"]):
    """Handles synchronous operations related to Acunetix scan profiles."""

    def list(self) -> List[ScanningProfile]:
        """
        Lists scan profiles.
        Corresponds to GET /scanning_profiles in API.
        API operationId: get_scanning_profiles.
        This endpoint does not support pagination or filtering according to the API spec.
        """
        response = self._client._request("GET", "scanning_profiles")
        
        # API spec for GET /scanning_profiles returns ScanningProfilesResponse,
        # which has a "scanning_profiles" property (array of ScanningProfile).
        if not isinstance(response, dict) or "scanning_profiles" not in response:
            # Fallback if API returns a direct list
            if isinstance(response, list):
                return [ScanningProfile.model_validate(item) for item in response]
            raise AcunetixError("Unexpected response structure for list scan profiles. Expected a dictionary with a 'scanning_profiles' key or a direct list.")
        
        items = response.get("scanning_profiles", [])
        return [ScanningProfile.model_validate(item) for item in items]

    def create(self, profile_data: ScanningProfile) -> ScanningProfile: # Return type changed
        """
        Creates a new scan profile.
        Corresponds to POST /scanning_profiles in API.
        API operationId: create_scanning_profile
        Returns the created ScanningProfile object.
        """
        # Exclude read-only fields for creation
        payload = profile_data.model_dump(exclude={"profile_id", "custom"}, exclude_none=True, by_alias=True, mode='json')
        # Removed return_raw_response=True
        response_data = self._client._request("POST", "scanning_profiles", json_data=payload) 
        
        if not isinstance(response_data, dict): 
            raise AcunetixError("Unexpected response type or structure for create scan profile.")
        
        # Assuming the response body directly contains the created profile data
        created_profile = ScanningProfile.model_validate(response_data) # Use model_validate for robust parsing
        return created_profile

    def get(self, profile_id: str) -> ScanningProfile:
        """
        Retrieves a specific scan profile by ID.
        Corresponds to GET /scanning_profiles/{scanning_profile_id} in API.
        API operationId: get_scanning_profile
        """
        response_data = self._client._request("GET", f"scanning_profiles/{profile_id}")
        if not isinstance(response_data, dict): 
            raise AcunetixError("Unexpected response type for get scan profile. Expected a dictionary.")
        return ScanningProfile(**response_data)

    def update(self, profile_id: str, update_data: ScanningProfile) -> None:
        """
        Modifies an existing scan profile.
        Corresponds to PATCH /scanning_profiles/{scanning_profile_id} in API.
        API operationId: update_scanning_profile
        API returns 204 No Content on success.
        """
        # Exclude read-only fields for update
        payload = update_data.model_dump(exclude={"profile_id", "custom"}, exclude_none=True, by_alias=True, mode='json')
        self._client._request("PATCH", f"scanning_profiles/{profile_id}", json_data=payload)
        # No return value as API returns 204

    def delete(self, profile_id: str) -> None:
        """
        Deletes a specific scan profile.
        Corresponds to DELETE /scanning_profiles/{scanning_profile_id} in API.
        API operationId: delete_scanning_profile
        API returns 204 No Content on success.
        """
        self._client._request("DELETE", f"scanning_profiles/{profile_id}")


class ScanProfilesAsyncResource(BaseResource["AcunetixAsyncClient"]):
    """Handles asynchronous operations related to Acunetix scan profiles."""

    async def list(self) -> List[ScanningProfile]:
        """
        Lists scan profiles asynchronously.
        Corresponds to GET /scanning_profiles in API.
        This endpoint does not support pagination or filtering according to the API spec.
        """
        response = await self._client._arequest("GET", "scanning_profiles")

        if not isinstance(response, dict) or "scanning_profiles" not in response:
            if isinstance(response, list):
                return [ScanningProfile.model_validate(item) for item in response]
            raise AcunetixError("Unexpected response structure for list scan profiles. Expected a dictionary with a 'scanning_profiles' key or a direct list.")
            
        items = response.get("scanning_profiles", [])
        return [ScanningProfile.model_validate(item) for item in items]

    async def create(self, profile_data: ScanningProfile) -> ScanningProfile: # Return type changed
        """Creates a new scan profile asynchronously."""
        payload = profile_data.model_dump(exclude={"profile_id", "custom"}, exclude_none=True, by_alias=True, mode='json')
        # Removed return_raw_response=True
        response_data = await self._client._arequest("POST", "scanning_profiles", json_data=payload)

        if not isinstance(response_data, dict): 
            raise AcunetixError("Unexpected response type or structure for create scan profile.")
            
        created_profile = ScanningProfile.model_validate(response_data) # Use model_validate for robust parsing
        return created_profile

    async def get(self, profile_id: str) -> ScanningProfile:
        """Retrieves a specific scan profile by ID asynchronously."""
        response_data = await self._client._arequest("GET", f"scanning_profiles/{profile_id}")
        if not isinstance(response_data, dict): 
            raise AcunetixError("Unexpected response type for get scan profile. Expected a dictionary.")
        return ScanningProfile(**response_data)

    async def update(self, profile_id: str, update_data: ScanningProfile) -> None:
        """Modifies an existing scan profile asynchronously."""
        payload = update_data.model_dump(exclude={"profile_id", "custom"}, exclude_none=True, by_alias=True, mode='json')
        await self._client._arequest("PATCH", f"scanning_profiles/{profile_id}", json_data=payload)

    async def delete(self, profile_id: str) -> None:
        """Deletes a specific scan profile asynchronously."""
        await self._client._arequest("DELETE", f"scanning_profiles/{profile_id}")
