from typing import Optional, Dict, Any, TYPE_CHECKING

from ..models.issue_tracker import (
    IssueTrackerList,
    IssueTrackerEntry,
    IssueTrackerConfig, # For helper endpoints that take full config
    IssueTrackerConnectionStatus,
    IssueTrackerProjects,
    IssueTrackerIssueTypes,
    IssueTrackerCollections,
    IssueTrackerCustomFields
)
# Pagination is not specified for the main list, but helper endpoints might use it if they return lists.
# from ..models.pagination import PaginatedList 
from .base_resource import BaseResource
from ..errors import AcunetixError

if TYPE_CHECKING:
    from ..client_sync import AcunetixSyncClient
    from ..client_async import AcunetixAsyncClient

class IssueTrackersSyncResource(BaseResource["AcunetixSyncClient"]):
    """Handles synchronous operations related to Acunetix Issue Trackers."""

    # --- Helper methods for new Issue Tracker configuration ---
    def check_connection_new(self, config_data: IssueTrackerConfig) -> IssueTrackerConnectionStatus:
        """
        Tests connection to a new (unsaved) Issue Tracker.
        Corresponds to POST /issue_trackers/check_connection.
        NOTE: API documentation has an operationId conflict for 'check_connection' 
              (also used by POST /wafs/check_connection).
        """
        payload = config_data.model_dump(exclude_none=True, by_alias=True, mode='json')
        response_data = self._client._request("POST", "issue_trackers/check_connection", json_data=payload)
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for check_connection_new.")
        return IssueTrackerConnectionStatus(**response_data)

    def check_projects_new(self, config_data: IssueTrackerConfig) -> IssueTrackerProjects:
        """Requests projects for a new (unsaved) Issue Tracker."""
        payload = config_data.model_dump(exclude_none=True, by_alias=True, mode='json')
        response_data = self._client._request("POST", "issue_trackers/check_projects", json_data=payload)
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for check_projects_new.")
        return IssueTrackerProjects(**response_data)

    def check_issue_types_new(self, config_data: IssueTrackerConfig) -> IssueTrackerIssueTypes:
        """Requests issue types for a project in a new (unsaved) Issue Tracker."""
        payload = config_data.model_dump(exclude_none=True, by_alias=True, mode='json')
        response_data = self._client._request("POST", "issue_trackers/check_issue_types", json_data=payload)
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for check_issue_types_new.")
        return IssueTrackerIssueTypes(**response_data)

    def get_collections_new(self, config_data: IssueTrackerConfig) -> IssueTrackerCollections:
        """Gets TFS collections for a new (unsaved) Issue Tracker."""
        payload = config_data.model_dump(exclude_none=True, by_alias=True, mode='json')
        response_data = self._client._request("POST", "issue_trackers/collections", json_data=payload)
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for get_collections_new.")
        return IssueTrackerCollections(**response_data)

    def get_custom_fields_new(self, config_data: IssueTrackerConfig) -> IssueTrackerCustomFields:
        """Gets custom fields for a new (unsaved) Issue Tracker."""
        payload = config_data.model_dump(exclude_none=True, by_alias=True, mode='json')
        response_data = self._client._request("POST", "issue_trackers/custom_fields", json_data=payload)
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for get_custom_fields_new.")
        return IssueTrackerCustomFields(**response_data)

    # --- CRUD for saved Issue Trackers ---
    def list(self) -> IssueTrackerList: # API spec does not show pagination for this
        """Lists all saved issue trackers."""
        response_data = self._client._request("GET", "issue_trackers")
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for list issue trackers.")
        return IssueTrackerList(**response_data)

    def create(self, entry_data: IssueTrackerEntry) -> Optional[str]:
        """
        Creates a new issue tracker entry.
        API returns 201 Created. The API documentation does not specify a response body
        for this operation but a Location header is typically expected for 201.
        Returns the Location header URL if available, otherwise None.
        """
        payload = entry_data.model_dump(exclude={"issue_tracker_id"}, exclude_none=True, by_alias=True, mode='json')
        raw_response = self._client._request("POST", "issue_trackers", json_data=payload, return_raw_response=True)
        
        if hasattr(raw_response, "headers"):
            return raw_response.headers.get("Location")
        return None

    def get(self, issue_tracker_id: str) -> IssueTrackerEntry:
        """Retrieves a specific issue tracker entry by ID."""
        response_data = self._client._request("GET", f"issue_trackers/{issue_tracker_id}")
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for get issue tracker entry.")
        return IssueTrackerEntry(**response_data)

    def update(self, issue_tracker_id: str, entry_data: IssueTrackerEntry) -> None: # API returns 204
        """Modifies an existing issue tracker entry."""
        payload = entry_data.model_dump(exclude={"issue_tracker_id"}, exclude_none=True, by_alias=True, mode='json')
        self._client._request("PATCH", f"issue_trackers/{issue_tracker_id}", json_data=payload)

    def delete(self, issue_tracker_id: str) -> None: # API returns 204
        """Deletes a specific issue tracker entry."""
        self._client._request("DELETE", f"issue_trackers/{issue_tracker_id}")

    # --- Helper methods for existing (saved) Issue Trackers ---
    def check_connection(self, issue_tracker_id: str) -> IssueTrackerConnectionStatus:
        """Tests connection for an existing Issue Tracker."""
        response_data = self._client._request("GET", f"issue_trackers/{issue_tracker_id}/check_connection")
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for check_connection.")
        return IssueTrackerConnectionStatus(**response_data)

    def get_collections(self, issue_tracker_id: str) -> IssueTrackerCollections:
        """Gets TFS collections for an existing Issue Tracker."""
        response_data = self._client._request("GET", f"issue_trackers/{issue_tracker_id}/collections")
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for get_collections.")
        return IssueTrackerCollections(**response_data)

    def get_custom_fields(self, issue_tracker_id: str) -> IssueTrackerCustomFields:
        """Gets custom fields for an existing Issue Tracker."""
        response_data = self._client._request("GET", f"issue_trackers/{issue_tracker_id}/custom_fields")
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for get_custom_fields.")
        return IssueTrackerCustomFields(**response_data)

    def get_projects(self, issue_tracker_id: str) -> IssueTrackerProjects:
        """Gets projects for an existing Issue Tracker."""
        response_data = self._client._request("GET", f"issue_trackers/{issue_tracker_id}/projects")
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for get_projects.")
        return IssueTrackerProjects(**response_data)
        
    def get_issue_types_by_project_id(self, issue_tracker_id: str, project_id: str) -> IssueTrackerIssueTypes: # API spec says IssueTrackerProjects
        """Gets issue types for a specific project ID of an existing Issue Tracker."""
        # API spec for this endpoint returns IssueTrackerProjects, which seems incorrect.
        # It should logically return IssueTrackerIssueTypes. Assuming IssueTrackerIssueTypes for now.
        response_data = self._client._request("GET", f"issue_trackers/{issue_tracker_id}/projects/{project_id}/issue_types")
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for get_issue_types_by_project_id.")
        # If API truly returns IssueTrackerProjects, then: return IssueTrackerProjects(**response_data)
        return IssueTrackerIssueTypes(**response_data) # Assuming it returns IssueTypes

    def get_issue_types_by_project_qname(self, issue_tracker_id: str, project_id_qname: str) -> IssueTrackerIssueTypes: # API spec says IssueTrackerProjects
        """Gets issue types for a project (by query param name/id) of an existing Issue Tracker."""
        # Similar to above, assuming IssueTrackerIssueTypes.
        params = {"project_id": project_id_qname}
        response_data = self._client._request("GET", f"issue_trackers/{issue_tracker_id}/projects/issue_types", params=params)
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for get_issue_types_by_project_qname.")
        return IssueTrackerIssueTypes(**response_data)


