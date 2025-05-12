# acunetix_sdk/models/__init__.py

# Common utility models
from .pagination import PaginatedList, PaginationInfo
from .common_settings import (
    UserCredentials,
    SiteLogin, SiteLoginKind,
    SSHCredentials, SSHCredentialsKind,
    ProxySettings, ProxyProtocol,
    OtpSettings, OtpType, OtpAlgorithm,
    ApiCustomCookie,
    FileUploadDescriptor, UploadLocationResponse, UploadedFile, UploadedFilesResponse,
    # LoginSequenceStep, CrawlSettings, CustomHeader, Cookie # Keep if used elsewhere, or remove if fully replaced
)

# Agent related models
from .agent import AgentRegistrationToken, NewAgentRegistrationToken

# Excluded Hours models
from .excluded_hours import ExcludedHoursProfile, ExcludedHoursProfilesList

# Export models
from .export import (
    ExportType, ExportTypesList,
    ExportSource, NewExport, Export, ExportIdList
)

# Issue Tracker models
from .issue_tracker import (
    IssueTrackerAuthKind, IssueTrackerAuth,
    IssueTrackerCollection, IssueTrackerCollections,
    IssueTrackerCustomField, IssueTrackerCustomFields,
    IssueTrackerProject, IssueTrackerProjects,
    IssueTrackerIssueType, IssueTrackerIssueTypes,
    IssueTrackerPlatform, IssueTrackerProxyType, IssueTrackerProxy,
    IssueTrackerCustomFieldEntry, IssueTrackerConfig,
    IssueTrackerConnectionStatus, IssueTrackerEntry, IssueTrackerList
)

# Notification models
from .notification import (
    NotificationType, NotificationData, Notification, NotificationIdList
)

# Report models
from .report import (
    ReportStatus, ReportSource, Report, ReportCreate, ReportIdList
)

# Report Template models
from .report_template import ReportTemplate

# Scan models
from .scan import (
    EmbeddedTarget, SeverityCounts as ScanSeverityCounts, # Alias to avoid clash if SeverityCounts is also top-level
    Schedule, ScanInfo,
    ScanBase, ScanCreateRequest, ScanUpdateRequest, ScanResponse,
    ScanResultItemResponse,
    ContinuousScanItemResponse  # 新增
)

# Scan Profile models
from .scan_profile import ScanningProfile

# Target models
from .target import (
    SeverityCounts, Link, ScanAuthorizationInfo, # Common components used by TargetResponse
    TargetBase, TargetCreateRequest, TargetUpdateRequest, TargetResponse,
    AddTargetsDescriptor, TargetIdList, TargetConfigurationData,
    ContinuousScanMode, SensorType, SensorSecretContainer,
    AllowedHost, AllowedHosts, TargetIdContainer,
    ExcludedPathList, ExcludedPathListUpdate, TargetGroupIdList,
    Technology, TechnologyVersion, UpgradeVersion # TechnologiesListResponse is handled by PaginatedList
)

# User and User Group models
from .user import (
    RoleMapping, RoleMappingCreate,
    UserBrief, User, UserCreate, UserUpdate, ChildUserIdList,
    UserGroupStats, UserGroup, UserGroupDetails,
    UserToUserGroupDetails,
    RoleMappingList, RoleMappingIdList, UserGroupRoleMappings,
    RoleStats, Role, RoleDetails, # Role related models
    PermissionDetailEntry, PermissionsList # Permission related models
)

# Vulnerability models
from .vulnerability import (
    VulnerabilityStatus, VulnerabilityRecheck, VulnerabilitiesRecheck,
    Vulnerability, VulnerabilityTypeDetails, VulnerabilityDetails,
    IntegrationsVulnerabilityIdList, CreateIssuesViaIntegrationsReportLine,
    CreateIssuesViaIntegrationsResponse,
    VulnerabilityGroupItem, VulnerabilityGroupsResponse,
    VulnerabilityType, VulnerabilityTypeTargetsCountResponseItem,
    VulnerabilityTypeSessionsCountResponseItem  # ensure list
)

# WAF models
from .waf import (
    WAFPlatform, WAFScope, WAFRegion, WAFProxyType, WAFProxy,
    WAFConfig, WAFConnectionStatus, WAFEntry, WAFsList
)

# Worker models
from .worker import (
    WorkerScanningApp, WorkerStatus, WorkerAuthorization,
    Worker, WorkerList, WorkerExtended, WorkerDescription, WorkerIdList,
    EmptyObject
)

