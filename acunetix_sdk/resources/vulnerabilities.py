from typing import List, Optional, Dict, Any, TYPE_CHECKING, IO
import io

from ..models.vulnerability import (
    Vulnerability,
    VulnerabilityDetails,
    VulnerabilityStatus,
    VulnerabilityRecheck,
    VulnerabilitiesRecheck,
    IntegrationsVulnerabilityIdList,
    CreateIssuesViaIntegrationsResponse,
    VulnerabilityGroupsResponse, # Added
    VulnerabilityType,           # Added
    VulnerabilityTypeTargetsCountResponseItem # Added
)
from ..models.pagination import PaginatedList
from .base_resource import BaseResource
from ..errors import AcunetixError

if TYPE_CHECKING:
    from ..client_sync import AcunetixSyncClient
    from ..client_async import AcunetixAsyncClient

class VulnerabilitiesSyncResource(BaseResource["AcunetixSyncClient"]):
    """Handles synchronous operations related to Acunetix vulnerabilities."""

    def list(self, cursor: Optional[str] = None, limit: Optional[int] = None, query: Optional[str] = None, sort: Optional[str] = None) -> PaginatedList[Vulnerability]:
        """
        Lists all vulnerabilities.
        Corresponds to GET /vulnerabilities in API.
        API operationId: get_vulnerabilities
        """
        params: Dict[str, Any] = {}
        if cursor: params["c"] = cursor
        if limit is not None: params["l"] = limit
        if query: params["q"] = query
        if sort: params["s"] = sort
        
        response = self._client._request("GET", "vulnerabilities", params=params)
        if not isinstance(response, dict) or "vulnerabilities" not in response or "pagination" not in response:
             raise AcunetixError("Unexpected response structure for list vulnerabilities. Expected 'vulnerabilities' and 'pagination' keys.")
        return PaginatedList[Vulnerability](items=response.get("vulnerabilities", []), pagination=response.get("pagination", {}))

    def get_details(self, vuln_id: str) -> VulnerabilityDetails:
        """
        Retrieves details for a specific vulnerability.
        Corresponds to GET /vulnerabilities/{vuln_id} in API.
        API operationId: get_vulnerability_details
        """
        response_data = self._client._request("GET", f"vulnerabilities/{vuln_id}")
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for get vulnerability details.")
        return VulnerabilityDetails(**response_data)

    def get_http_response(self, vuln_id: str) -> IO[bytes]:
        """
        Retrieves the HTTP response for a specific vulnerability.
        Corresponds to GET /vulnerabilities/{vuln_id}/http_response in API.
        API operationId: get_vulnerability_http_response
        """
        response_content = self._client._request(
            method="GET",
            path=f"vulnerabilities/{vuln_id}/http_response",
            expected_response_type="bytes",
            additional_headers={"Accept": "application/octet-stream"}
        )
        if not isinstance(response_content, bytes):
            raise AcunetixError(f"Expected bytes for vulnerability HTTP response, got {type(response_content)}")
        return io.BytesIO(response_content)

    def recheck(self, vuln_id: str, recheck_data: VulnerabilityRecheck) -> Optional[str]:
        """
        Re-checks a specific vulnerability.
        Corresponds to PUT /vulnerabilities/{vuln_id}/recheck in API.
        API operationId: recheck_vulnerability
        Returns the Location header (URL of the new scan) if provided by the API, otherwise None.
        """
        payload = recheck_data.model_dump(exclude_none=True, by_alias=True, mode='json')
        # Assuming _request can return headers or the full response object
        # For simplicity, let's assume _request is modified to return a tuple (body, headers)
        # or the client object has a way to access last response headers.
        # This is a placeholder for how one might get headers.
        # response_headers = self._client.last_response_headers 
        # For now, we'll assume the _request method itself is enhanced or we can't get headers easily.
        # If _request returns the raw response object:
        raw_response = self._client._request("PUT", f"vulnerabilities/{vuln_id}/recheck", json_data=payload, return_raw_response=True)
        if hasattr(raw_response, "headers"):
            return raw_response.headers.get("Location")
        return None

    def recheck_many(self, recheck_data: VulnerabilitiesRecheck) -> None:
        """
        Re-checks a list of vulnerabilities.
        Corresponds to PUT /vulnerabilities/recheck in API.
        API operationId: recheck_vulnerabilities
        """
        payload = recheck_data.model_dump(exclude_none=True, by_alias=True, mode='json')
        self._client._request("PUT", "vulnerabilities/recheck", json_data=payload)
        # API returns 204 No Content

    def update_status(self, vuln_id: str, status_data: VulnerabilityStatus) -> None:
        """
        Updates the status of a specific vulnerability.
        Corresponds to PUT /vulnerabilities/{vuln_id}/status in API.
        API operationId: set_vulnerability_status
        """
        payload = status_data.model_dump(exclude_none=True, by_alias=True, mode='json')
        self._client._request("PUT", f"vulnerabilities/{vuln_id}/status", json_data=payload)
        # API returns 204 No Content

    def create_issues_in_tracker(self, issue_data: IntegrationsVulnerabilityIdList) -> CreateIssuesViaIntegrationsResponse:
        """
        Schedules the creation of issues on an issue tracker for given vulnerabilities.
        Corresponds to POST /vulnerabilities/issues in API.
        API operationId: create_vulnerability_issues
        """
        payload = issue_data.model_dump(exclude_none=True, by_alias=True, mode='json')
        response_data = self._client._request("POST", "vulnerabilities/issues", json_data=payload)
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for create issues in tracker.")
        return CreateIssuesViaIntegrationsResponse(**response_data)

    def get_vulnerability_by_id(self, vuln_id: str) -> VulnerabilityDetails: # Same as get_details but for clarity with API path
        """
        Retrieves details for a specific vulnerability by its standalone ID.
        Corresponds to GET /scan_vulnerabilities/{vuln_id} in API. (Note: API path uses scan_vulnerabilities)
        API operationId: get_scan_vulnerability_detail_from_vuln_id
        """
        # The API path is /scan_vulnerabilities/{vuln_id}, not /vulnerabilities/{vuln_id} for this specific operationId
        response_data = self._client._request("GET", f"scan_vulnerabilities/{vuln_id}")
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for get_vulnerability_by_id.")
        return VulnerabilityDetails(**response_data)

    # --- Vulnerability Groups and Types ---
    def list_groups(self, group_by: Optional[str] = "fqdn", query: Optional[str] = None, sort: Optional[str] = None) -> VulnerabilityGroupsResponse: # No model_dump here
        """
        Lists vulnerability groups.
        Corresponds to GET /vulnerability_groups in API.
        API operationId: get_vulnerability_groups
        """
        params: Dict[str, Any] = {}
        if group_by: params["group_by"] = group_by # Enum: fqdn, target
        if query: params["q"] = query
        if sort: params["s"] = sort

        response_data = self._client._request("GET", "vulnerability_groups", params=params)
        if not isinstance(response_data, dict): # API returns VulnerabilityGroupsResponse directly
            raise AcunetixError("Unexpected response type for list vulnerability groups.")
        return VulnerabilityGroupsResponse(**response_data)

    def list_types(self, cursor: Optional[str] = None, limit: Optional[int] = None, view: Optional[str] = "default", query: Optional[str] = None, sort: Optional[str] = None) -> PaginatedList[VulnerabilityTypeTargetsCountResponseItem]:
        """
        Lists vulnerability types.
        Corresponds to GET /vulnerability_types in API.
        API operationId: get_vulnerability_types
        """
        params: Dict[str, Any] = {}
        if cursor: params["c"] = cursor
        if limit is not None: params["l"] = limit
        if view: params["v"] = view # Enum: criticality, default
        if query: params["q"] = query
        if sort: params["s"] = sort

        response_data = self._client._request("GET", "vulnerability_types", params=params)
        # API returns VulnerabilityTypeTargetsCountResponse which has "vulnerability_types" and "pagination"
        if not isinstance(response_data, dict) or "vulnerability_types" not in response_data or "pagination" not in response_data:
            raise AcunetixError("Unexpected response structure for list vulnerability types.")
        return PaginatedList[VulnerabilityTypeTargetsCountResponseItem](items=response_data.get("vulnerability_types", []), pagination=response_data.get("pagination", {}))

    def get_type_details(self, vt_id: str) -> VulnerabilityType:
        """
        Retrieves details for a specific vulnerability type.
        Corresponds to GET /vulnerability_types/{vt_id} in API.
        API operationId: get_vulnerability_type
        """
        response_data = self._client._request("GET", f"vulnerability_types/{vt_id}")
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for get vulnerability type details.")
        return VulnerabilityType(**response_data)


