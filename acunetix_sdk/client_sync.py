# Synchronous Acunetix client 
from typing import Optional, Iterable, Dict, Any, Type, TypeVar, List

from .client_base import BaseAcunetixClient
from .http_clients import SyncHTTPClient
from .resources.targets import TargetsSyncResource
from .resources.scans import ScansSyncResource
from .resources.reports import ReportsSyncResource
from .resources.users import UsersSyncResource
from .resources.scan_profiles import ScanProfilesSyncResource
from .resources.report_templates import ReportTemplatesSyncResource
from .resources.notifications import NotificationsSyncResource
from .resources.target_groups import TargetGroupsSyncResource # Added TargetGroupsSyncResource
# Import all new sync resource classes
from .resources.user_groups import UserGroupsSyncResource
from .resources.roles import RolesSyncResource
from .resources.agents_config import AgentsConfigSyncResource
from .resources.excluded_hours import ExcludedHoursSyncResource
from .resources.issue_trackers import IssueTrackersSyncResource
from .resources.exports import ExportsSyncResource
from .resources.vulnerabilities import VulnerabilitiesSyncResource
from .resources.wafs import WafsSyncResource
from .resources.workers import WorkersSyncResource

from .models.pagination import PaginatedList
# Update model imports to reflect actual response types from resource methods
from .models.target import TargetResponse
from .models.scan import ScanResponse, ScanResultItemResponse
from .models.report import Report
from .models.user import UserResponse as User, UserGroupDetails, RoleDetails # Assuming UserResponse exists or User is the detailed one
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

from .errors import AcunetixError
import logging # Added import for logging type hint


T = TypeVar('T') # Generic type for list items

