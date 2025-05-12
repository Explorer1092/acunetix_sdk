from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, HttpUrl, field_validator
from enum import Enum # Added
import datetime
from .utils import parse_datetime_string
from .scan_profile import ScanningProfile
from .report_template import ReportTemplate

# Minimal Target model for embedding in ScanResponse
class EmbeddedTarget(BaseModel):
    target_id: Optional[str] = Field(None, description="目标ID")
    address: Optional[HttpUrl] = Field(None, description="目标地址")
    description: Optional[str] = Field(None, description="目标描述")
    type: Optional[str] = Field(None, description="目标类型") 
    criticality: Optional[int] = Field(None, description="目标重要性") 

class SeverityCounts(BaseModel):
    """Corresponds to #/definitions/SeverityCounts"""
    critical: Optional[int] = 0
    high: Optional[int] = 0
    medium: Optional[int] = 0
    low: Optional[int] = 0
    info: Optional[int] = 0

class Schedule(BaseModel):
    """Corresponds to #/definitions/Schedule"""
    disable: bool = Field(...)
    time_sensitive: Optional[bool] = Field(None) 
    history_limit: Optional[int] = Field(None)
    start_date: Optional[datetime.datetime] = Field(None)
    recurrence: Optional[str] = Field(None, pattern=r"^DTSTART:.*") 
    triggerable: Optional[bool] = Field(default=False)

    @field_validator("start_date", mode="before")
    @classmethod
    def _validate_start_date(cls, value: Any) -> Optional[datetime.datetime]:
        return parse_datetime_string(value)

class ScanInfoStatusEnum(str, Enum):
    SCHEDULED = "scheduled"
    QUEUED = "queued"
    STARTING = "starting"
    PROCESSING = "processing"
    ABORTING = "aborting"
    ABORTED = "aborted"
    PAUSING = "pausing"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    # RESUMING is not in API spec for ScanInfo.status, but present in ScanStatistics.status

class ScanInfo(BaseModel):
    """Corresponds to #/definitions/ScanInfo"""
    status: Optional[ScanInfoStatusEnum] = None 
    event_level: Optional[int] = None
    severity_counts: Optional[SeverityCounts] = None
    progress: Optional[int] = Field(None, ge=0, le=100)
    start_date: Optional[datetime.datetime] = Field(None, description="Session start date") 
    threat: Optional[int] = None
    scan_session_id: Optional[str] = Field(None, pattern=r"^[0-9a-fA-F-]{36}$") 
    acusensor: Optional[bool] = None

    @field_validator("start_date", mode="before")
    @classmethod
    def _validate_session_start_date(cls, value: Any) -> Optional[datetime.datetime]:
        return parse_datetime_string(value)


class ScanBase(BaseModel): 
    target_id: str = Field(..., pattern=r"^[0-9a-fA-F-]{36}$") 
    profile_id: str = Field(..., pattern=r"^[0-9a-fA-F-]{36}$") 
    report_template_id: Optional[str] = Field(None, pattern=r"^[0-9a-fA-F-]{36}$") 
    schedule: Schedule
    max_scan_time: Optional[int] = Field(default=0, description="In minutes, 0 for unlimited/system default")
    incremental: Optional[bool] = Field(default=False)

class ScanCreateRequest(ScanBase):
    """
    Request body for POST /scans (scheduling a scan).
    Corresponds to #/definitions/Scan in API spec.
    """
    pass 

class ScanUpdateRequest(BaseModel):
    """
    Request body for PATCH /scans/{scan_id}.
    All fields are optional for an update.
    Corresponds to #/definitions/Scan in API spec, but for PATCH.
    """
    target_id: Optional[str] = Field(None, pattern=r"^[0-9a-fA-F-]{36}$")
    profile_id: Optional[str] = Field(None, pattern=r"^[0-9a-fA-F-]{36}$")
    report_template_id: Optional[str] = Field(None, pattern=r"^[0-9a-fA-F-]{36}$")
    schedule: Optional[Schedule] = None
    max_scan_time: Optional[int] = Field(None, description="In minutes, 0 for unlimited/system default")
    incremental: Optional[bool] = Field(None)


class ScanResponse(ScanBase):
    """
    Response model for GET /scans/{scan_id} and items in GET /scans list.
    Corresponds to #/definitions/ScanItemResponse in API spec.
    """
    scan_id: str = Field(..., pattern=r"^[0-9a-fA-F-]{36}$") 
    next_run: Optional[datetime.datetime] = Field(None, description="Read-only: Next scheduled run")
    
    target: Optional[EmbeddedTarget] = None 
    criticality: Optional[int] = None
    profile_name: Optional[str] = None
    start_date: Optional[datetime.datetime] = Field(None, description="Actual scan start date-time")
    manual_intervention: Optional[bool] = None
    
    current_session: Optional[ScanInfo] = None
    previous_session: Optional[ScanInfo] = None 

    @field_validator("next_run", "start_date", mode="before")
    @classmethod
    def _validate_dates(cls, value: Any) -> Optional[datetime.datetime]:
        return parse_datetime_string(value)

class ScanResultItemResponse(BaseModel):
    """Corresponds to #/definitions/ScanResultItem"""
    scan_id: str = Field(..., pattern=r"^[0-9a-fA-F-]{36}$")
    result_id: str = Field(..., pattern=r"^[0-9a-fA-F-]{36}$")
    start_date: Optional[datetime.datetime] = None
    end_date: Optional[datetime.datetime] = None
    status: Optional[ScanInfoStatusEnum] = None # Reusing ScanInfoStatusEnum if applicable

    @field_validator("start_date", "end_date", mode="before")
    @classmethod
    def _validate_result_dates(cls, value: Any) -> Optional[datetime.datetime]:
        return parse_datetime_string(value)

class VulnerabilityBrief(BaseModel): 
    vuln_id: str 
    name: str
    severity: str 
    confidence: Optional[int] = None

class Vulnerability(VulnerabilityBrief): 
    description: Optional[str] = None
    details: Optional[str] = None
    impact: Optional[str] = None
    recommendation: Optional[str] = None

# --- Backwards-compatibility aliases ---
SchedulingOptions = Schedule
ScanCreate = ScanCreateRequest
Scan = ScanResponse
ScanUpdate = ScanUpdateRequest

class ScanBrief(ScanResponse):
    """兼容旧版 SDK 的简要扫描模型。"""
    pass

ScanSeverityCounts = SeverityCounts

ScanScanProfileBrief = ScanningProfile

ScanReportTemplateBrief = ReportTemplate

# --- Continuous Scan Models ---
class ContinuousScanItemResponse(BaseModel):
    """Corresponds to #/definitions/ContinuousScanItemResponse in API spec."""
    start_date: Optional[datetime.date] = None
    end_date: Optional[datetime.date] = None
    scan_type: Optional[str] = Field(None, description="扫描类型 (profile name 或 id)")
    status: Optional[str] = Field(None, description="持续扫描状态")

    @field_validator("start_date", "end_date", mode="before")
    @classmethod
    def _validate_dates(cls, value: Any) -> Optional[datetime.date]:
        if isinstance(value, str):
            try:
                return datetime.datetime.fromisoformat(value).date()
            except ValueError:
                return None
        return value
