# Asynchronous Acunetix client 
from typing import Optional, AsyncIterable, Dict, Any, Type, TypeVar, List
import asyncio # For polling
import time # For polling timeout
import logging # Added

from .client_base import BaseAcunetixClient
from .http_clients import AsyncHTTPClient
from .resources.targets import TargetsAsyncResource
from .resources.scans import ScansAsyncResource
from .resources.reports import ReportsAsyncResource
from .resources.users import UsersAsyncResource
from .resources.scan_profiles import ScanProfilesAsyncResource
from .resources.report_templates import ReportTemplatesAsyncResource
from .resources.notifications import NotificationsAsyncResource
from .resources.target_groups import TargetGroupsAsyncResource # Added TargetGroupsAsyncResource
# Import all new async resource classes
from .resources.user_groups import UserGroupsAsyncResource
from .resources.roles import RolesAsyncResource
from .resources.agents_config import AgentsConfigAsyncResource
from .resources.excluded_hours import ExcludedHoursAsyncResource
from .resources.issue_trackers import IssueTrackersAsyncResource
from .resources.exports import ExportsAsyncResource
from .resources.vulnerabilities import VulnerabilitiesAsyncResource
from .resources.wafs import WafsAsyncResource
from .resources.workers import WorkersAsyncResource

from .models.pagination import PaginatedList
# Update model imports to reflect actual response types from resource methods
from .models.target import TargetResponse
from .models.scan import ScanResponse, ScanResultItemResponse
from .models.report import Report, ReportStatus # ReportStatus used in TERMINAL_REPORT_STATUSES
from .models.user import UserResponse as User, UserGroupDetails, RoleDetails # Assuming UserResponse or User is detailed
from .models.scan_profile import ScanningProfile
from .models.report_template import ReportTemplate
from .models.notification import Notification
from .models.vulnerability import Vulnerability, VulnerabilityDetails, VulnerabilityTypeTargetsCountResponseItem, VulnerabilityGroupsResponse
from .models.agent import AgentRegistrationToken
from .models.excluded_hours import ExcludedHoursProfilesList, ExcludedHoursProfile
from .models.issue_tracker import IssueTrackerList, IssueTrackerEntry
from .models.export import ExportTypesList, Export, ExportType
from .models.waf import WAFsList, WAFEntry
from .models.worker import WorkerList, Worker

from .errors import AcunetixError, NotFoundError


T = TypeVar('T') # Generic type for list items
logger = logging.getLogger(__name__)

TERMINAL_SCAN_STATUSES = {"completed", "aborted", "failed"}
TERMINAL_REPORT_STATUSES = {ReportStatus.COMPLETED, ReportStatus.FAILED}

