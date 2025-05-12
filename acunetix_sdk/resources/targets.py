from typing import List, Optional, Dict, Any, TYPE_CHECKING, IO

from ..models.target import (
    TargetResponse, 
    TargetCreateRequest, 
    TargetUpdateRequest, 
    AddTargetsDescriptor,
    TargetIdList,
    TargetConfigurationData,
    ContinuousScanMode,
    SensorSecretContainer,
    SensorType,
    AllowedHosts,
    TargetIdContainer,
    ExcludedPathList,
    ExcludedPathListUpdate,
    TargetGroupIdList,
    Technology,              # Added import for technologies
    TargetDeletionNotification,
    ContinuousScanItemResponse,
    # TechnologiesListResponse # This model is not directly used as return type, PaginatedList[Technology] is
)
from ..models.vulnerability import Vulnerability # Updated import

# Models for file uploads are in common_settings
from ..models.common_settings import (
    FileUploadDescriptor,
    UploadLocationResponse,
    UploadedFile,
    UploadedFilesResponse
)
from ..models.pagination import PaginatedList
from .base_resource import BaseResource
from ..errors import AcunetixError
import io # For IO[bytes] type hint

if TYPE_CHECKING:
    from ..client_sync import AcunetixSyncClient
    from ..client_async import AcunetixAsyncClient

