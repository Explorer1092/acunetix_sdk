from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, HttpUrl
from enum import Enum

class WorkerScanningApp(str, Enum):
    WVS = "wvs" # Web Vulnerability Scanner
    OVAS = "ovas" # OpenVAS / Network Scanner

class WorkerStatus(str, Enum):
    OFFLINE = "offline"
    ONLINE = "online"
    # Add other potential statuses if known

class WorkerAuthorization(str, Enum):
    PENDING = "pending"
    AUTHORIZED = "authorized"
    REJECTED = "rejected"
    DETACHED = "detached"

class Worker(BaseModel):
    """Corresponds to #/definitions/Worker in API spec."""
    scanning_app: WorkerScanningApp
    endpoint: str # Changed from HttpUrl to str to accommodate non-URL values like "Main Installation"
    description: Optional[str] = None
    worker_id: Optional[str] = Field(None, description="UUID, read-only for GET")
    status: Optional[WorkerStatus] = None
    authorization: Optional[WorkerAuthorization] = None
    app_version: Optional[str] = None
    license_status: Optional[str] = None # NOTE: API documentation does not provide enum values for this string field.
    targets: Optional[List[str]] = Field(default_factory=list, description="List of target UUIDs, read-only")
    notification_status: Optional[bool] = Field(None, description="Worker notification status (实际API响应中包含此字段)")

class WorkerList(BaseModel):
    """Corresponds to #/definitions/WorkerList in API spec."""
    workers: Optional[List[Worker]] = Field(default_factory=list)
    # Note: API spec does not show pagination for GET /workers.

class WorkerExtended(Worker):
    """Corresponds to #/definitions/WorkerExtended in API spec."""
    max_scans: Optional[int] = None
    current_scans: Optional[int] = None
    status_extra: Optional[Dict[str, Any]] = None # Generic object for extra status info

class WorkerDescription(BaseModel):
    """
    Corresponds to #/definitions/WorkerDescription in API spec.
    Used as request body for POST /workers/{worker_id}/rename.
    """
    description: str = Field(..., min_length=1, max_length=256)

class WorkerIdList(BaseModel):
    """
    Corresponds to #/definitions/WorkerIdList in API spec.
    Used as request body for POST /targets/{target_id}/configuration/workers.
    """
    worker_id_list: List[str] = Field(..., description="List of worker UUIDs")

class EmptyObject(BaseModel):
    """
    Corresponds to #/definitions/EmptyObject in API spec.
    Represents an empty JSON object {} for requests that require a body but no specific fields.
    """
    pass # Pydantic will serialize this to {}