class AcunetixAsyncClient(BaseAcunetixClient[AsyncHTTPClient]):
    """Asynchronous client for interacting with the Acunetix API."""
    def __init__(
        self,
        api_key: str,
        endpoint: str,
        *, # Use keyword-only arguments for options
        http_client: Optional[AsyncHTTPClient] = None,
        verify_ssl: bool = False,
        timeout: Optional[int] = 30,
        logger: Optional[logging.Logger] = None, # Added logger parameter
    ):
        """
        Initializes the asynchronous Acunetix API client.

        :param api_key: Your Acunetix API key.
        :param endpoint: The Acunetix API endpoint (e.g., 'your-acunetix.com:3443').
        :param http_client: Optional pre-configured AsyncHTTPClient instance.
        :param verify_ssl: Whether to verify SSL certificates (used if http_client is not provided).
        :param timeout: Default timeout in seconds for HTTP requests (used if http_client is not provided).
        :param logger: Optional logger instance for the client to use.
        """
        actual_logger = logger

        if http_client:
            client_to_use = http_client
        else:
            client_to_use = AsyncHTTPClient(verify_ssl=verify_ssl, logger_instance=actual_logger)
            
        super().__init__(
            api_key=api_key, endpoint=endpoint, 
            http_client=client_to_use, 
            default_timeout=timeout,
            logger=actual_logger # Pass the determined logger to base class
        )
        
        if not http_client and not logger: 
             client_to_use.logger = self.logger

        # Initialize resource namespaces
        self.targets: TargetsAsyncResource = TargetsAsyncResource(self)
        self.scans: ScansAsyncResource = ScansAsyncResource(self)
        self.reports: ReportsAsyncResource = ReportsAsyncResource(self)
        self.users: UsersAsyncResource = UsersAsyncResource(self)
        self.scan_profiles: ScanProfilesAsyncResource = ScanProfilesAsyncResource(self)
        self.report_templates: ReportTemplatesAsyncResource = ReportTemplatesAsyncResource(self)
        self.notifications: NotificationsAsyncResource = NotificationsAsyncResource(self)
        self.user_groups: UserGroupsAsyncResource = UserGroupsAsyncResource(self)
        self.roles: RolesAsyncResource = RolesAsyncResource(self)
        self.agents_config: AgentsConfigAsyncResource = AgentsConfigAsyncResource(self)
        self.excluded_hours: ExcludedHoursAsyncResource = ExcludedHoursAsyncResource(self)
        self.issue_trackers: IssueTrackersAsyncResource = IssueTrackersAsyncResource(self)
        self.exports: ExportsAsyncResource = ExportsAsyncResource(self)
        self.vulnerabilities: VulnerabilitiesAsyncResource = VulnerabilitiesAsyncResource(self)
        self.wafs: WafsAsyncResource = WafsAsyncResource(self)
        self.workers: WorkersAsyncResource = WorkersAsyncResource(self)
        self.target_groups: TargetGroupsAsyncResource = TargetGroupsAsyncResource(self) # Added target_groups

    async def _list_all_generic_async(self, list_method, **kwargs) -> AsyncIterable[T]:
        """Generic async helper to iterate through all pages of a list endpoint."""
        cursor = None
        page_limit = kwargs.pop("page_limit", 100)
        while True:
            paginated_response: PaginatedList[T] = await list_method(cursor=cursor, limit=page_limit, **kwargs)
            items = paginated_response.items
            for item in items:
                yield item
            cursor = paginated_response.pagination.next_cursor
            if not cursor or not items:
                break

    # Updated list_all_* async methods with correct return types
    async def list_all_targets(self, query: Optional[str] = None, sort: Optional[str] = None, page_limit: int = 100) -> AsyncIterable[TargetResponse]:
        async for item in self._list_all_generic_async(self.targets.list, query=query, sort=sort, page_limit=page_limit):
            yield item

    async def list_all_scans(self, target_id: Optional[str] = None, query: Optional[str] = None, sort: Optional[str] = None, page_limit: int = 100) -> AsyncIterable[ScanResponse]:
        async for item in self._list_all_generic_async(self.scans.list, target_id=target_id, query=query, sort=sort, page_limit=page_limit):
            yield item
            
    async def list_all_scan_results(self, scan_id: str, sort: Optional[str] = None, page_limit: int = 100) -> AsyncIterable[ScanResultItemResponse]:
        async for item in self._list_all_generic_async(self.scans.get_results, scan_id=scan_id, sort=sort, page_limit=page_limit):
            yield item

    async def list_all_scan_vulnerabilities(self, scan_id: str, result_id: str, query: Optional[str] = None, sort: Optional[str] = None, page_limit: int = 100) -> AsyncIterable[Vulnerability]:
        async for item in self._list_all_generic_async(self.scans.get_vulnerabilities, scan_id=scan_id, result_id=result_id, query=query, sort=sort, page_limit=page_limit):
            yield item

    async def list_all_reports(self, query: Optional[str] = None, sort: Optional[str] = None, page_limit: int = 100) -> AsyncIterable[Report]:
        async for item in self._list_all_generic_async(self.reports.list, query=query, sort=sort, page_limit=page_limit):
            yield item

    async def list_all_users(self, query: Optional[str] = None, sort: Optional[str] = None, page_limit: int = 100) -> AsyncIterable[User]:
        async for item in self._list_all_generic_async(self.users.list, query=query, sort=sort, page_limit=page_limit):
            yield item

    async def list_all_scan_profiles(self, query: Optional[str] = None, sort: Optional[str] = None, page_limit: int = 100) -> AsyncIterable[ScanningProfile]:
        async for item in self._list_all_generic_async(self.scan_profiles.list, query=query, sort=sort, page_limit=page_limit):
            yield item

    async def list_all_report_templates(self, query: Optional[str] = None, sort: Optional[str] = None, page_limit: int = 100) -> AsyncIterable[ReportTemplate]:
        async for item in self._list_all_generic_async(self.report_templates.list, query=query, sort=sort, page_limit=page_limit):
            yield item

    async def list_all_notifications(self, query: Optional[str] = None, sort: Optional[str] = None, unread: Optional[bool] = None, page_limit: int = 100) -> AsyncIterable[Notification]: # Changed unread_only to unread
        async for item in self._list_all_generic_async(self.notifications.list, query=query, sort=sort, unread=unread, page_limit=page_limit):
            yield item

    async def list_all_user_groups(self, query: Optional[str] = None, sort: Optional[str] = None, extended: Optional[bool] = None, page_limit: int = 100) -> AsyncIterable[UserGroupDetails]:
        async for item in self._list_all_generic_async(self.user_groups.list, query=query, sort=sort, extended=extended, page_limit=page_limit):
            yield item
            
    async def list_all_roles(self, query: Optional[str] = None, sort: Optional[str] = None, extended: Optional[bool] = None, page_limit: int = 100) -> AsyncIterable[RoleDetails]:
        async for item in self._list_all_generic_async(self.roles.list, query=query, sort=sort, extended=extended, page_limit=page_limit):
            yield item

    async def list_all_vulnerabilities(self, query: Optional[str] = None, sort: Optional[str] = None, page_limit: int = 100) -> AsyncIterable[Vulnerability]:
        async for item in self._list_all_generic_async(self.vulnerabilities.list, query=query, sort=sort, page_limit=page_limit):
            yield item
            
    async def list_all_vulnerability_types(self, view: Optional[str] = "default", query: Optional[str] = None, sort: Optional[str] = None, page_limit: int = 100) -> AsyncIterable[VulnerabilityTypeTargetsCountResponseItem]:
        async for item in self._list_all_generic_async(self.vulnerabilities.list_types, view=view, query=query, sort=sort, page_limit=page_limit):
            yield item

    # Non-paginated list_all style methods for resources that don't use PaginatedList
    async def get_all_excluded_hours_profiles(self) -> List[ExcludedHoursProfile]:
        result = await self.excluded_hours.list()
        return result.values or []

    async def get_all_issue_trackers(self) -> List[IssueTrackerEntry]:
        result = await self.issue_trackers.list()
        return result.issue_trackers or []
        
    async def get_all_export_types(self) -> List[ExportType]:
        result = await self.exports.list_export_types()
        return result.export_types or [] # Assuming alias worked or key is export_types

    async def get_all_wafs(self) -> List[WAFEntry]:
        result = await self.wafs.list()
        return result.wafs or []

    async def get_all_workers(self) -> List[Worker]:
        result = await self.workers.list()
        return result.workers or []

    async def wait_for_scan_completion(self, scan_id: str, poll_interval: int = 5, timeout: int = 600) -> ScanResponse: # Return type updated
        """Polls the scan status until it reaches a terminal state (completed, aborted, failed) or times out.
        
        :param scan_id: The ID of the scan to wait for.
        :param poll_interval: How often to check the status (in seconds).
        :param timeout: Maximum time to wait (in seconds).
        :return: The final Scan object.
        :raises TimeoutError: If the scan doesn't complete within the timeout.
        :raises AcunetixError: If there's an API error during polling (e.g., scan not found initially).
        """
        start_time = time.monotonic()
        while True:
            if time.monotonic() - start_time > timeout:
                raise TimeoutError(f"Scan {scan_id} did not complete within {timeout} seconds.")
            
            try:
                scan = await self.scans.get(scan_id)
                if scan.status.lower() in TERMINAL_SCAN_STATUSES:
                    logger.info(f"Scan {scan_id} reached terminal state: {scan.status}")
                    return scan
                else:
                    logger.debug(f"Polling scan {scan_id}, current status: {scan.status}")
            except NotFoundError:
                 logger.error(f"Scan {scan_id} not found during polling.")
                 raise
            except AcunetixError as e:
                logger.warning(f"API Error polling scan {scan_id}: {e}. Retrying in {poll_interval}s.")
                # Continue polling after warning
                
            await asyncio.sleep(poll_interval)
            
    async def wait_for_report_completion(self, report_id: str, poll_interval: int = 5, timeout: int = 300) -> Report:
        """Polls the report status until it reaches a terminal state (completed, failed) or times out.
        
        :param report_id: The ID of the report to wait for.
        :param poll_interval: How often to check the status (in seconds).
        :param timeout: Maximum time to wait (in seconds).
        :return: The final Report object.
        :raises TimeoutError: If the report doesn't complete within the timeout.
        :raises AcunetixError: If there's an API error during polling.
        """
        start_time = time.monotonic()
        while True:
            if time.monotonic() - start_time > timeout:
                raise TimeoutError(f"Report {report_id} did not complete within {timeout} seconds.")
            
            try:
                report = await self.reports.get(report_id)
                if report.status in TERMINAL_REPORT_STATUSES:
                    logger.info(f"Report {report_id} reached terminal state: {report.status}")
                    return report
                else:
                    logger.debug(f"Polling report {report_id}, current status: {report.status}")
            except NotFoundError:
                 logger.error(f"Report {report_id} not found during polling.")
                 raise
            except AcunetixError as e:
                logger.warning(f"API Error polling report {report_id}: {e}. Retrying in {poll_interval}s.")
                
            await asyncio.sleep(poll_interval)

    async def __aenter__(self) -> "AcunetixAsyncClient":
        """Enter the asynchronous runtime context related to this object."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the asynchronous runtime context and close resources."""
        await self.close()

    async def close(self):
        """Closes the underlying HTTPX client session. Should be called for cleanup."""
        if hasattr(self.http_client, 'close') and callable(self.http_client.close):
            await self.http_client.close() # type: ignore # Already checked it's AsyncHTTPClient via Generic