# Target Group models
from .target_group import TargetGroup, TargetGroupIdList, TargetGroupListResponse


__all__ = [
    # Pagination
    "PaginatedList", "PaginationInfo",
    # Common Settings
    "UserCredentials", "SiteLogin", "SiteLoginKind", "SSHCredentials", "SSHCredentialsKind",
    "ProxySettings", "ProxyProtocol", "OtpSettings", "OtpType", "OtpAlgorithm", "ApiCustomCookie",
    "FileUploadDescriptor", "UploadLocationResponse", "UploadedFile", "UploadedFilesResponse",
    # Agent
    "AgentRegistrationToken", "NewAgentRegistrationToken",
    # Excluded Hours
    "ExcludedHoursProfile", "ExcludedHoursProfilesList",
    # Export
    "ExportType", "ExportTypesList", "ExportSource", "NewExport", "Export", "ExportIdList",
    # Issue Tracker
    "IssueTrackerAuthKind", "IssueTrackerAuth", "IssueTrackerCollection", "IssueTrackerCollections",
    "IssueTrackerCustomField", "IssueTrackerCustomFields", "IssueTrackerProject", "IssueTrackerProjects",
    "IssueTrackerIssueType", "IssueTrackerIssueTypes", "IssueTrackerPlatform", "IssueTrackerProxyType",
    "IssueTrackerProxy", "IssueTrackerCustomFieldEntry", "IssueTrackerConfig", "IssueTrackerConnectionStatus",
    "IssueTrackerEntry", "IssueTrackerList",
    # Notification
    "NotificationType", "NotificationData", "Notification", "NotificationIdList",
    # Report
    "ReportStatus", "ReportSource", "Report", "ReportCreate", "ReportIdList",
    # Report Template
    "ReportTemplate",
    # Scan
    "EmbeddedTarget", "ScanSeverityCounts", "Schedule", "ScanInfo", "ScanBase",
    "ScanCreateRequest", "ScanUpdateRequest", "ScanResponse", "ScanResultItemResponse",
    "ContinuousScanItemResponse",
    # Scan Profile
    "ScanningProfile",
    # Target
    "SeverityCounts", "Link", "ScanAuthorizationInfo", "TargetBase", "TargetCreateRequest",
    "TargetUpdateRequest", "TargetResponse", "AddTargetsDescriptor", "TargetIdList",
    "TargetConfigurationData", "ContinuousScanMode", "SensorType", "SensorSecretContainer",
    "AllowedHost", "AllowedHosts", "TargetIdContainer", "ExcludedPathList", "ExcludedPathListUpdate",
    "TargetGroupIdList", "Technology", "TechnologyVersion", "UpgradeVersion",
    # Target Group
    "TargetGroup", "TargetGroupListResponse", # TargetGroupIdList is already included above
    # User & User Group & Role
    "RoleMapping", "RoleMappingCreate", "UserBrief", "User", "UserCreate", "UserUpdate", "ChildUserIdList",
    "UserGroupStats", "UserGroup", "UserGroupDetails", "UserToUserGroupDetails", "RoleMappingList",
    "RoleMappingIdList", "UserGroupRoleMappings", "RoleStats", "Role", "RoleDetails",
    "PermissionDetailEntry", "PermissionsList",
    # Vulnerability
    "VulnerabilityStatus", "VulnerabilityRecheck", "VulnerabilitiesRecheck", "Vulnerability",
    "VulnerabilityTypeDetails", "VulnerabilityDetails", "IntegrationsVulnerabilityIdList",
    "CreateIssuesViaIntegrationsReportLine", "CreateIssuesViaIntegrationsResponse",
    "VulnerabilityGroupItem", "VulnerabilityGroupsResponse", "VulnerabilityType",
    "VulnerabilityTypeTargetsCountResponseItem", "VulnerabilityTypeSessionsCountResponseItem",
    # WAF
    "WAFPlatform", "WAFScope", "WAFRegion", "WAFProxyType", "WAFProxy", "WAFConfig",
    "WAFConnectionStatus", "WAFEntry", "WAFsList",
    # Worker
    "WorkerScanningApp", "WorkerStatus", "WorkerAuthorization", "Worker", "WorkerList",
    "WorkerExtended", "WorkerDescription", "WorkerIdList", "EmptyObject",
]
