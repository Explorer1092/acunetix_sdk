# This file makes src/acunetix_sdk a Python package 

"""
Acunetix SDK for Python
=======================

A Python client for the Acunetix API, supporting both synchronous and asynchronous operations.

Usage:

Synchronous Client:
-------------------
```python
from acunetix_sdk import AcunetixSyncClient, AcunetixError, TargetBrief

client = AcunetixSyncClient(api_key="YOUR_API_KEY", endpoint="your-acunetix.com:3443")

try:
    print("Listing all targets:")
    for target in client.list_all_targets(page_limit=5):
        print(f"  Target ID: {target.target_id}, Address: {target.address}")
except AcunetixError as e:
    print(f"API Error: {e}")
finally:
    client.close()
```

Asynchronous Client:
--------------------
```python
import asyncio
from acunetix_sdk import AcunetixAsyncClient, AcunetixError, TargetBrief

async def main():
    client = AcunetixAsyncClient(api_key="YOUR_API_KEY", endpoint="your-acunetix.com:3443")
    try:
        print("Listing all targets asynchronously:")
        async for target in client.list_all_targets(page_limit=5):
            print(f"  Target ID: {target.target_id}, Address: {target.address}")
    except AcunetixError as e:
        print(f"API Error: {e}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
```

"""

__version__ = "0.1.2" 

# Core Clients
from .client_sync import AcunetixSyncClient
from .client_async import AcunetixAsyncClient

# Error Classes
from .errors import (
    AcunetixError,
    AuthenticationError,
    NotFoundError,
    BadRequestError,
    RateLimitError,
    ServerError
)

# Key Models (example, can be expanded)
from .models.target import Target, TargetCreate, TargetUpdate, TargetBrief, TargetConfig, ScanSpeedEnum as ScanSpeed, TargetSettings, CustomHeader  # Import ScanSpeedEnum as ScanSpeed, Added TargetSettings, CustomHeader
from .models.scan import (
    Scan, ScanBrief, ScanCreate, ScanUpdate, ScanSeverityCounts, 
    SchedulingOptions, ScanScanProfileBrief, ScanReportTemplateBrief, # ScanSpeed removed from here
    Vulnerability, VulnerabilityBrief
)
from .models.report import Report, ReportBrief, ReportCreate, ReportFormat, ReportStatus, ReportSource
from .models.user import User, UserBrief, UserCreate, UserUpdate
from .models.scan_profile import ScanProfile, ScanProfileCreateRequest, ScanProfileType, ScanProfileUpdateRequest # Changed ScanProfileCreate to ScanProfileCreateRequest, Added ScanProfileUpdateRequest
from .models.report_template import ReportTemplate, ReportTemplateType # Removed ReportTemplateCreateRequest, ReportTemplateUpdateRequest
from .models.notification import Notification, NotificationData, NotificationType, NotificationCreateRequest, NotificationUpdateRequest, NotificationScope, NotificationEvent # Added missing imports
from .models.target_group import TargetGroup, TargetGroupCreateRequest, TargetGroupUpdateRequest, TargetGroupBrief, TargetGroupListResponse # Added TargetGroup models
from .models.excluded_hours import ExcludedHoursProfile, ExcludedHoursProfilesList # Added ExcludedHours models
from .models.issue_tracker import ( # Added IssueTracker models
    IssueTrackerEntry, IssueTrackerConfig, IssueTrackerAuthKind, IssueTrackerPlatform,
    IssueTrackerList, IssueTrackerConnectionStatus
)
from .models.waf import ( # Added WAF models
    WAFEntry, WAFConfig, WAFPlatform, WAFScope, WAFRegion, WAFsList,
    WAFConnectionStatus, WAFProxyType, WAFProxy
)
from .models.agent import AgentRegistrationToken, NewAgentRegistrationToken, AgentsConfig # Added Agent models

__all__ = [
    # Clients
    "AcunetixSyncClient",
    "AcunetixAsyncClient",
    # Errors
    "AcunetixError",
    "AuthenticationError",
    "NotFoundError",
    "BadRequestError",
    "RateLimitError",
    "ServerError",
    # Models (Export more as they are added)
    "Target",
    "TargetCreate",
    "TargetUpdate",
    "TargetBrief",
    "TargetConfig",
    "TargetSettings", # Added
    "CustomHeader",   # Added
    # Scan Models
    "Scan",
    "ScanBrief",
    "ScanCreate",
    "ScanUpdate",
    "ScanSeverityCounts",
    "SchedulingOptions",
    "ScanScanProfileBrief",
    "ScanReportTemplateBrief",
    "ScanSpeed",
    "Vulnerability",
    "VulnerabilityBrief",
    # Report Models
    "Report",
    "ReportBrief",
    "ReportCreate",
    "ReportFormat",
    "ReportStatus",
    "ReportSource",
    # User Models
    "User",
    "UserBrief",
    "UserCreate",
    "UserUpdate",
    # Scan Profile Models
    "ScanProfile",
    "ScanProfileCreateRequest", # Changed from ScanProfileCreate
    "ScanProfileUpdateRequest", # Added
    "ScanProfileType",
    # Report Template Models
    "ReportTemplate",
    "ReportTemplateType",
    # Notification Models
    "Notification",
    "NotificationData",
    "NotificationType",
    "NotificationCreateRequest", # Added
    "NotificationUpdateRequest", # Added
    "NotificationScope",         # Added
    "NotificationEvent",         # Added
    # Target Group Models
    "TargetGroup",
    "TargetGroupCreateRequest",
    "TargetGroupUpdateRequest",
    "TargetGroupBrief",
    "TargetGroupListResponse",
    # Excluded Hours Models
    "ExcludedHoursProfile",
    "ExcludedHoursProfilesList",
    # Issue Tracker Models
    "IssueTrackerEntry",
    "IssueTrackerConfig",
    "IssueTrackerAuthKind",
    "IssueTrackerPlatform",
    "IssueTrackerList",
    "IssueTrackerConnectionStatus",
    # WAF Models
    "WAFEntry",
    "WAFConfig",
    "WAFPlatform",
    "WAFScope",
    "WAFRegion",
    "WAFsList",
    "WAFConnectionStatus",
    "WAFProxyType",
    "WAFProxy",
    # Agent Models
    "AgentRegistrationToken",
    "NewAgentRegistrationToken",
    "AgentsConfig",
]
