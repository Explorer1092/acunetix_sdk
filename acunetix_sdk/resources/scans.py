from typing import List, Optional, Dict, Any, TYPE_CHECKING

from ..models.scan import (
    ScanResponse, 
    ScanCreateRequest, 
    ScanUpdateRequest,
    ScanResultItemResponse
)
from ..models.vulnerability import (
    Vulnerability, VulnerabilityTypeSessionsCountResponseItem, VulnerabilityType,
    VulnerabilityDetails, VulnerabilityStatus, VulnerabilityRecheck, VulnerabilitiesRecheck
)
from ..models.pagination import PaginatedList
from .base_resource import BaseResource
from ..errors import AcunetixError
from ..models.target import Technology

if TYPE_CHECKING:
    from ..client_sync import AcunetixSyncClient
    from ..client_async import AcunetixAsyncClient

class ScansSyncResource(BaseResource["AcunetixSyncClient"]):
    """Handles synchronous operations related to Acunetix scans."""

    def list(self, target_id: Optional[str] = None, cursor: Optional[str] = None, limit: Optional[int] = None, query: Optional[str] = None, sort: Optional[str] = None) -> PaginatedList[ScanResponse]:
        """
        Lists scans.
        Corresponds to GET /scans in API.
        API operationId: get_scans
        """
        params: Dict[str, Any] = {}
        
        # Construct query string
        query_parts = []
        if target_id:
            query_parts.append(f"target_id:{target_id}")
        if query: # Append user-provided query if exists
            query_parts.append(query)
        
        final_query = ";".join(query_parts)
        if final_query:
            params["q"] = final_query
            
        if cursor: params["c"] = cursor
        if limit is not None: params["l"] = limit
        if sort: params["s"] = sort
        
        response = self._client._request("GET", "scans", params=params)
        if not isinstance(response, dict) or "scans" not in response or "pagination" not in response:
             raise AcunetixError("Unexpected response structure for list scans. Expected 'scans' and 'pagination' keys.")
        return PaginatedList[ScanResponse](items=response.get("scans", []), pagination=response.get("pagination", {}))

    def create(self, scan_data: ScanCreateRequest) -> ScanResponse:
        """
        Schedules a new scan.
        Corresponds to POST /scans in API.
        API operationId: schedule_scan
        """
        payload = scan_data.model_dump(exclude_none=True, by_alias=True, mode='json')
        response_data = self._client._request("POST", "scans", json_data=payload)
        if not isinstance(response_data, dict): 
            raise AcunetixError("Unexpected response type for create scan. Expected a dictionary.")
        return ScanResponse(**response_data) # API returns ScanItemResponse

    def get(self, scan_id: str) -> ScanResponse:
        """
        Retrieves a specific scan by ID.
        Corresponds to GET /scans/{scan_id} in API.
        API operationId: get_scan
        """
        response_data = self._client._request("GET", f"scans/{scan_id}")
        if not isinstance(response_data, dict): 
            raise AcunetixError("Unexpected response type for get scan. Expected a dictionary.")
        return ScanResponse(**response_data) # API returns ScanItemResponse

    def update(self, scan_id: str, scan_data: ScanUpdateRequest) -> None:
        """
        Modifies an existing scan.
        Corresponds to PATCH /scans/{scan_id} in API.
        API operationId: update_scan
        """
        payload = scan_data.model_dump(exclude_none=True, by_alias=True, mode='json')
        self._client._request("PATCH", f"scans/{scan_id}", json_data=payload)
        # API returns 204 No Content

    def delete(self, scan_id: str) -> None:
        """
        Deletes a specific scan.
        Corresponds to DELETE /scans/{scan_id} in API.
        API operationId: remove_scan
        """
        self._client._request("DELETE", f"scans/{scan_id}") # API returns 204 No Content

    def abort(self, scan_id: str) -> None:
        """
        Aborts a running scan.
        Corresponds to POST /scans/{scan_id}/abort in API.
        API operationId: abort_scan
        """
        self._client._request("POST", f"scans/{scan_id}/abort") # API returns 204 No Content

    def resume(self, scan_id: str) -> None:
        """
        Resumes a paused scan.
        Corresponds to POST /scans/{scan_id}/resume in API.
        API operationId: resume_scan
        """
        self._client._request("POST", f"scans/{scan_id}/resume") # API returns 204 No Content
    
    def trigger(self, scan_id: str) -> None:
        """
        Triggers a new scan session for an existing scan.
        Corresponds to POST /scans/{scan_id}/trigger in API.
        API operationId: trigger_scan
        """
        self._client._request("POST", f"scans/{scan_id}/trigger") # API returns 204 No Content

    def get_results(self, scan_id: str, cursor: Optional[str] = None, limit: Optional[int] = None, sort: Optional[str] = None) -> PaginatedList[ScanResultItemResponse]:
        """
        Retrieves the result history for a specific scan.
        Corresponds to GET /scans/{scan_id}/results in API.
        API operationId: get_scan_result_history
        """
        params: Dict[str, Any] = {}
        if cursor: params["c"] = cursor
        if limit is not None: params["l"] = limit
        if sort: params["s"] = sort
        
        response = self._client._request("GET", f"scans/{scan_id}/results", params=params)
        if not isinstance(response, dict) or "results" not in response or "pagination" not in response:
            raise AcunetixError("Unexpected response structure for get scan results. Expected 'results' and 'pagination' keys.")
        return PaginatedList[ScanResultItemResponse](items=response.get("results", []), pagination=response.get("pagination", {}))

    def get_vulnerabilities(self, scan_id: str, result_id: str, cursor: Optional[str] = None, limit: Optional[int] = None, query: Optional[str] = None, sort: Optional[str] = None) -> PaginatedList[Vulnerability]:
        """
        Gets vulnerabilities for a specific scan result (session).
        Corresponds to GET /scans/{scan_id}/results/{result_id}/vulnerabilities in API.
        API operationId: get_scan_vulnerabilities
        """
        params: Dict[str, Any] = {}
        if cursor: params["c"] = cursor
        if limit is not None: params["l"] = limit
        if query: params["q"] = query
        if sort: params["s"] = sort
        
        api_path = f"scans/{scan_id}/results/{result_id}/vulnerabilities"
        response = self._client._request("GET", api_path, params=params)
        if not isinstance(response, dict) or "vulnerabilities" not in response or "pagination" not in response:
            raise AcunetixError("Unexpected response structure for get vulnerabilities. Expected 'vulnerabilities' and 'pagination' keys.")
        return PaginatedList[Vulnerability](items=response.get("vulnerabilities", []), pagination=response.get("pagination", {}))

    def get_result_by_id(self, result_id: str) -> ScanResultItemResponse:
        """
        Retrieves a specific scan result by its standalone ID.
        Corresponds to GET /results/{result_id} in API.
        API operationId: get_scan_result
        """
        response_data = self._client._request("GET", f"results/{result_id}")
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for get_result_by_id.")
        return ScanResultItemResponse(**response_data)

    # --- Scan Result Crawl Data and Statistics ---
    def search_crawl_data(
        self,
        scan_id: str,
        result_id: str,
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
        query: Optional[str] = None,
        sort: Optional[str] = None,
    ) -> PaginatedList[Dict[str, Any]]:
        """Search crawl data for a given scan result.

        对应 GET /scans/{scan_id}/results/{result_id}/crawldata
        API operationId: search_crawl_data
        如果 API 返回 302，底层 http_client 会自动跟随重定向并返回列表。
        """
        params: Dict[str, Any] = {}
        if cursor: params["c"] = cursor
        if limit is not None: params["l"] = limit
        if query: params["q"] = query
        if sort: params["s"] = sort

        response = self._client._request(
            "GET",
            f"scans/{scan_id}/results/{result_id}/crawldata",
            params=params,
        )
        if not isinstance(response, dict) or "locations" not in response or "pagination" not in response:
            raise AcunetixError("Unexpected response structure for search_crawl_data. Expected 'locations' and 'pagination' keys.")
        return PaginatedList[Dict[str, Any]](items=response.get("locations", []), pagination=response.get("pagination", {}))

    def get_crawl_location_details(self, scan_id: str, result_id: str, loc_id: int) -> Dict[str, Any]:
        """Retrieve details for a specific crawl location."""
        response = self._client._request(
            "GET",
            f"scans/{scan_id}/results/{result_id}/crawldata/{loc_id}",
        )
        if not isinstance(response, dict):
            raise AcunetixError("Unexpected response type for get_crawl_location_details.")
        return response

    def get_crawl_location_children(
        self,
        scan_id: str,
        result_id: str,
        loc_id: int,
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
        sort: Optional[str] = None,
    ) -> PaginatedList[Dict[str, Any]]:
        """List child crawl locations of a given location."""
        params: Dict[str, Any] = {}
        if cursor: params["c"] = cursor
        if limit is not None: params["l"] = limit
        if sort: params["s"] = sort
        response = self._client._request(
            "GET",
            f"scans/{scan_id}/results/{result_id}/crawldata/{loc_id}/children",
            params=params,
        )
        if not isinstance(response, dict) or "locations" not in response or "pagination" not in response:
            raise AcunetixError("Unexpected response structure for get_crawl_location_children.")
        return PaginatedList[Dict[str, Any]](items=response.get("locations", []), pagination=response.get("pagination", {}))

    def get_crawl_location_vulnerabilities(
        self,
        scan_id: str,
        result_id: str,
        loc_id: int,
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
        sort: Optional[str] = None,
    ) -> PaginatedList[Vulnerability]:
        """List vulnerabilities for a specific crawl location."""
        params: Dict[str, Any] = {}
        if cursor: params["c"] = cursor
        if limit is not None: params["l"] = limit
        if sort: params["s"] = sort
        response = self._client._request(
            "GET",
            f"scans/{scan_id}/results/{result_id}/crawldata/{loc_id}/vulnerabilities",
            params=params,
        )
        if not isinstance(response, dict) or "vulnerabilities" not in response or "pagination" not in response:
            raise AcunetixError("Unexpected response structure for get_crawl_location_vulnerabilities.")
        return PaginatedList[Vulnerability](items=response.get("vulnerabilities", []), pagination=response.get("pagination", {}))

    def get_statistics(self, scan_id: str, result_id: str) -> Dict[str, Any]:
        """Retrieve statistics for a scan result.

        对应 GET /scans/{scan_id}/results/{result_id}/statistics
        API operationId: get_statistics
        """
        response = self._client._request(
            "GET",
            f"scans/{scan_id}/results/{result_id}/statistics",
        )
        if not isinstance(response, dict):
            raise AcunetixError("Unexpected response type for get_statistics.")
        return response

    def list_result_technologies(
        self,
        scan_id: str,
        result_id: str,
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
        query: Optional[str] = None,
        sort: Optional[str] = None,
    ) -> PaginatedList[Technology]:
        """List technologies found in a specific scan session.

        对应 GET /scans/{scan_id}/results/{result_id}/technologies
        API operationId: get_scan_technologies
        """
        params: Dict[str, Any] = {}
        if cursor: params["c"] = cursor
        if limit is not None: params["l"] = limit
        if query: params["q"] = query
        if sort: params["s"] = sort
        response = self._client._request("GET", f"scans/{scan_id}/results/{result_id}/technologies", params=params)
        if not isinstance(response, dict) or "technologies" not in response or "pagination" not in response:
            raise AcunetixError("Unexpected response structure for list_result_technologies.")
        return PaginatedList[Technology](items=response.get("technologies", []), pagination=response.get("pagination", {}))

    def list_result_technology_location_vulnerabilities(
        self,
        scan_id: str,
        result_id: str,
        tech_id: str,
        loc_id: int,
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
        query: Optional[str] = None,
        sort: Optional[str] = None,
    ) -> PaginatedList[Vulnerability]:
        """List vulnerabilities for a technology at a specific location within a scan session."""
        params: Dict[str, Any] = {}
        if cursor: params["c"] = cursor
        if limit is not None: params["l"] = limit
        if query: params["q"] = query
        if sort: params["s"] = sort
        path = f"scans/{scan_id}/results/{result_id}/technologies/{tech_id}/locations/{loc_id}/vulnerabilities"
        response = self._client._request("GET", path, params=params)
        if not isinstance(response, dict) or "vulnerabilities" not in response or "pagination" not in response:
            raise AcunetixError("Unexpected response structure for list_result_technology_location_vulnerabilities.")
        return PaginatedList[Vulnerability](items=response.get("vulnerabilities", []), pagination=response.get("pagination", {}))

    def list_result_vulnerability_types(
        self,
        scan_id: str,
        result_id: str,
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
        query: Optional[str] = None,
        sort: Optional[str] = None,
    ) -> PaginatedList[VulnerabilityTypeSessionsCountResponseItem]:
        """List vulnerability types encountered in a scan session."""
        params: Dict[str, Any] = {}
        if cursor: params["c"] = cursor
        if limit is not None: params["l"] = limit
        if query: params["q"] = query
        if sort: params["s"] = sort
        path = f"scans/{scan_id}/results/{result_id}/vulnerability_types"
        response = self._client._request("GET", path, params=params)
        if not isinstance(response, dict) or "vulnerability_types" not in response or "pagination" not in response:
            raise AcunetixError("Unexpected response structure for list_result_vulnerability_types.")
        return PaginatedList[VulnerabilityTypeSessionsCountResponseItem](items=response.get("vulnerability_types", []), pagination=response.get("pagination", {}))

    def get_scan_vulnerability_detail(self, scan_id: str, result_id: str, vuln_id: str) -> VulnerabilityDetails:
        """
        获取特定扫描会话中漏洞的详细信息。
        对应 GET /scans/{scan_id}/results/{result_id}/vulnerabilities/{vuln_id}
        API operationId: get_scan_vulnerability_detail
        """
        path = f"scans/{scan_id}/results/{result_id}/vulnerabilities/{vuln_id}"
        response_data = self._client._request("GET", path)
        if not isinstance(response_data, dict):
            raise AcunetixError("获取扫描漏洞详情时返回了意外的响应类型。")
        return VulnerabilityDetails(**response_data)

    def get_scan_vulnerability_http_response(self, scan_id: str, result_id: str, vuln_id: str) -> bytes:
        """
        获取漏洞的 HTTP 响应。
        对应 GET /scans/{scan_id}/results/{result_id}/vulnerabilities/{vuln_id}/http_response
        API operationId: get_scan_session_vulnerability_http_response
        """
        path = f"scans/{scan_id}/results/{result_id}/vulnerabilities/{vuln_id}/http_response"
        # 假设 _request 方法可以处理原始字节响应
        response = self._client._request("GET", path, expect_json=False)
        if not isinstance(response, bytes):
            raise AcunetixError("获取漏洞 HTTP 响应时返回了意外的响应类型。")
        return response

    def set_scan_vulnerability_status(self, scan_id: str, result_id: str, vuln_id: str, status_data: VulnerabilityStatus) -> None:
        """
        更新漏洞状态。
        对应 PUT /scans/{scan_id}/results/{result_id}/vulnerabilities/{vuln_id}/status
        API operationId: set_scan_session_vulnerability_status
        """
        path = f"scans/{scan_id}/results/{result_id}/vulnerabilities/{vuln_id}/status"
        self._client._request("PUT", path, json_data=status_data.model_dump(exclude_none=True, by_alias=True, mode='json'))
        # API 返回 204 No Content

    def recheck_scan_vulnerability(self, scan_id: str, result_id: str, vuln_id: str, recheck_data: VulnerabilityRecheck) -> None:
        """
        重检单个漏洞。
        对应 PUT /scans/{scan_id}/results/{result_id}/vulnerabilities/{vuln_id}/recheck
        API operationId: recheck_scan_session_vulnerability
        """
        path = f"scans/{scan_id}/results/{result_id}/vulnerabilities/{vuln_id}/recheck"
        # API 文档显示 201 Created 并带有 Location header，但 SDK 通常不直接处理 header
        self._client._request("PUT", path, json_data=recheck_data.model_dump(exclude_none=True, by_alias=True, mode='json'))

    def recheck_scan_vulnerabilities(self, scan_id: str, result_id: str, recheck_data: VulnerabilitiesRecheck) -> None:
        """
        重检多个漏洞。
        对应 POST /scans/{scan_id}/results/{result_id}/vulnerabilities/recheck
        API operationId: recheck_scan_session_vulnerabilities
        """
        path = f"scans/{scan_id}/results/{result_id}/vulnerabilities/recheck"
        self._client._request("POST", path, json_data=recheck_data.model_dump(exclude_none=True, by_alias=True, mode='json'))
        # API 返回 204 No Content

    def get_scan_vulnerability_detail_by_vuln_id(self, vuln_id: str) -> VulnerabilityDetails:
        """
        通过漏洞 ID 获取漏洞详情，无需 scan_id 和 result_id。
        对应 GET /scan_vulnerabilities/{vuln_id}
        API operationId: get_scan_vulnerability_detail_from_vuln_id
        """
        path = f"scan_vulnerabilities/{vuln_id}"
        response_data = self._client._request("GET", path)
        if not isinstance(response_data, dict):
            raise AcunetixError("通过 vuln_id 获取扫描漏洞详情时返回了意外的响应类型。")
        return VulnerabilityDetails(**response_data)


