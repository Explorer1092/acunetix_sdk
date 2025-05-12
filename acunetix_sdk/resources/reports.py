from typing import List, Optional, Dict, Any, TYPE_CHECKING, IO
import io

from ..models.report import Report, ReportCreate, ReportIdList # Updated imports
from ..models.pagination import PaginatedList
from .base_resource import BaseResource
from ..errors import AcunetixError

if TYPE_CHECKING:
    from ..client_sync import AcunetixSyncClient
    from ..client_async import AcunetixAsyncClient

class ReportsSyncResource(BaseResource["AcunetixSyncClient"]):
    """Handles synchronous operations related to Acunetix reports."""

    def list(self, cursor: Optional[str] = None, limit: Optional[int] = None, query: Optional[str] = None, sort: Optional[str] = None) -> PaginatedList[Report]:
        """
        Lists reports.
        Corresponds to GET /reports in API.
        API operationId: get_reports
        """
        params: Dict[str, Any] = {}
        if cursor: params["c"] = cursor
        if limit is not None: params["l"] = limit
        if query: params["q"] = query
        if sort: params["s"] = sort
        response = self._client._request("GET", "reports", params=params)
        if not isinstance(response, dict) or "reports" not in response or "pagination" not in response:
             raise AcunetixError("Unexpected response structure for list reports. Expected 'reports' and 'pagination' keys.")
        return PaginatedList[Report](items=response.get("reports", []), pagination=response.get("pagination", {}))

    def create(self, report_data: ReportCreate) -> tuple[Report, Optional[str]]:
        """
        Generates a new report.
        Corresponds to POST /reports in API.
        API operationId: generate_new_report
        Returns the created Report object and the Location header URL if available.
        """
        payload = report_data.model_dump(exclude_none=True, by_alias=True, mode='json')
        raw_response = self._client._request("POST", "reports", json_data=payload, return_raw_response=True)
        
        location_header = None
        if hasattr(raw_response, "headers"):
            location_header = raw_response.headers.get("Location")

        # Assuming the body of the response is accessible from raw_response if it's a custom object,
        # or if _request with return_raw_response=True still gives parsed body for 201.
        # This part needs to align with how _request behaves.
        # If raw_response is httpx.Response, then raw_response.json() would be the dict.
        # For now, let's assume _request can provide the parsed body even with return_raw_response=True,
        # or that the body is an attribute of raw_response.
        # A safer approach: make _request return (parsed_body, headers_dict)
        
        response_data = None
        if hasattr(raw_response, "json"): # httpx.Response like object
             try:
                response_data = raw_response.json()
             except Exception: # Not JSON or empty
                pass
        elif isinstance(raw_response, dict): # If _request already parsed it
            response_data = raw_response
        
        if not isinstance(response_data, dict): 
            raise AcunetixError("Unexpected response type or structure for create report. Expected a dictionary.")
        
        created_report = Report(**response_data)
        return created_report, location_header

    def get(self, report_id: str) -> Report:
        """
        Retrieves a specific report by ID.
        Corresponds to GET /reports/{report_id} in API.
        API operationId: get_report
        """
        response_data = self._client._request("GET", f"reports/{report_id}")
        if not isinstance(response_data, dict): 
            raise AcunetixError("Unexpected response type for get report. Expected a dictionary.")
        return Report(**response_data)

    def delete(self, report_id: str) -> None:
        """
        Deletes a specific report.
        Corresponds to DELETE /reports/{report_id} in API.
        API operationId: remove_report
        """
        self._client._request("DELETE", f"reports/{report_id}")

    def delete_many(self, report_ids: List[str]) -> None:
        """
        Deletes multiple reports.
        Corresponds to POST /reports/delete in API.
        API operationId: remove_reports
        """
        payload = ReportIdList(report_id_list=report_ids)
        self._client._request("POST", "reports/delete", json_data=payload.model_dump(exclude_none=True, by_alias=True, mode='json'))

    def regenerate(self, report_id: str) -> tuple[Report, Optional[str]]:
        """
        Re-generates a specific report.
        Corresponds to POST /reports/{report_id}/repeat in API.
        API operationId: repeat_report
        Returns the regenerated Report object and the Location header URL if available.
        """
        raw_response = self._client._request("POST", f"reports/{report_id}/repeat", return_raw_response=True)
        
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
            raise AcunetixError("Unexpected response type or structure for regenerate report. Expected a dictionary.")
        
        regenerated_report = Report(**response_data)
        return regenerated_report, location_header

    def download(self, descriptor: str) -> IO[bytes]:
        """
        Downloads a report file using its descriptor.
        The descriptor is typically obtained from the 'download' field of a Report object.
        Corresponds to GET /reports/download/{descriptor} in API.
        API operationId: download_report
        """
        response_content = self._client._request(
            method="GET", 
            path=f"reports/download/{descriptor}",
            expected_response_type="bytes",
            additional_headers={"Accept": "application/octet-stream"} 
        )
        if not isinstance(response_content, bytes):
            raise AcunetixError(f"Expected bytes for report download, got {type(response_content)}")
        return io.BytesIO(response_content)