class TargetsSyncResource(BaseResource["AcunetixSyncClient"]):
    """Handles synchronous operations related to Acunetix targets."""

    def list(self, cursor: Optional[str] = None, limit: Optional[int] = None, query: Optional[str] = None, sort: Optional[str] = None) -> PaginatedList[TargetResponse]:
        params: Dict[str, Any] = {}
        if cursor: params["c"] = cursor
        if limit is not None: params["l"] = limit
        if query: params["q"] = query
        if sort: params["s"] = sort
        response = self._client._request("GET", "targets", params=params)
        if not isinstance(response, dict) or "targets" not in response or "pagination" not in response:
             raise AcunetixError("Unexpected response structure for list targets. Expected 'targets' and 'pagination' keys.")
        return PaginatedList[TargetResponse](items=response.get("targets", []), pagination=response.get("pagination", {}))

    def create(self, target_data: TargetCreateRequest) -> TargetResponse:
        # 使用 model_dump(mode='json') 来确保 HttpUrl 等特殊类型被正确序列化为 JSON 兼容的字符串
        dict_payload = target_data.model_dump(exclude_none=True, by_alias=True, mode='json') 
        # _request in client_base sets Content-Type: application/json when json_data is used.
        response_data = self._client._request("POST", "targets", json_data=dict_payload) # 传递给 json_data
        if not isinstance(response_data, dict): 
            raise AcunetixError("Unexpected response type for create target. Expected a dictionary.")
        return TargetResponse(**response_data)

    def create_many(self, descriptor: AddTargetsDescriptor) -> List[TargetResponse]:
        dict_payload = descriptor.model_dump(exclude_none=True, by_alias=True, mode='json')
        response_data = self._client._request("POST", "targets/add", json_data=dict_payload)
        if not isinstance(response_data, dict) or "targets" not in response_data or not isinstance(response_data["targets"], list):
            raise AcunetixError("Unexpected response type for create_many targets. Expected a dict with a 'targets' list.")
        return [TargetResponse(**item) for item in response_data["targets"]]

    def get(self, target_id: str) -> TargetResponse:
        response_data = self._client._request("GET", f"targets/{target_id}")
        if not isinstance(response_data, dict): 
            raise AcunetixError("Unexpected response type for get target. Expected a dictionary.")
        return TargetResponse(**response_data)

    def update(self, target_id: str, update_data: TargetUpdateRequest) -> None:
        dict_payload = update_data.model_dump(exclude_none=True, by_alias=True, mode='json')
        self._client._request("PATCH", f"targets/{target_id}", json_data=dict_payload)

    def delete(self, target_id: str) -> Optional[TargetDeletionNotification]:
        """
        Deletes a specific target.
        Corresponds to DELETE /targets/{target_id} in API.
        API operationId: remove_target
        Returns TargetDeletionNotification if API returns 200, otherwise None for 204.
        """
        # Removed expect_json_response=False, _request should handle 204 appropriately
        response_data = self._client._request("DELETE", f"targets/{target_id}") 
        
        # Check if response_data indicates a 200 response with content vs a 204 no content
        # This depends on how _request handles different status codes and content types.
        # Assuming if it's a 200 with TargetDeletionNotification, response_data will be a dict.
        # If it's 204, response_data might be None or an empty response object.
        if response_data and isinstance(response_data, dict): # Check if there's data to parse
            # This assumes _request can return the parsed JSON for 200 or None/empty for 204
            # And that the underlying HTTP client doesn't raise an error for 204 with no content if expect_json_response=True
            # A more robust way would be for _request to return status_code as well.
            # For now, we try to parse if data is present.
            try:
                return TargetDeletionNotification(**response_data)
            except Exception as e: # Broad exception if parsing fails but data was present
                # Log this unexpected scenario
                # print(f"Warning: Received data for DELETE /targets/{target_id} but failed to parse as TargetDeletionNotification: {e}")
                return None # Or re-raise a specific error
        return None # For 204 No Content or if response_data is None/empty

    def delete_many(self, target_ids: List[str]) -> None:
        # This method serializes TargetIdList, which only contains basic types.
        # For consistency, use model_dump(mode='json') and json_data.
        dict_payload = TargetIdList(target_id_list=target_ids).model_dump(exclude_none=True, by_alias=True, mode='json')
        self._client._request("POST", "targets/delete", json_data=dict_payload)

    def get_configuration(self, target_id: str) -> TargetConfigurationData:
        response_data = self._client._request("GET", f"targets/{target_id}/configuration")
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for get target configuration.")
        return TargetConfigurationData(**response_data)

    def update_configuration(self, target_id: str, config_data: TargetConfigurationData) -> None:
        dict_payload = config_data.model_dump(exclude_none=True, by_alias=True, mode='json')
        self._client._request("PATCH", f"targets/{target_id}/configuration", json_data=dict_payload)

    def get_continuous_scan_status(self, target_id: str) -> ContinuousScanMode:
        response_data = self._client._request("GET", f"targets/{target_id}/continuous_scan")
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for get continuous scan status.")
        return ContinuousScanMode(**response_data)

    def set_continuous_scan_status(self, target_id: str, status_data: ContinuousScanMode) -> None:
        dict_payload = status_data.model_dump(exclude_none=True, by_alias=True, mode='json')
        self._client._request("POST", f"targets/{target_id}/continuous_scan", json_data=dict_payload)

    def reset_sensor_secret(self, target_id: str, secret_data: Optional[SensorSecretContainer] = None) -> SensorSecretContainer:
        dict_payload = secret_data.model_dump(exclude_none=True, by_alias=True, mode='json') if secret_data else {}
        response_data = self._client._request("POST", f"targets/{target_id}/sensor/reset", json_data=dict_payload)
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for reset sensor secret.")
        return SensorSecretContainer(**response_data)

    def download_sensor(self, sensor_type: SensorType, sensor_secret: str) -> IO[bytes]:
        response_content = self._client._request(
            method="GET",
            path=f"targets/sensors/{sensor_type.value}/{sensor_secret}",
            expected_response_type="bytes",
            additional_headers={"Accept": "application/octet-stream"}
        )
        if not isinstance(response_content, bytes):
            raise AcunetixError(f"Expected bytes for sensor download, got {type(response_content)}")
        return io.BytesIO(response_content)

    def list_allowed_hosts(self, target_id: str) -> AllowedHosts:
        response_data = self._client._request("GET", f"targets/{target_id}/allowed_hosts")
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for list allowed hosts.")
        return AllowedHosts(**response_data)

    def add_allowed_host(self, target_id: str, allowed_target_id_container: TargetIdContainer) -> None:
        dict_payload = allowed_target_id_container.model_dump(exclude_none=True, by_alias=True, mode='json')
        self._client._request("POST", f"targets/{target_id}/allowed_hosts", json_data=dict_payload)

    def remove_allowed_host(self, target_id: str, allowed_target_id: str) -> None:
        self._client._request("DELETE", f"targets/{target_id}/allowed_hosts/{allowed_target_id}")

    def get_login_sequence_info(self, target_id: str) -> UploadedFile:
        response_data = self._client._request("GET", f"targets/{target_id}/configuration/login_sequence")
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for get login sequence info.")
        return UploadedFile(**response_data)

    def prepare_login_sequence_upload(self, target_id: str, descriptor: FileUploadDescriptor) -> UploadLocationResponse:
        dict_payload = descriptor.model_dump(exclude_none=True, by_alias=True, mode='json')
        response_data = self._client._request("POST", f"targets/{target_id}/configuration/login_sequence", json_data=dict_payload)
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for prepare login sequence upload.")
        return UploadLocationResponse(**response_data)

    def delete_login_sequence(self, target_id: str) -> None:
        self._client._request("DELETE", f"targets/{target_id}/configuration/login_sequence")

    def download_login_sequence(self, target_id: str) -> IO[bytes]:
        response_content = self._client._request(
            method="GET",
            path=f"targets/{target_id}/configuration/login_sequence/download",
            expected_response_type="bytes",
            additional_headers={"Accept": "application/octet-stream"}
        )
        if not isinstance(response_content, bytes):
            raise AcunetixError(f"Expected bytes for login sequence download, got {type(response_content)}")
        return io.BytesIO(response_content)

    def get_client_certificate_info(self, target_id: str) -> UploadedFile:
        response_data = self._client._request("GET", f"targets/{target_id}/configuration/client_certificate")
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for get client certificate info.")
        return UploadedFile(**response_data)

    def prepare_client_certificate_upload(self, target_id: str, descriptor: FileUploadDescriptor) -> UploadLocationResponse:
        dict_payload = descriptor.model_dump(exclude_none=True, by_alias=True, mode='json')
        response_data = self._client._request("POST", f"targets/{target_id}/configuration/client_certificate", json_data=dict_payload)
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for prepare client certificate upload.")
        return UploadLocationResponse(**response_data)

    def delete_client_certificate(self, target_id: str) -> None:
        self._client._request("DELETE", f"targets/{target_id}/configuration/client_certificate")

    def list_imported_files(self, target_id: str) -> UploadedFilesResponse:
        response_data = self._client._request("GET", f"targets/{target_id}/configuration/imports")
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for list imported files.")
        return UploadedFilesResponse(**response_data)

    def prepare_import_file_upload(self, target_id: str, descriptor: FileUploadDescriptor) -> UploadLocationResponse:
        dict_payload = descriptor.model_dump(exclude_none=True, by_alias=True, mode='json')
        response_data = self._client._request("POST", f"targets/{target_id}/configuration/imports", json_data=dict_payload)
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for prepare import file upload.")
        return UploadLocationResponse(**response_data)

    def delete_imported_file(self, target_id: str, import_id: str) -> None:
        self._client._request("DELETE", f"targets/{target_id}/configuration/imports/{import_id}")

    # --- Target Configuration - Excluded Paths Methods ---
    def get_excluded_paths(self, target_id: str) -> ExcludedPathList:
        """
        Retrieves the list of excluded paths for a target.
        Corresponds to GET /targets/{target_id}/configuration/exclusions in API.
        API operationId: get_excluded_paths
        """
        response_data = self._client._request("GET", f"targets/{target_id}/configuration/exclusions")
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for get excluded paths.")
        return ExcludedPathList(**response_data)

    def update_excluded_paths(self, target_id: str, update_data: ExcludedPathListUpdate) -> None:
        """
        Updates the list of excluded paths for a target.
        Corresponds to POST /targets/{target_id}/configuration/exclusions in API.
        API operationId: update_excluded_paths
        """
        dict_payload = update_data.model_dump(exclude_none=True, by_alias=True, mode='json') # exclude_none for partial updates
        self._client._request("POST", f"targets/{target_id}/configuration/exclusions", json_data=dict_payload)
        # API returns 204 No Content

    # --- Target Groups for a Target ---
    def list_target_groups(self, target_id: str) -> TargetGroupIdList:
        """
        Retrieves a list of target groups a specific target belongs to.
        Corresponds to GET /targets/{target_id}/target_groups in API.
        API operationId: list_target_groups
        """
        response_data = self._client._request("GET", f"targets/{target_id}/target_groups")
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for list target groups.")
        return TargetGroupIdList(**response_data)

    # --- Target Technologies and Vulnerabilities ---
    def list_technologies(self, target_id: str, cursor: Optional[str] = None, limit: Optional[int] = None, query: Optional[str] = None, sort: Optional[str] = None) -> PaginatedList[Technology]:
        """
        Lists technologies found on a specific target.
        Corresponds to GET /targets/{target_id}/technologies in API.
        API operationId: get_target_technologies
        """
        params: Dict[str, Any] = {}
        if cursor: params["c"] = cursor
        if limit is not None: params["l"] = limit
        if query: params["q"] = query # API spec shows query for this endpoint
        if sort: params["s"] = sort   # API spec shows sort for this endpoint

        response_data = self._client._request("GET", f"targets/{target_id}/technologies", params=params)
        if not isinstance(response_data, dict) or "technologies" not in response_data or "pagination" not in response_data:
            raise AcunetixError("Unexpected response structure for list_technologies. Expected 'technologies' and 'pagination' keys.")
        return PaginatedList[Technology](items=response_data.get("technologies", []), pagination=response_data.get("pagination", {}))

    def list_technology_vulnerabilities(self, target_id: str, tech_id: str, cursor: Optional[str] = None, limit: Optional[int] = None, query: Optional[str] = None, sort: Optional[str] = None) -> PaginatedList[Vulnerability]:
        """
        Lists vulnerabilities for a specific technology found on a target.
        Corresponds to GET /targets/{target_id}/technologies/{tech_id}/vulnerabilities in API.
        API operationId: get_scan_technology_vulnerabilities 
        NOTE: API documentation has an operationId conflict for 'get_scan_technology_vulnerabilities'
              (also used by GET /scans/{scan_id}/results/{result_id}/technologies/{tech_id}/locations/{loc_id}/vulnerabilities).
        """
        params: Dict[str, Any] = {}
        if cursor: params["c"] = cursor
        if limit is not None: params["l"] = limit
        if query: params["q"] = query
        if sort: params["s"] = sort

        response_data = self._client._request("GET", f"targets/{target_id}/technologies/{tech_id}/vulnerabilities", params=params)
        if not isinstance(response_data, dict) or "vulnerabilities" not in response_data or "pagination" not in response_data:
            raise AcunetixError("Unexpected response structure for list_technology_vulnerabilities. Expected 'vulnerabilities' and 'pagination' keys.")
        # Assuming Vulnerability model from scan.py is compatible or will be made compatible
        return PaginatedList[Vulnerability](items=response_data.get("vulnerabilities", []), pagination=response_data.get("pagination", {}))

    # --- Target Configuration - Workers ---
    def get_assigned_workers(self, target_id: str) -> "WorkerList": # Forward reference for WorkerList
        """
        Retrieves workers assigned to a specific target.
        Corresponds to GET /targets/{target_id}/configuration/workers in API.
        API operationId: get_workers_assigned_to_target
        """
        # Need to import WorkerList from ..models.worker
        from ..models.worker import WorkerList as WorkerListModel # Alias to avoid conflict if any
        response_data = self._client._request("GET", f"targets/{target_id}/configuration/workers")
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for get assigned workers.")
        return WorkerListModel(**response_data)

    def assign_workers(self, target_id: str, worker_id_list: "WorkerIdList") -> None: # Forward reference
        """
        Assigns workers to a specific target.
        Corresponds to POST /targets/{target_id}/configuration/workers in API.
        API operationId: assign_workers_to_target
        """
        # Need to import WorkerIdList from ..models.worker
        from ..models.worker import WorkerIdList as WorkerIdListModel # Ensure this import is present
        dict_payload = worker_id_list.model_dump(exclude_none=True, by_alias=True, mode='json')
        self._client._request("POST", f"targets/{target_id}/configuration/workers", json_data=dict_payload)
        # API returns 204 No Content

    def export_cvs(self, query: Optional[str] = None, sort: Optional[str] = None) -> IO[bytes]:
        """Downloads the targets list in CVS format.

        Corresponds to GET /targets/cvs_export in API.
        API operationId: cvs_export
        Returns a BytesIO stream containing the CVS data.
        """
        params: Dict[str, Any] = {}
        if query:
            params["q"] = query
        if sort:
            params["s"] = sort
        response_content = self._client._request(
            method="GET",
            path="targets/cvs_export",
            params=params,
            expected_response_type="bytes",
            additional_headers={"Accept": "application/octet-stream"}
        )
        if not isinstance(response_content, bytes):
            raise AcunetixError(f"Expected bytes for CVS export, got {type(response_content)}")
        return io.BytesIO(response_content)

    def list_continuous_scans(
        self,
        target_id: str,
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
        sort: Optional[str] = None,
    ) -> PaginatedList[ContinuousScanItemResponse]:
        """List continuous scans for a target.

        Corresponds to GET /targets/{target_id}/continuous_scan/list in API.
        API operationId: get_continuous_scans
        """
        params: Dict[str, Any] = {}
        if cursor:
            params["c"] = cursor
        if limit is not None:
            params["l"] = limit
        if sort:
            params["s"] = sort
        response = self._client._request("GET", f"targets/{target_id}/continuous_scan/list", params=params)
        if not isinstance(response, dict) or "scans" not in response or "pagination" not in response:
            raise AcunetixError("Unexpected response structure for list_continuous_scans. Expected 'scans' and 'pagination' keys.")
        return PaginatedList[ContinuousScanItemResponse](items=response.get("scans", []), pagination=response.get("pagination", {}))