class ScansAsyncResource(BaseResource["AcunetixAsyncClient"]):
    """Handles asynchronous operations related to Acunetix scans."""

    async def list(self, target_id: Optional[str] = None, cursor: Optional[str] = None, limit: Optional[int] = None, query: Optional[str] = None, sort: Optional[str] = None) -> PaginatedList[ScanResponse]:
        params: Dict[str, Any] = {}
        query_parts = []
        if target_id: query_parts.append(f"target_id:{target_id}")
        if query: query_parts.append(query)
        final_query = ";".join(query_parts)
        if final_query: params["q"] = final_query
        if cursor: params["c"] = cursor
        if limit is not None: params["l"] = limit
        if sort: params["s"] = sort
        response = await self._client._arequest("GET", "scans", params=params)
        if not isinstance(response, dict) or "scans" not in response or "pagination" not in response:
            raise AcunetixError("Unexpected response structure for list scans.")
        return PaginatedList[ScanResponse](items=response.get("scans", []), pagination=response.get("pagination", {}))

    async def create(self, scan_data: ScanCreateRequest) -> ScanResponse:
        payload = scan_data.model_dump(exclude_none=True, by_alias=True, mode='json')
        response_data = await self._client._arequest("POST", "scans", json_data=payload)
        if not isinstance(response_data, dict): 
            raise AcunetixError("Unexpected response type for create scan.")
        return ScanResponse(**response_data)

    async def get(self, scan_id: str) -> ScanResponse:
        response_data = await self._client._arequest("GET", f"scans/{scan_id}")
        if not isinstance(response_data, dict): 
            raise AcunetixError("Unexpected response type for get scan.")
        return ScanResponse(**response_data)

    async def update(self, scan_id: str, scan_data: ScanUpdateRequest) -> None:
        payload = scan_data.model_dump(exclude_none=True, by_alias=True, mode='json')
        await self._client._arequest("PATCH", f"scans/{scan_id}", json_data=payload)

    async def delete(self, scan_id: str) -> None:
        await self._client._arequest("DELETE", f"scans/{scan_id}")

    async def abort(self, scan_id: str) -> None:
        await self._client._arequest("POST", f"scans/{scan_id}/abort")

    async def resume(self, scan_id: str) -> None:
        await self._client._arequest("POST", f"scans/{scan_id}/resume")
        
    async def trigger(self, scan_id: str) -> None:
        await self._client._arequest("POST", f"scans/{scan_id}/trigger")

    async def get_results(self, scan_id: str, cursor: Optional[str] = None, limit: Optional[int] = None, sort: Optional[str] = None) -> PaginatedList[ScanResultItemResponse]:
        params: Dict[str, Any] = {}
        if cursor: params["c"] = cursor
        if limit is not None: params["l"] = limit
        if sort: params["s"] = sort
        response = await self._client._arequest("GET", f"scans/{scan_id}/results", params=params)
        if not isinstance(response, dict) or "results" not in response or "pagination" not in response:
            raise AcunetixError("Unexpected response structure for get scan results.")
        return PaginatedList[ScanResultItemResponse](items=response.get("results", []), pagination=response.get("pagination", {}))

    async def get_vulnerabilities(self, scan_id: str, result_id: str, cursor: Optional[str] = None, limit: Optional[int] = None, query: Optional[str] = None, sort: Optional[str] = None) -> PaginatedList[Vulnerability]:
        params: Dict[str, Any] = {}
        if cursor: params["c"] = cursor
        if limit is not None: params["l"] = limit
        if query: params["q"] = query
        if sort: params["s"] = sort
        api_path = f"scans/{scan_id}/results/{result_id}/vulnerabilities"
        response = await self._client._arequest("GET", api_path, params=params)
        if not isinstance(response, dict) or "vulnerabilities" not in response or "pagination" not in response:
            raise AcunetixError("Unexpected response structure for get vulnerabilities.")
        return PaginatedList[Vulnerability](items=response.get("vulnerabilities", []), pagination=response.get("pagination", {}))

    async def get_result_by_id(self, result_id: str) -> ScanResultItemResponse:
        """Retrieves a specific scan result by its standalone ID asynchronously."""
        response_data = await self._client._arequest("GET", f"results/{result_id}")
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for get_result_by_id.")
        return ScanResultItemResponse(**response_data)

    # 同步方法对应的异步实现
    async def search_crawl_data(
        self,
        scan_id: str,
        result_id: str,
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
        query: Optional[str] = None,
        sort: Optional[str] = None,
    ) -> PaginatedList[Dict[str, Any]]:
        params: Dict[str, Any] = {}
        if cursor: params["c"] = cursor
        if limit is not None: params["l"] = limit
        if query: params["q"] = query
        if sort: params["s"] = sort
        response = await self._client._arequest(
            "GET",
            f"scans/{scan_id}/results/{result_id}/crawldata",
            params=params,
        )
        if not isinstance(response, dict) or "locations" not in response or "pagination" not in response:
            raise AcunetixError("Unexpected response structure for search_crawl_data.")
        return PaginatedList[Dict[str, Any]](items=response.get("locations", []), pagination=response.get("pagination", {}))

    async def get_crawl_location_details(self, scan_id: str, result_id: str, loc_id: int) -> Dict[str, Any]:
        response = await self._client._arequest(
            "GET",
            f"scans/{scan_id}/results/{result_id}/crawldata/{loc_id}",
        )
        if not isinstance(response, dict):
            raise AcunetixError("Unexpected response type for get_crawl_location_details.")
        return response

    async def get_crawl_location_children(
        self,
        scan_id: str,
        result_id: str,
        loc_id: int,
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
        sort: Optional[str] = None,
    ) -> PaginatedList[Dict[str, Any]]:
        params: Dict[str, Any] = {}
        if cursor: params["c"] = cursor
        if limit is not None: params["l"] = limit
        if sort: params["s"] = sort
        response = await self._client._arequest(
            "GET",
            f"scans/{scan_id}/results/{result_id}/crawldata/{loc_id}/children",
            params=params,
        )
        if not isinstance(response, dict) or "locations" not in response or "pagination" not in response:
            raise AcunetixError("Unexpected response structure for get_crawl_location_children.")
        return PaginatedList[Dict[str, Any]](items=response.get("locations", []), pagination=response.get("pagination", {}))

    async def get_crawl_location_vulnerabilities(
        self,
        scan_id: str,
        result_id: str,
        loc_id: int,
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
        sort: Optional[str] = None,
    ) -> PaginatedList[Vulnerability]:
        params: Dict[str, Any] = {}
        if cursor: params["c"] = cursor
        if limit is not None: params["l"] = limit
        if sort: params["s"] = sort
        response = await self._client._arequest(
            "GET",
            f"scans/{scan_id}/results/{result_id}/crawldata/{loc_id}/vulnerabilities",
            params=params,
        )
        if not isinstance(response, dict) or "vulnerabilities" not in response or "pagination" not in response:
            raise AcunetixError("Unexpected response structure for get_crawl_location_vulnerabilities.")
        return PaginatedList[Vulnerability](items=response.get("vulnerabilities", []), pagination=response.get("pagination", {}))

    async def get_statistics(self, scan_id: str, result_id: str) -> Dict[str, Any]:
        response = await self._client._arequest(
            "GET",
            f"scans/{scan_id}/results/{result_id}/statistics",
        )
        if not isinstance(response, dict):
            raise AcunetixError("Unexpected response type for get_statistics.")
        return response

    async def list_result_technologies(
        self,
        scan_id: str,
        result_id: str,
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
        query: Optional[str] = None,
        sort: Optional[str] = None,
    ) -> PaginatedList[Technology]:
        params: Dict[str, Any] = {}
        if cursor: params["c"] = cursor
        if limit is not None: params["l"] = limit
        if query: params["q"] = query
        if sort: params["s"] = sort
        response = await self._client._arequest("GET", f"scans/{scan_id}/results/{result_id}/technologies", params=params)
        if not isinstance(response, dict) or "technologies" not in response or "pagination" not in response:
            raise AcunetixError("Unexpected response structure for list_result_technologies.")
        return PaginatedList[Technology](items=response.get("technologies", []), pagination=response.get("pagination", {}))

    async def list_result_technology_location_vulnerabilities(
        self,
        scan_id: str,
        result_id: str,
        tech_id: str,
        loc_id: int,
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
        query: Optional[str] = None,
        sort: Optional[str] = None,
    ) -> PaginatedList[Vulnerability]:
        params: Dict[str, Any] = {}
        if cursor: params["c"] = cursor
        if limit is not None: params["l"] = limit
        if query: params["q"] = query
        if sort: params["s"] = sort
        path = f"scans/{scan_id}/results/{result_id}/technologies/{tech_id}/locations/{loc_id}/vulnerabilities"
        response = await self._client._arequest("GET", path, params=params)
        if not isinstance(response, dict) or "vulnerabilities" not in response or "pagination" not in response:
            raise AcunetixError("Unexpected response structure for list_result_technology_location_vulnerabilities.")
        return PaginatedList[Vulnerability](items=response.get("vulnerabilities", []), pagination=response.get("pagination", {}))

    async def list_result_vulnerability_types(
        self,
        scan_id: str,
        result_id: str,
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
        query: Optional[str] = None,
        sort: Optional[str] = None,
    ) -> PaginatedList[VulnerabilityTypeSessionsCountResponseItem]:
        params: Dict[str, Any] = {}
        if cursor: params["c"] = cursor
        if limit is not None: params["l"] = limit
        if query: params["q"] = query
        if sort: params["s"] = sort
        path = f"scans/{scan_id}/results/{result_id}/vulnerability_types"
        response = await self._client._arequest("GET", path, params=params)
        if not isinstance(response, dict) or "vulnerability_types" not in response or "pagination" not in response:
            raise AcunetixError("Unexpected response structure for list_result_vulnerability_types.")
        return PaginatedList[VulnerabilityTypeSessionsCountResponseItem](items=response.get("vulnerability_types", []), pagination=response.get("pagination", {}))

    async def get_scan_vulnerability_detail(self, scan_id: str, result_id: str, vuln_id: str) -> VulnerabilityDetails:
        """
        获取特定扫描会话中漏洞的详细信息。
        对应 GET /scans/{scan_id}/results/{result_id}/vulnerabilities/{vuln_id}
        """
        path = f"scans/{scan_id}/results/{result_id}/vulnerabilities/{vuln_id}"
        response_data = await self._client._arequest("GET", path)
        if not isinstance(response_data, dict):
            raise AcunetixError("获取扫描漏洞详情时返回了意外的响应类型。")
        return VulnerabilityDetails(**response_data)

    async def get_scan_vulnerability_http_response(self, scan_id: str, result_id: str, vuln_id: str) -> bytes:
        """
        获取漏洞的 HTTP 响应。
        对应 GET /scans/{scan_id}/results/{result_id}/vulnerabilities/{vuln_id}/http_response
        """
        path = f"scans/{scan_id}/results/{result_id}/vulnerabilities/{vuln_id}/http_response"
        response = await self._client._arequest("GET", path, expect_json=False)
        if not isinstance(response, bytes):
            raise AcunetixError("获取漏洞 HTTP 响应时返回了意外的响应类型。")
        return response

    async def set_scan_vulnerability_status(self, scan_id: str, result_id: str, vuln_id: str, status_data: VulnerabilityStatus) -> None:
        """
        更新漏洞状态。
        对应 PUT /scans/{scan_id}/results/{result_id}/vulnerabilities/{vuln_id}/status
        """
        path = f"scans/{scan_id}/results/{result_id}/vulnerabilities/{vuln_id}/status"
        await self._client._arequest("PUT", path, json_data=status_data.model_dump(exclude_none=True, by_alias=True, mode='json'))

    async def recheck_scan_vulnerability(self, scan_id: str, result_id: str, vuln_id: str, recheck_data: VulnerabilityRecheck) -> None:
        """
        重检单个漏洞。
        对应 PUT /scans/{scan_id}/results/{result_id}/vulnerabilities/{vuln_id}/recheck
        """
        path = f"scans/{scan_id}/results/{result_id}/vulnerabilities/{vuln_id}/recheck"
        await self._client._arequest("PUT", path, json_data=recheck_data.model_dump(exclude_none=True, by_alias=True, mode='json'))

    async def recheck_scan_vulnerabilities(self, scan_id: str, result_id: str, recheck_data: VulnerabilitiesRecheck) -> None:
        """
        重检多个漏洞。
        对应 POST /scans/{scan_id}/results/{result_id}/vulnerabilities/recheck
        """
        path = f"scans/{scan_id}/results/{result_id}/vulnerabilities/recheck"
        await self._client._arequest("POST", path, json_data=recheck_data.model_dump(exclude_none=True, by_alias=True, mode='json'))

    async def get_scan_vulnerability_detail_by_vuln_id(self, vuln_id: str) -> VulnerabilityDetails:
        """
        通过漏洞 ID 获取漏洞详情，无需 scan_id 和 result_id。
        对应 GET /scan_vulnerabilities/{vuln_id}
        """
        path = f"scan_vulnerabilities/{vuln_id}"
        response_data = await self._client._arequest("GET", path)
        if not isinstance(response_data, dict):
            raise AcunetixError("通过 vuln_id 获取扫描漏洞详情时返回了意外的响应类型。")
        return VulnerabilityDetails(**response_data)