class AcunetixSyncClient(BaseAcunetixClient[SyncHTTPClient]):
    """Synchronous client for interacting with the Acunetix API."""
    def __init__(
        self,
        api_key: str,
        endpoint: str,
        *, # Use keyword-only arguments for options
        http_client: Optional[SyncHTTPClient] = None,
        verify_ssl: bool = False,
        timeout: Optional[int] = 30,
        logger: Optional[logging.Logger] = None, # Added logger parameter
    ):
        """
        Initializes the synchronous Acunetix API client.

        :param api_key: Your Acunetix API key.
        :param endpoint: The Acunetix API endpoint (e.g., 'your-acunetix.com:3443').
        :param http_client: Optional pre-configured SyncHTTPClient instance.
        :param verify_ssl: Whether to verify SSL certificates (used if http_client is not provided).
        :param timeout: Default timeout in seconds for HTTP requests (used if http_client is not provided).
        :param logger: Optional logger instance for the client to use.
        """
        # First, determine the logger to be used. BaseAcunetClient will also use this.
        # If a logger is passed, it will be used; otherwise, BaseAcunetixClient will create a default one.
        # We need this logger instance to potentially pass to a new SyncHTTPClient.
        
        # Initialize the logger in the base class first, so self.logger is available.
        # This requires a slight re-think if http_client is created *before* super().__init__
        # Let's pass the logger to super, and if http_client is None, create it *after* super()
        # and then re-assign self.http_client. This is a bit clunky.

        # Alternative: Determine logger, create http_client if needed, then call super.
        actual_logger = logger
        if not actual_logger:
            # If no logger is passed, we'll let BaseAcunetixClient create its default.
            # For SyncHTTPClient, if it's created here, it will also create its own default
            # unless we pass one. To ensure they share the *same* default logger if none is provided
            # to AcunetixSyncClient, we'd need more coordination or pass the name.
            # For now, if logger is None, SyncHTTPClient will create its own "acunetix_sdk.http" logger.
            # If logger is provided to AcunetixSyncClient, we pass it to SyncHTTPClient.
            pass # Base class will handle creating a default logger if 'logger' is None

        if http_client:
            client_to_use = http_client
        else:
            # Pass the 'logger' (which might be None) to SyncHTTPClient.
            # SyncHTTPClient's __init__ will then use it or create its own default.
            client_to_use = SyncHTTPClient(verify_ssl=verify_ssl, logger_instance=actual_logger)
            
        super().__init__(
            api_key=api_key, endpoint=endpoint, 
            http_client=client_to_use, 
            default_timeout=timeout,
            logger=actual_logger # Pass the determined logger to base class
        )
        # Now self.logger is set by BaseAcunetixClient.
        # If client_to_use was created locally and actual_logger was None,
        # client_to_use.logger and self.logger might be different instances (though possibly same name if default logic aligns).
        # To ensure they are the *same* instance if one is created by default:
        if not http_client and not logger: # If both were None, Base created self.logger, http_client created its own
             client_to_use.logger = self.logger # Make them use the same logger instance from Base

        # Initialize resource namespaces
        self.targets: TargetsSyncResource = TargetsSyncResource(self)
        self.scans: ScansSyncResource = ScansSyncResource(self)
        self.reports: ReportsSyncResource = ReportsSyncResource(self)
        self.users: UsersSyncResource = UsersSyncResource(self)
        self.scan_profiles: ScanProfilesSyncResource = ScanProfilesSyncResource(self)
        self.report_templates: ReportTemplatesSyncResource = ReportTemplatesSyncResource(self)
        self.notifications: NotificationsSyncResource = NotificationsSyncResource(self)
        self.user_groups: UserGroupsSyncResource = UserGroupsSyncResource(self)
        self.roles: RolesSyncResource = RolesSyncResource(self)
        self.agents_config: AgentsConfigSyncResource = AgentsConfigSyncResource(self)
        self.excluded_hours: ExcludedHoursSyncResource = ExcludedHoursSyncResource(self)
        self.issue_trackers: IssueTrackersSyncResource = IssueTrackersSyncResource(self)
        self.exports: ExportsSyncResource = ExportsSyncResource(self)
        self.vulnerabilities: VulnerabilitiesSyncResource = VulnerabilitiesSyncResource(self)
        self.wafs: WafsSyncResource = WafsSyncResource(self)
        self.workers: WorkersSyncResource = WorkersSyncResource(self)
        self.target_groups: TargetGroupsSyncResource = TargetGroupsSyncResource(self) # Added target_groups

    def _list_all_generic(self, list_method, **kwargs) -> Iterable[T]:
        """Generic helper to iterate through all pages of a list endpoint."""
        # No need for model_cls and items_key if list_method returns PaginatedList[T]
        cursor = None
        page_limit = kwargs.pop("page_limit", 100)
        while True:
            # The list_method now returns PaginatedList[T]
            paginated_response: PaginatedList[T] = list_method(cursor=cursor, limit=page_limit, **kwargs)
            
            # Pydantic ensures paginated_response.items is List[T]
            items = paginated_response.items
            for item in items:
                yield item

            cursor = paginated_response.pagination.next_cursor
            if not cursor or not items: # Stop if no next cursor or page was empty
                break

    # Updated list_all_* methods with correct return types
    def list_all_targets(self, query: Optional[str] = None, sort: Optional[str] = None, page_limit: int = 100) -> Iterable[TargetResponse]:
        return self._list_all_generic(self.targets.list, query=query, sort=sort, page_limit=page_limit)

    def list_all_scans(self, target_id: Optional[str] = None, query: Optional[str] = None, sort: Optional[str] = None, page_limit: int = 100) -> Iterable[ScanResponse]:
        return self._list_all_generic(self.scans.list, target_id=target_id, query=query, sort=sort, page_limit=page_limit)
    
    def list_all_scan_results(self, scan_id: str, sort: Optional[str] = None, page_limit: int = 100) -> Iterable[ScanResultItemResponse]:
        return self._list_all_generic(self.scans.get_results, scan_id=scan_id, sort=sort, page_limit=page_limit)

    def list_all_scan_vulnerabilities(self, scan_id: str, result_id: str, query: Optional[str] = None, sort: Optional[str] = None, page_limit: int = 100) -> Iterable[Vulnerability]:
        return self._list_all_generic(self.scans.get_vulnerabilities, scan_id=scan_id, result_id=result_id, query=query, sort=sort, page_limit=page_limit)

    def list_all_reports(self, query: Optional[str] = None, sort: Optional[str] = None, page_limit: int = 100) -> Iterable[Report]:
        return self._list_all_generic(self.reports.list, query=query, sort=sort, page_limit=page_limit)

    def list_all_users(self, query: Optional[str] = None, sort: Optional[str] = None, page_limit: int = 100) -> Iterable[User]: # Assuming User is the detailed model
        return self._list_all_generic(self.users.list, query=query, sort=sort, page_limit=page_limit)

    def list_all_scan_profiles(self, query: Optional[str] = None, sort: Optional[str] = None, page_limit: int = 100) -> Iterable[ScanningProfile]:
        return self._list_all_generic(self.scan_profiles.list, query=query, sort=sort, page_limit=page_limit)

    def list_all_report_templates(self, query: Optional[str] = None, sort: Optional[str] = None, page_limit: int = 100) -> Iterable[ReportTemplate]:
        # Note: report_templates.list might not support query/sort if API doesn't
        return self._list_all_generic(self.report_templates.list, query=query, sort=sort, page_limit=page_limit)

    def list_all_notifications(self, query: Optional[str] = None, sort: Optional[str] = None, unread: Optional[bool] = None, page_limit: int = 100) -> Iterable[Notification]:
        return self._list_all_generic(self.notifications.list, query=query, sort=sort, unread=unread, page_limit=page_limit)

    def list_all_user_groups(self, query: Optional[str] = None, sort: Optional[str] = None, extended: Optional[bool] = None, page_limit: int = 100) -> Iterable[UserGroupDetails]:
        return self._list_all_generic(self.user_groups.list, query=query, sort=sort, extended=extended, page_limit=page_limit)

    def list_all_roles(self, query: Optional[str] = None, sort: Optional[str] = None, extended: Optional[bool] = None, page_limit: int = 100) -> Iterable[RoleDetails]:
        return self._list_all_generic(self.roles.list, query=query, sort=sort, extended=extended, page_limit=page_limit)
    
    def list_all_vulnerabilities(self, query: Optional[str] = None, sort: Optional[str] = None, page_limit: int = 100) -> Iterable[Vulnerability]:
        return self._list_all_generic(self.vulnerabilities.list, query=query, sort=sort, page_limit=page_limit)

    def list_all_vulnerability_types(self, view: Optional[str] = "default", query: Optional[str] = None, sort: Optional[str] = None, page_limit: int = 100) -> Iterable[VulnerabilityTypeTargetsCountResponseItem]:
        return self._list_all_generic(self.vulnerabilities.list_types, view=view, query=query, sort=sort, page_limit=page_limit)

    # Non-paginated list_all style methods for resources that don't use PaginatedList
    def get_all_excluded_hours_profiles(self) -> List[ExcludedHoursProfile]:
        return self.excluded_hours.list().values or []

    def get_all_issue_trackers(self) -> List[IssueTrackerEntry]:
        return self.issue_trackers.list().issue_trackers or []
        
    def get_all_export_types(self) -> List[ExportType]:
        # The API response for export_types has "templates" key, aliased to "export_types" in model
        return self.exports.list_export_types().export_types or []

    def get_all_wafs(self) -> List[WAFEntry]:
        return self.wafs.list().wafs or []

    def get_all_workers(self) -> List[Worker]:
        return self.workers.list().workers or []

    def __enter__(self) -> "AcunetixSyncClient":
        """Enter the runtime context related to this object."""
        # Perform any setup if needed, though http_client is already initialized.
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the runtime context related to this object and close resources."""
        self.close()

    def close(self):
        """Closes the underlying HTTP session. Useful for cleanup in some contexts."""
        if hasattr(self.http_client, 'close') and callable(self.http_client.close):
            self.http_client.close()