class ReportsAsyncResource(BaseResource["AcunetixAsyncClient"]):
    """Handles asynchronous operations related to Acunetix reports."""

    async def list(self, cursor: Optional[str] = None, limit: Optional[int] = None, query: Optional[str] = None, sort: Optional[str] = None) -> PaginatedList[Report]:
        """Lists reports asynchronously."""
        params: Dict[str, Any] = {}
        if cursor: params["c"] = cursor
        if limit is not None: params["l"] = limit
        if query: params["q"] = query
        if sort: params["s"] = sort
        response = await self._client._arequest("GET", "reports", params=params)
        if not isinstance(response, dict) or "reports" not in response or "pagination" not in response:
            raise AcunetixError("Unexpected response structure for list reports. Expected 'reports' and 'pagination' keys.")
        return PaginatedList[Report](items=response.get("reports", []), pagination=response.get("pagination", {}))

    async def create(self, report_data: ReportCreate) -> tuple[Report, Optional[str]]:
        """Generates a new report asynchronously."""
        payload = report_data.model_dump(exclude_none=True, by_alias=True, mode='json')
        raw_response = await self._client._arequest("POST", "reports", json_data=payload, return_raw_response=True)
        
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
            raise AcunetixError("Unexpected response type or structure for create report. Expected a dictionary.")
        
        created_report = Report(**response_data)
        return created_report, location_header

    async def get(self, report_id: str) -> Report:
        """Retrieves a specific report by ID asynchronously."""
        response_data = await self._client._arequest("GET", f"reports/{report_id}")
        if not isinstance(response_data, dict): 
            raise AcunetixError("Unexpected response type for get report. Expected a dictionary.")
        return Report(**response_data)

    async def delete(self, report_id: str) -> None:
        """Deletes a specific report asynchronously."""
        await self._client._arequest("DELETE", f"reports/{report_id}")

    async def delete_many(self, report_ids: List[str]) -> None:
        """Deletes multiple reports asynchronously."""
        payload = ReportIdList(report_id_list=report_ids)
        await self._client._arequest("POST", "reports/delete", json_data=payload.model_dump(exclude_none=True, by_alias=True, mode='json'))

    async def regenerate(self, report_id: str) -> tuple[Report, Optional[str]]:
        """Re-generates a specific report asynchronously."""
        raw_response = await self._client._arequest("POST", f"reports/{report_id}/repeat", return_raw_response=True)
        
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
            raise AcunetixError("Unexpected response type or structure for regenerate report. Expected a dictionary.")
        
        regenerated_report = Report(**response_data)
        return regenerated_report, location_header

    async def download(self, descriptor: str) -> IO[bytes]:
        """Downloads a report file using its descriptor asynchronously."""
        response_content = await self._client._arequest(
            method="GET", 
            path=f"reports/download/{descriptor}",
            expected_response_type="bytes",
            additional_headers={"Accept": "application/octet-stream"}
        )
        if not isinstance(response_content, bytes):
            raise AcunetixError(f"Expected bytes for report download, got {type(response_content)}")
        return io.BytesIO(response_content)