class VulnerabilitiesAsyncResource(BaseResource["AcunetixAsyncClient"]):
    """Handles asynchronous operations related to Acunetix vulnerabilities."""

    async def list(self, cursor: Optional[str] = None, limit: Optional[int] = None, query: Optional[str] = None, sort: Optional[str] = None) -> PaginatedList[Vulnerability]:
        params: Dict[str, Any] = {}
        if cursor: params["c"] = cursor
        if limit is not None: params["l"] = limit
        if query: params["q"] = query
        if sort: params["s"] = sort
        response = await self._client._arequest("GET", "vulnerabilities", params=params)
        if not isinstance(response, dict) or "vulnerabilities" not in response or "pagination" not in response:
             raise AcunetixError("Unexpected response structure for list vulnerabilities.")
        return PaginatedList[Vulnerability](items=response.get("vulnerabilities", []), pagination=response.get("pagination", {}))

    async def get_details(self, vuln_id: str) -> VulnerabilityDetails:
        response_data = await self._client._arequest("GET", f"vulnerabilities/{vuln_id}")
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for get vulnerability details.")
        return VulnerabilityDetails(**response_data)

    async def get_http_response(self, vuln_id: str) -> IO[bytes]:
        response_content = await self._client._arequest(
            method="GET",
            path=f"vulnerabilities/{vuln_id}/http_response",
            expected_response_type="bytes",
            additional_headers={"Accept": "application/octet-stream"}
        )
        if not isinstance(response_content, bytes):
            raise AcunetixError(f"Expected bytes for vulnerability HTTP response, got {type(response_content)}")
        return io.BytesIO(response_content)

    async def recheck(self, vuln_id: str, recheck_data: VulnerabilityRecheck) -> Optional[str]:
        payload = recheck_data.model_dump(exclude_none=True, by_alias=True, mode='json')
        raw_response = await self._client._arequest("PUT", f"vulnerabilities/{vuln_id}/recheck", json_data=payload, return_raw_response=True)
        if hasattr(raw_response, "headers"):
            return raw_response.headers.get("Location")
        return None

    async def recheck_many(self, recheck_data: VulnerabilitiesRecheck) -> None:
        payload = recheck_data.model_dump(exclude_none=True, by_alias=True, mode='json')
        await self._client._arequest("PUT", "vulnerabilities/recheck", json_data=payload)

    async def update_status(self, vuln_id: str, status_data: VulnerabilityStatus) -> None:
        payload = status_data.model_dump(exclude_none=True, by_alias=True, mode='json')
        await self._client._arequest("PUT", f"vulnerabilities/{vuln_id}/status", json_data=payload)

    async def create_issues_in_tracker(self, issue_data: IntegrationsVulnerabilityIdList) -> CreateIssuesViaIntegrationsResponse:
        payload = issue_data.model_dump(exclude_none=True, by_alias=True, mode='json')
        response_data = await self._client._arequest("POST", "vulnerabilities/issues", json_data=payload)
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for create issues in tracker.")
        return CreateIssuesViaIntegrationsResponse(**response_data)

    async def get_vulnerability_by_id(self, vuln_id: str) -> VulnerabilityDetails:
        """Retrieves details for a specific vulnerability by its standalone ID asynchronously."""
        response_data = await self._client._arequest("GET", f"scan_vulnerabilities/{vuln_id}")
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for get_vulnerability_by_id.")
        return VulnerabilityDetails(**response_data)

    # --- Vulnerability Groups and Types ---
    async def list_groups(self, group_by: Optional[str] = "fqdn", query: Optional[str] = None, sort: Optional[str] = None) -> VulnerabilityGroupsResponse:
        params: Dict[str, Any] = {}
        if group_by: params["group_by"] = group_by
        if query: params["q"] = query
        if sort: params["s"] = sort
        response_data = await self._client._arequest("GET", "vulnerability_groups", params=params)
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for list vulnerability groups.")
        return VulnerabilityGroupsResponse(**response_data)

    async def list_types(self, cursor: Optional[str] = None, limit: Optional[int] = None, view: Optional[str] = "default", query: Optional[str] = None, sort: Optional[str] = None) -> PaginatedList[VulnerabilityTypeTargetsCountResponseItem]:
        params: Dict[str, Any] = {}
        if cursor: params["c"] = cursor
        if limit is not None: params["l"] = limit
        if view: params["v"] = view
        if query: params["q"] = query
        if sort: params["s"] = sort
        response_data = await self._client._arequest("GET", "vulnerability_types", params=params)
        if not isinstance(response_data, dict) or "vulnerability_types" not in response_data or "pagination" not in response_data:
            raise AcunetixError("Unexpected response structure for list vulnerability types.")
        return PaginatedList[VulnerabilityTypeTargetsCountResponseItem](items=response_data.get("vulnerability_types", []), pagination=response_data.get("pagination", {}))

    async def get_type_details(self, vt_id: str) -> VulnerabilityType:
        response_data = await self._client._arequest("GET", f"vulnerability_types/{vt_id}")
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for get vulnerability type details.")
        return VulnerabilityType(**response_data)
