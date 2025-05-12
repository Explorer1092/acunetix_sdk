from typing import List, Optional, Dict, Any, TYPE_CHECKING

from ..models.export import (
    ExportTypesList,
    NewExport,
    Export,
    ExportIdList # Assuming this is the correct model for bulk delete
    # ExportList # Removed as GET /exports endpoint does not exist
)
from .base_resource import BaseResource
from ..errors import AcunetixError

if TYPE_CHECKING:
    from ..client_sync import AcunetixSyncClient
    from ..client_async import AcunetixAsyncClient

class ExportsSyncResource(BaseResource["AcunetixSyncClient"]):
    """Handles synchronous operations related to Acunetix Exports."""

    def list_export_types(self) -> ExportTypesList:
        """
        Lists available export types.
        Corresponds to GET /export_types in API.
        API operationId: get_export_types
        """
        response_data = self._client._request("GET", "export_types")
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for list export types.")
        # The model ExportTypesList uses alias "export_types" for "templates" key from API spec
        return ExportTypesList(**response_data)

    def create_export(self, export_data: NewExport) -> tuple[Export, Optional[str]]:
        """
        Creates a new export.
        Corresponds to POST /exports in API.
        API operationId: export
        Returns the created Export object and the Location header URL if available.
        """
        payload = export_data.model_dump(exclude_none=True, by_alias=True, mode='json')
        raw_response = self._client._request("POST", "exports", json_data=payload, return_raw_response=True)
        
        location_header = None
        if hasattr(raw_response, "headers"):
            location_header = raw_response.headers.get("Location")

        response_data = None
        if hasattr(raw_response, "json"):
             try:
                response_data = raw_response.json()
             except Exception:
                pass
        elif isinstance(raw_response, dict):
            response_data = raw_response
        
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type or structure for create export.")
        
        created_export = Export(**response_data)
        return created_export, location_header

    def get_export(self, export_id: str) -> Export:
        """
        Retrieves a specific export by ID.
        Corresponds to GET /exports/{export_id} in API.
        API operationId: get_export
        """
        response_data = self._client._request("GET", f"exports/{export_id}")
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for get export.")
        return Export(**response_data)

    def delete_export(self, export_id: str) -> None:
        """
        Deletes a specific export.
        Corresponds to DELETE /exports/{export_id} in API.
        API operationId: remove_export
        """
        self._client._request("DELETE", f"exports/{export_id}")
        # API returns 204 No Content

    def delete_many_exports(self, export_ids: List[str]) -> None:
        """
        Deletes multiple exports.
        Corresponds to POST /exports/delete in API.
        API operationId: remove_exports
        Note: API spec says request body is ReportIdList, assuming it's ExportIdList.
        """
        payload = ExportIdList(export_id_list=export_ids)
        self._client._request("POST", "exports/delete", json_data=payload.model_dump(exclude_none=True, by_alias=True, mode='json'))
        # API returns 204 No Content

    # Removed list method as GET /exports endpoint does not exist in the provided API spec.


class ExportsAsyncResource(BaseResource["AcunetixAsyncClient"]):
    """Handles asynchronous operations related to Acunetix Exports."""

    async def list_export_types(self) -> ExportTypesList:
        response_data = await self._client._arequest("GET", "export_types")
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for list export types.")
        return ExportTypesList(**response_data)

    async def create_export(self, export_data: NewExport) -> tuple[Export, Optional[str]]:
        payload = export_data.model_dump(exclude_none=True, by_alias=True, mode='json')
        raw_response = await self._client._arequest("POST", "exports", json_data=payload, return_raw_response=True)

        location_header = None
        if hasattr(raw_response, "headers"):
            location_header = raw_response.headers.get("Location")
        
        response_data = None
        if hasattr(raw_response, "json"):
             try:
                response_data = raw_response.json()
             except Exception:
                pass
        elif isinstance(raw_response, dict):
            response_data = raw_response

        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type or structure for create export.")
            
        created_export = Export(**response_data)
        return created_export, location_header

    async def get_export(self, export_id: str) -> Export:
        response_data = await self._client._arequest("GET", f"exports/{export_id}")
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for get export.")
        return Export(**response_data)

    async def delete_export(self, export_id: str) -> None:
        await self._client._arequest("DELETE", f"exports/{export_id}")

    async def delete_many_exports(self, export_ids: List[str]) -> None:
        payload = ExportIdList(export_id_list=export_ids)
        await self._client._arequest("POST", "exports/delete", json_data=payload.model_dump(exclude_none=True, by_alias=True, mode='json'))

    # Removed list method as GET /exports endpoint does not exist in the provided API spec.
