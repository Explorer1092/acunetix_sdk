from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator
from enum import Enum
import datetime
from .utils import parse_datetime_string

class ReportFormat(str, Enum):
    PDF = "Pdf"
    HTML = "Html"
    CSV = "Csv"
    XML = "Xml"
    JSON = "Json"
    # Add other formats as supported by the API, check documentation for exact values

class ReportStatus(str, Enum):
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"

class ReportSourceListType(str, Enum):
    ALL_VULNERABILITIES = "all_vulnerabilities"
    TARGETS = "targets"
    GROUPS = "groups"
    SCANS = "scans"
    SCAN_RESULT = "scan_result"
    VULNERABILITIES = "vulnerabilities" # Top-level vulnerabilities
    SCAN_VULNERABILITIES = "scan_vulnerabilities" # Vulns from a specific scan session
    SCAN_PAIR = "scan_pair" # For comparison reports
    SCAN_RESULT_PAIR = "scan_result_pair" # For comparison reports

class ReportSource(BaseModel):
    """
    Corresponds to #/definitions/ReportSource in API spec.
    Defines the source for which a report is generated.
    """
    list_type: ReportSourceListType = Field(..., description="Type of IDs in id_list")
    id_list: List[str] = Field(..., description="List of IDs (e.g., scan_ids, target_ids)")
    description: Optional[str] = Field(None, description="Optional description for the source selection")

class Report(BaseModel):
    """
    Corresponds to #/definitions/Report in API spec.
    """
    report_id: str = Field(..., description="报告唯一标识符")
    template_id: str = Field(..., description="报告模板唯一标识符")
    template_name: Optional[str] = Field(None, description="报告模板名称")
    template_type: Optional[int] = Field(None, description="报告模板类型 (整数)")
    status: ReportStatus = Field(..., description="报告状态")
    generation_date: Optional[datetime.datetime] = Field(None, description="报告生成日期")
    source: Optional[ReportSource] = Field(None, description="报告来源")
    download: Optional[List[str]] = Field(default_factory=list, description="报告下载链接列表")

    @field_validator("generation_date", mode="before")
    @classmethod
    def _validate_timestamps(cls, value: Any) -> Optional[datetime.datetime]:
        return parse_datetime_string(value)


class ReportBrief(BaseModel):
    """
    简要报告信息，用于分页列表等场景。
    """
    report_id: str = Field(..., description="报告唯一标识符")
    template_name: Optional[str] = Field(None, description="报告模板名称")
    status: ReportStatus = Field(..., description="报告状态")
    generation_date: Optional[datetime.datetime] = Field(None, description="报告生成日期")

    @field_validator("generation_date", mode="before")
    @classmethod
    def _validate_timestamps(cls, value: Any) -> Optional[datetime.datetime]: # Ensure this validator is also here
        return parse_datetime_string(value)


class ReportCreate(BaseModel):
    """
    Payload for creating a new report.
    Corresponds to #/definitions/NewReport in API spec.
    """
    template_id: str = Field(..., description="报告模板唯一标识符")
    source: ReportSource = Field(..., description="报告来源")

class ReportIdList(BaseModel):
    """
    Corresponds to #/definitions/ReportIdList in API spec.
    Used for bulk deleting reports.
    """
    report_id_list: List[str] = Field(..., description="报告 UUID 列表")