class TargetsAsyncResource(BaseResource["AcunetixAsyncClient"]):
    """Handles asynchronous operations related to Acunetix targets."""

    async def list(self, cursor: Optional[str] = None, limit: Optional[int] = None, query: Optional[str] = None, sort: Optional[str] = None) -> PaginatedList[TargetResponse]:
        params: Dict[str, Any] = {}
        if cursor: params["c"] = cursor
        if limit is not None: params["l"] = limit
        if query: params["q"] = query
        if sort: params["s"] = sort
        response = await self._client._arequest("GET", "targets", params=params)
        if not isinstance(response, dict) or "targets" not in response or "pagination" not in response:
            raise AcunetixError("Unexpected response structure for list targets.")
        return PaginatedList[TargetResponse](items=response.get("targets", []), pagination=response.get("pagination", {}))

    async def create(self, target_data: TargetCreateRequest) -> TargetResponse:
        dict_payload = target_data.model_dump(exclude_none=True, by_alias=True, mode='json')
        response_data = await self._client._arequest("POST", "targets", json_data=dict_payload)
        if not isinstance(response_data, dict): 
            raise AcunetixError("Unexpected response type for create target.")
        return TargetResponse(**response_data)

    async def create_many(self, descriptor: AddTargetsDescriptor) -> List[TargetResponse]:
        dict_payload = descriptor.model_dump(exclude_none=True, by_alias=True, mode='json')
        response_data = await self._client._arequest("POST", "targets/add", json_data=dict_payload)
        if not isinstance(response_data, dict) or "targets" not in response_data or not isinstance(response_data["targets"], list):
            raise AcunetixError("Unexpected response type for create_many targets.")
        return [TargetResponse(**item) for item in response_data["targets"]]

    async def get(self, target_id: str) -> TargetResponse:
        response_data = await self._client._arequest("GET", f"targets/{target_id}")
        if not isinstance(response_data, dict): 
            raise AcunetixError("Unexpected response type for get target.")
        return TargetResponse(**response_data)

    async def update(self, target_id: str, update_data: TargetUpdateRequest) -> None:
        dict_payload = update_data.model_dump(exclude_none=True, by_alias=True, mode='json')
        await self._client._arequest("PATCH", f"targets/{target_id}", json_data=dict_payload)

    async def delete(self, target_id: str) -> Optional[TargetDeletionNotification]:
        """Deletes a specific target asynchronously."""
        response_data = await self._client._arequest("DELETE", f"targets/{target_id}", expect_json_response=False)
        if response_data and isinstance(response_data, dict):
            try:
                return TargetDeletionNotification(**response_data)
            except Exception:
                return None
        return None

    async def delete_many(self, target_ids: List[str]) -> None:
        dict_payload = TargetIdList(target_id_list=target_ids).model_dump(exclude_none=True, by_alias=True, mode='json')
        await self._client._arequest("POST", "targets/delete", json_data=dict_payload)

    async def get_configuration(self, target_id: str) -> TargetConfigurationData:
        response_data = await self._client._arequest("GET", f"targets/{target_id}/configuration")
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for get target configuration.")
        return TargetConfigurationData(**response_data)

    async def update_configuration(self, target_id: str, config_data: TargetConfigurationData) -> None:
        dict_payload = config_data.model_dump(exclude_none=True, by_alias=True, mode='json')
        await self._client._arequest("PATCH", f"targets/{target_id}/configuration", json_data=dict_payload)

    async def get_continuous_scan_status(self, target_id: str) -> ContinuousScanMode:
        response_data = await self._client._arequest("GET", f"targets/{target_id}/continuous_scan")
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for get continuous scan status.")
        return ContinuousScanMode(**response_data)

    async def set_continuous_scan_status(self, target_id: str, status_data: ContinuousScanMode) -> None:
        dict_payload = status_data.model_dump(exclude_none=True, by_alias=True, mode='json')
        await self._client._arequest("POST", f"targets/{target_id}/continuous_scan", json_data=dict_payload)

    async def reset_sensor_secret(self, target_id: str, secret_data: Optional[SensorSecretContainer] = None) -> SensorSecretContainer:
        dict_payload = secret_data.model_dump(exclude_none=True, by_alias=True, mode='json') if secret_data else {}
        response_data = await self._client._arequest("POST", f"targets/{target_id}/sensor/reset", json_data=dict_payload)
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for reset sensor secret.")
        return SensorSecretContainer(**response_data)

    async def download_sensor(self, sensor_type: SensorType, sensor_secret: str) -> IO[bytes]:
        response_content = await self._client._arequest(
            method="GET",
            path=f"targets/sensors/{sensor_type.value}/{sensor_secret}",
            expected_response_type="bytes",
            additional_headers={"Accept": "application/octet-stream"}
        )
        if not isinstance(response_content, bytes):
            raise AcunetixError(f"Expected bytes for sensor download, got {type(response_content)}")
        return io.BytesIO(response_content)

    async def list_allowed_hosts(self, target_id: str) -> AllowedHosts:
        response_data = await self._client._arequest("GET", f"targets/{target_id}/allowed_hosts")
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for list allowed hosts.")
        return AllowedHosts(**response_data)

    async def add_allowed_host(self, target_id: str, allowed_target_id_container: TargetIdContainer) -> None:
        dict_payload = allowed_target_id_container.model_dump(exclude_none=True, by_alias=True, mode='json')
        await self._client._arequest("POST", f"targets/{target_id}/allowed_hosts", json_data=dict_payload)

    async def remove_allowed_host(self, target_id: str, allowed_target_id: str) -> None:
        await self._client._arequest("DELETE", f"targets/{target_id}/allowed_hosts/{allowed_target_id}")

    async def get_login_sequence_info(self, target_id: str) -> UploadedFile:
        response_data = await self._client._arequest("GET", f"targets/{target_id}/configuration/login_sequence")
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for get login sequence info.")
        return UploadedFile(**response_data)

    async def prepare_login_sequence_upload(self, target_id: str, descriptor: FileUploadDescriptor) -> UploadLocationResponse:
        dict_payload = descriptor.model_dump(exclude_none=True, by_alias=True, mode='json')
        response_data = await self._client._arequest("POST", f"targets/{target_id}/configuration/login_sequence", json_data=dict_payload)
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for prepare login sequence upload.")
        return UploadLocationResponse(**response_data)

    async def delete_login_sequence(self, target_id: str) -> None:
        await self._client._arequest("DELETE", f"targets/{target_id}/configuration/login_sequence")

    async def download_login_sequence(self, target_id: str) -> IO[bytes]:
        response_content = await self._client._arequest(
            method="GET",
            path=f"targets/{target_id}/configuration/login_sequence/download",
            expected_response_type="bytes",
            additional_headers={"Accept": "application/octet-stream"}
        )
        if not isinstance(response_content, bytes):
            raise AcunetixError(f"Expected bytes for login sequence download, got {type(response_content)}")
        return io.BytesIO(response_content)

    async def get_client_certificate_info(self, target_id: str) -> UploadedFile:
        response_data = await self._client._arequest("GET", f"targets/{target_id}/configuration/client_certificate")
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for get client certificate info.")
        return UploadedFile(**response_data)

    async def prepare_client_certificate_upload(self, target_id: str, descriptor: FileUploadDescriptor) -> UploadLocationResponse:
        dict_payload = descriptor.model_dump(exclude_none=True, by_alias=True, mode='json')
        response_data = await self._client._arequest("POST", f"targets/{target_id}/configuration/client_certificate", json_data=dict_payload)
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for prepare client certificate upload.")
        return UploadLocationResponse(**response_data)

    async def delete_client_certificate(self, target_id: str) -> None:
        await self._client._arequest("DELETE", f"targets/{target_id}/configuration/client_certificate")

    async def list_imported_files(self, target_id: str) -> UploadedFilesResponse:
        response_data = await self._client._arequest("GET", f"targets/{target_id}/configuration/imports")
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for list imported files.")
        return UploadedFilesResponse(**response_data)

    async def prepare_import_file_upload(self, target_id: str, descriptor: FileUploadDescriptor) -> UploadLocationResponse:
        dict_payload = descriptor.model_dump(exclude_none=True, by_alias=True, mode='json')
        response_data = await self._client._arequest("POST", f"targets/{target_id}/configuration/imports", json_data=dict_payload)
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for prepare import file upload.")
        return UploadLocationResponse(**response_data)

    async def delete_imported_file(self, target_id: str, import_id: str) -> None:
        await self._client._arequest("DELETE", f"targets/{target_id}/configuration/imports/{import_id}")

    # --- Target Configuration - Excluded Paths Methods ---
    async def get_excluded_paths(self, target_id: str) -> ExcludedPathList:
        """
        Retrieves the list of excluded paths for a target.
        Corresponds to GET /targets/{target_id}/configuration/exclusions in API.
        API operationId: get_excluded_paths
        """
        response_data = await self._client._arequest("GET", f"targets/{target_id}/configuration/exclusions")
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for get excluded paths.")
        return ExcludedPathList(**response_data)

    async def update_excluded_paths(self, target_id: str, update_data: ExcludedPathListUpdate) -> None:
        """
        Updates the list of excluded paths for a target.
        Corresponds to POST /targets/{target_id}/configuration/exclusions in API.
        API operationId: update_excluded_paths
        """
        dict_payload = update_data.model_dump(exclude_none=True, by_alias=True, mode='json')
        await self._client._arequest("POST", f"targets/{target_id}/configuration/exclusions", json_data=dict_payload)
        # API returns 204 No Content

    # --- Target Groups for a Target ---
    async def list_target_groups(self, target_id: str) -> TargetGroupIdList:
        response_data = await self._client._arequest("GET", f"targets/{target_id}/target_groups")
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for list target groups.")
        return TargetGroupIdList(**response_data)

    # --- Target Technologies and Vulnerabilities ---
    async def list_technologies(self, target_id: str, cursor: Optional[str] = None, limit: Optional[int] = None, query: Optional[str] = None, sort: Optional[str] = None) -> PaginatedList[Technology]:
        params: Dict[str, Any] = {}
        if cursor: params["c"] = cursor
        if limit is not None: params["l"] = limit
        if query: params["q"] = query
        if sort: params["s"] = sort
        response_data = await self._client._arequest("GET", f"targets/{target_id}/technologies", params=params)
        if not isinstance(response_data, dict) or "technologies" not in response_data or "pagination" not in response_data:
            raise AcunetixError("Unexpected response structure for list_technologies.")
        return PaginatedList[Technology](items=response_data.get("technologies", []), pagination=response_data.get("pagination", {}))

    async def list_technology_vulnerabilities(self, target_id: str, tech_id: str, cursor: Optional[str] = None, limit: Optional[int] = None, query: Optional[str] = None, sort: Optional[str] = None) -> PaginatedList[Vulnerability]:
        """
        Lists vulnerabilities for a specific technology found on a target asynchronously.
        Corresponds to GET /targets/{target_id}/technologies/{tech_id}/vulnerabilities in API.
        API operationId: get_scan_technology_vulnerabilities
        NOTE: API documentation has an operationId conflict for 'get_scan_technology_vulnerabilities'
              (also used by GET /scans/{scan_id}/results/{result_id}/technologies/{tech_id}/locations/{loc_id}/vulnerabilities).
        """
        params: Dict[str, Any] = {}
        if cursor: params["c"] = cursor
        if limit is not None: params["l"] = limit
        if query: params["q"] = query
        if sort: params["s"] = sort
        response_data = await self._client._arequest("GET", f"targets/{target_id}/technologies/{tech_id}/vulnerabilities", params=params)
        if not isinstance(response_data, dict) or "vulnerabilities" not in response_data or "pagination" not in response_data:
            raise AcunetixError("Unexpected response structure for list_technology_vulnerabilities.")
        return PaginatedList[Vulnerability](items=response_data.get("vulnerabilities", []), pagination=response_data.get("pagination", {}))

    # --- Target Configuration - Workers (Async) ---
    async def get_assigned_workers(self, target_id: str) -> "WorkerList": # Forward reference
        from ..models.worker import WorkerList as WorkerListModel
        response_data = await self._client._arequest("GET", f"targets/{target_id}/configuration/workers")
        if not isinstance(response_data, dict):
            raise AcunetixError("Async: Unexpected response for get assigned workers.")
        return WorkerListModel(**response_data)

    async def assign_workers(self, target_id: str, worker_id_list: "WorkerIdList") -> None: # Forward reference
        from ..models.worker import WorkerIdList as WorkerIdListModel # Ensure this import is present
        dict_payload = worker_id_list.model_dump(exclude_none=True, by_alias=True, mode='json')
        await self._client._arequest("POST", f"targets/{target_id}/configuration/workers", json_data=dict_payload)

    async def export_cvs(self, query: Optional[str] = None, sort: Optional[str] = None) -> IO[bytes]:
        """Asynchronously downloads the targets list in CVS format."""
        params: Dict[str, Any] = {}
        if query:
            params["q"] = query
        if sort:
            params["s"] = sort
        response_content = await self._client._arequest(
            method="GET",
            path="targets/cvs_export",
            params=params,
            expected_response_type="bytes",
            additional_headers={"Accept": "application/octet-stream"}
        )
        if not isinstance(response_content, bytes):
            raise AcunetixError(f"Expected bytes for CVS export, got {type(response_content)}")
        return io.BytesIO(response_content)

    async def list_continuous_scans(
        self,
        target_id: str,
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
        sort: Optional[str] = None,
    ) -> PaginatedList[ContinuousScanItemResponse]:
        params: Dict[str, Any] = {}
        if cursor:
            params["c"] = cursor
        if limit is not None:
            params["l"] = limit
        if sort:
            params["s"] = sort
        response = await self._client._arequest("GET", f"targets/{target_id}/continuous_scan/list", params=params)
        if not isinstance(response, dict) or "scans" not in response or "pagination" not in response:
            raise AcunetixError("Unexpected response structure for list_continuous_scans.")
        return PaginatedList[ContinuousScanItemResponse](items=response.get("scans", []), pagination=response.get("pagination", {}))