class IssueTrackersAsyncResource(BaseResource["AcunetixAsyncClient"]):
    """Handles asynchronous operations related to Acunetix Issue Trackers."""

    async def check_connection_new(self, config_data: IssueTrackerConfig) -> IssueTrackerConnectionStatus:
        """
        Tests connection to a new (unsaved) Issue Tracker asynchronously.
        Corresponds to POST /issue_trackers/check_connection.
        NOTE: API documentation has an operationId conflict for 'check_connection' 
              (also used by POST /wafs/check_connection).
        """
        payload = config_data.model_dump(exclude_none=True, by_alias=True, mode='json')
        response_data = await self._client._arequest("POST", "issue_trackers/check_connection", json_data=payload)
        if not isinstance(response_data, dict): raise AcunetixError("Async: Unexpected response for check_connection_new.")
        return IssueTrackerConnectionStatus(**response_data)

    async def check_projects_new(self, config_data: IssueTrackerConfig) -> IssueTrackerProjects:
        payload = config_data.model_dump(exclude_none=True, by_alias=True, mode='json')
        response_data = await self._client._arequest("POST", "issue_trackers/check_projects", json_data=payload)
        if not isinstance(response_data, dict): raise AcunetixError("Async: Unexpected response for check_projects_new.")
        return IssueTrackerProjects(**response_data)

    async def check_issue_types_new(self, config_data: IssueTrackerConfig) -> IssueTrackerIssueTypes:
        payload = config_data.model_dump(exclude_none=True, by_alias=True, mode='json')
        response_data = await self._client._arequest("POST", "issue_trackers/check_issue_types", json_data=payload)
        if not isinstance(response_data, dict): raise AcunetixError("Async: Unexpected response for check_issue_types_new.")
        return IssueTrackerIssueTypes(**response_data)

    async def get_collections_new(self, config_data: IssueTrackerConfig) -> IssueTrackerCollections:
        payload = config_data.model_dump(exclude_none=True, by_alias=True, mode='json')
        response_data = await self._client._arequest("POST", "issue_trackers/collections", json_data=payload)
        if not isinstance(response_data, dict): raise AcunetixError("Async: Unexpected response for get_collections_new.")
        return IssueTrackerCollections(**response_data)

    async def get_custom_fields_new(self, config_data: IssueTrackerConfig) -> IssueTrackerCustomFields:
        payload = config_data.model_dump(exclude_none=True, by_alias=True, mode='json')
        response_data = await self._client._arequest("POST", "issue_trackers/custom_fields", json_data=payload)
        if not isinstance(response_data, dict): raise AcunetixError("Async: Unexpected response for get_custom_fields_new.")
        return IssueTrackerCustomFields(**response_data)

    async def list(self) -> IssueTrackerList:
        response_data = await self._client._arequest("GET", "issue_trackers")
        if not isinstance(response_data, dict): raise AcunetixError("Async: Unexpected response for list issue trackers.")
        return IssueTrackerList(**response_data)

    async def create(self, entry_data: IssueTrackerEntry) -> Optional[str]:
        """
        Creates a new issue tracker entry asynchronously.
        API returns 201 Created. Expects Location header.
        Returns the Location header URL if available, otherwise None.
        """
        payload = entry_data.model_dump(exclude={"issue_tracker_id"}, exclude_none=True, by_alias=True, mode='json')
        raw_response = await self._client._arequest("POST", "issue_trackers", json_data=payload, return_raw_response=True)

        if hasattr(raw_response, "headers"):
            return raw_response.headers.get("Location")
        return None

    async def get(self, issue_tracker_id: str) -> IssueTrackerEntry:
        response_data = await self._client._arequest("GET", f"issue_trackers/{issue_tracker_id}")
        if not isinstance(response_data, dict): raise AcunetixError("Async: Unexpected response for get issue tracker entry.")
        return IssueTrackerEntry(**response_data)

    async def update(self, issue_tracker_id: str, entry_data: IssueTrackerEntry) -> None:
        payload = entry_data.model_dump(exclude={"issue_tracker_id"}, exclude_none=True, by_alias=True, mode='json')
        await self._client._arequest("PATCH", f"issue_trackers/{issue_tracker_id}", json_data=payload)

    async def delete(self, issue_tracker_id: str) -> None:
        await self._client._arequest("DELETE", f"issue_trackers/{issue_tracker_id}")

    async def check_connection(self, issue_tracker_id: str) -> IssueTrackerConnectionStatus:
        response_data = await self._client._arequest("GET", f"issue_trackers/{issue_tracker_id}/check_connection")
        if not isinstance(response_data, dict): raise AcunetixError("Async: Unexpected response for check_connection.")
        return IssueTrackerConnectionStatus(**response_data)

    async def get_collections(self, issue_tracker_id: str) -> IssueTrackerCollections:
        response_data = await self._client._arequest("GET", f"issue_trackers/{issue_tracker_id}/collections")
        if not isinstance(response_data, dict): raise AcunetixError("Async: Unexpected response for get_collections.")
        return IssueTrackerCollections(**response_data)

    async def get_custom_fields(self, issue_tracker_id: str) -> IssueTrackerCustomFields:
        response_data = await self._client._arequest("GET", f"issue_trackers/{issue_tracker_id}/custom_fields")
        if not isinstance(response_data, dict): raise AcunetixError("Async: Unexpected response for get_custom_fields.")
        return IssueTrackerCustomFields(**response_data)

    async def get_projects(self, issue_tracker_id: str) -> IssueTrackerProjects:
        response_data = await self._client._arequest("GET", f"issue_trackers/{issue_tracker_id}/projects")
        if not isinstance(response_data, dict): raise AcunetixError("Async: Unexpected response for get_projects.")
        return IssueTrackerProjects(**response_data)
        
    async def get_issue_types_by_project_id(self, issue_tracker_id: str, project_id: str) -> IssueTrackerIssueTypes:
        response_data = await self._client._arequest("GET", f"issue_trackers/{issue_tracker_id}/projects/{project_id}/issue_types")
        if not isinstance(response_data, dict): raise AcunetixError("Async: Unexpected response for get_issue_types_by_project_id.")
        return IssueTrackerIssueTypes(**response_data)

    async def get_issue_types_by_project_qname(self, issue_tracker_id: str, project_id_qname: str) -> IssueTrackerIssueTypes:
        params = {"project_id": project_id_qname}
        response_data = await self._client._arequest("GET", f"issue_trackers/{issue_tracker_id}/projects/issue_types", params=params)
        if not isinstance(response_data, dict): raise AcunetixError("Async: Unexpected response for get_issue_types_by_project_qname.")
        return IssueTrackerIssueTypes(**response_data)
