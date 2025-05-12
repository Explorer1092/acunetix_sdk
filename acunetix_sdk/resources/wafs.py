from typing import Optional, TYPE_CHECKING

from ..models.waf import (
    WAFsList,
    WAFEntry,
    WAFConfig, # For the check_connection_new helper
    WAFConnectionStatus
)
# Pagination is not specified for the main list.
from .base_resource import BaseResource
from ..errors import AcunetixError

if TYPE_CHECKING:
    from ..client_sync import AcunetixSyncClient
    from ..client_async import AcunetixAsyncClient

class WafsSyncResource(BaseResource["AcunetixSyncClient"]):
    """Handles synchronous operations related to Acunetix WAFs."""

    def check_connection_new(self, config_data: WAFConfig) -> WAFConnectionStatus:
        """
        Tests connection to a new (unsaved) WAF configuration.
        Corresponds to POST /wafs/check_connection in API.
        NOTE: API documentation has an operationId conflict for 'check_connection' 
              (also used by POST /issue_trackers/check_connection).
        """
        payload = config_data.model_dump(exclude_none=True, by_alias=True, mode='json')
        response_data = self._client._request("POST", "wafs/check_connection", json_data=payload)
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for WAF check_connection_new.")
        return WAFConnectionStatus(**response_data)

    def list(self) -> WAFsList:
        """
        Lists all configured WAFs.
        Corresponds to GET /wafs in API.
        API operationId: get_wafs
        """
        response_data = self._client._request("GET", "wafs")
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for list WAFs.")
        return WAFsList(**response_data)

    def create(self, entry_data: WAFEntry) -> WAFEntry: # API returns 200 OK, assuming it returns the object
        """
        Creates a new WAF entry.
        Corresponds to POST /wafs in API.
        API operationId: create_waf_entry
        NOTE: API documentation specifies a 200 OK response with description "WAF created",
              but does not define a response body schema. This implementation assumes
              the created WAFEntry object is returned, which needs verification.
        """
        # For POST, waf_id should not be sent.
        payload = entry_data.model_dump(exclude={"waf_id"}, exclude_none=True, by_alias=True, mode='json')
        response_data = self._client._request("POST", "wafs", json_data=payload)
        # If API indeed returns no body or an empty body for 200 OK,
        # this part needs adjustment. For now, assume it returns the object.
        if not isinstance(response_data, dict):
            # Consider raising an error or returning a default/empty WAFEntry if no body is expected/returned.
            # For now, we proceed assuming a dict is returned.
            pass
        return WAFEntry(**response_data)

    def get(self, waf_id: str) -> WAFEntry:
        """
        Retrieves a specific WAF entry by ID.
        Corresponds to GET /wafs/{waf_id} in API.
        API operationId: get_waf_entry
        """
        response_data = self._client._request("GET", f"wafs/{waf_id}")
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for get WAF entry.")
        return WAFEntry(**response_data)

    def update(self, waf_id: str, entry_data: WAFEntry) -> None: # API returns 204
        """
        Modifies an existing WAF entry.
        Corresponds to PATCH /wafs/{waf_id} in API.
        API operationId: update_waf_entry
        """
        # For PATCH, waf_id should not be in the payload.
        payload = entry_data.model_dump(exclude={"waf_id"}, exclude_none=True, by_alias=True, mode='json')
        self._client._request("PATCH", f"wafs/{waf_id}", json_data=payload)
        # API returns 204 No Content

    def delete(self, waf_id: str) -> None: # API returns 204
        """
        Deletes a specific WAF entry.
        Corresponds to DELETE /wafs/{waf_id} in API.
        API operationId: delete_waf_entry
        """
        self._client._request("DELETE", f"wafs/{waf_id}")

    def check_connection(self, waf_id: str) -> WAFConnectionStatus:
        """
        Tests connection for an existing WAF entry.
        Corresponds to GET /wafs/{waf_id}/check_connection in API.
        API operationId: waf_entry_check_connection
        """
        response_data = self._client._request("GET", f"wafs/{waf_id}/check_connection")
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for WAF check_connection.")
        return WAFConnectionStatus(**response_data)


class WafsAsyncResource(BaseResource["AcunetixAsyncClient"]):
    """Handles asynchronous operations related to Acunetix WAFs."""

    async def check_connection_new(self, config_data: WAFConfig) -> WAFConnectionStatus:
        """
        Tests connection to a new (unsaved) WAF configuration asynchronously.
        Corresponds to POST /wafs/check_connection in API.
        NOTE: API documentation has an operationId conflict for 'check_connection' 
              (also used by POST /issue_trackers/check_connection).
        """
        payload = config_data.model_dump(exclude_none=True, by_alias=True, mode='json')
        response_data = await self._client._arequest("POST", "wafs/check_connection", json_data=payload)
        if not isinstance(response_data, dict):
            raise AcunetixError("Async: Unexpected response for WAF check_connection_new.")
        return WAFConnectionStatus(**response_data)

    async def list(self) -> WAFsList:
        response_data = await self._client._arequest("GET", "wafs")
        if not isinstance(response_data, dict):
            raise AcunetixError("Async: Unexpected response for list WAFs.")
        return WAFsList(**response_data)

    async def create(self, entry_data: WAFEntry) -> WAFEntry:
        """
        Creates a new WAF entry asynchronously.
        Corresponds to POST /wafs in API.
        API operationId: create_waf_entry
        NOTE: API documentation specifies a 200 OK response with description "WAF created",
              but does not define a response body schema. This implementation assumes
              the created WAFEntry object is returned, which needs verification.
        """
        payload = entry_data.model_dump(exclude={"waf_id"}, exclude_none=True, by_alias=True, mode='json')
        response_data = await self._client._arequest("POST", "wafs", json_data=payload)
        if not isinstance(response_data, dict):
            # Consider raising an error or returning a default/empty WAFEntry if no body is expected/returned.
            pass
        return WAFEntry(**response_data)

    async def get(self, waf_id: str) -> WAFEntry:
        response_data = await self._client._arequest("GET", f"wafs/{waf_id}")
        if not isinstance(response_data, dict):
            raise AcunetixError("Async: Unexpected response for get WAF entry.")
        return WAFEntry(**response_data)

    async def update(self, waf_id: str, entry_data: WAFEntry) -> None:
        payload = entry_data.model_dump(exclude={"waf_id"}, exclude_none=True, by_alias=True, mode='json')
        await self._client._arequest("PATCH", f"wafs/{waf_id}", json_data=payload)

    async def delete(self, waf_id: str) -> None:
        await self._client._arequest("DELETE", f"wafs/{waf_id}")

    async def check_connection(self, waf_id: str) -> WAFConnectionStatus:
        response_data = await self._client._arequest("GET", f"wafs/{waf_id}/check_connection")
        if not isinstance(response_data, dict):
            raise AcunetixError("Async: Unexpected response for WAF check_connection.")
        return WAFConnectionStatus(**response_data)
