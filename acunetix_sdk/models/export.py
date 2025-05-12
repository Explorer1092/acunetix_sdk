from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, HttpUrl, field_validator, conlist
from enum import Enum
import datetime
from .utils import parse_datetime_string
from .report import ReportSourceListType # Reusing Enum
# from .pagination import PaginatedList, PaginationInfo # No longer needed for ExportList

class ExportTypeAcceptedSourceEnum(str, Enum): # Same as ReportSourceListType
    ALL_VULNERABILITIES = "all_vulnerabilities"
    TARGETS = "targets"
    GROUPS = "groups"
    SCANS = "scans"
    SCAN_RESULT = "scan_result"
    VULNERABILITIES = "vulnerabilities"
    SCAN_VULNERABILITIES = "scan_vulnerabilities"
    SCAN_PAIR = "scan_pair"
    SCAN_RESULT_PAIR = "scan_result_pair"

class ExportType(BaseModel):
    """Corresponds to #/definitions/ExportType in API spec."""
    export_id: str = Field(..., description="导出类型唯一标识符 (UUID)") # API 'export_id' is required
    name: Optional[str] = Field(None, description="导出类型名称")
    id: Optional[str] = Field(None, description="备用ID (UUID), API规范中存在但可能与export_id重复") 
    content_type: Optional[str] = Field(None, description="内容类型")
    accepted_sources: Optional[List[ExportTypeAcceptedSourceEnum]] = Field(default_factory=list, description="此模板接受的源类型列表")
    upload: Optional[bool] = Field(None, description="此导出类型是否涉及上传 (例如到WAF)")

class ExportTypesList(BaseModel):
    """Corresponds to #/definitions/ExportTypesList in API spec."""
    templates: Optional[List[ExportType]] = Field(default_factory=list, description="可用导出模板列表") # API spec uses "templates" as key

class ExportSource(BaseModel):
    """Corresponds to #/definitions/ExportSource in API spec."""
    list_type: ReportSourceListType = Field(..., description="id_list 中的 ID 类型") 
    id_list: Optional[conlist(str, max_length=500)] = Field(default_factory=list, description="ID 列表 (例如 scan_ids)")
    waf_id: Optional[str] = Field(None, description="WAF UUID, 如果导出到 WAF")
    # waf_name: Optional[str] = None # Removed as not in API spec

class NewExport(BaseModel):
    """
    Request body for POST /exports.
    Corresponds to #/definitions/NewExport in API spec.
    """
    export_id: str = Field(..., description="导出类型 UUID (来自 GET /export_types)") # This is the ExportType's export_id
    source: ExportSource

class ExportStatusEnum(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing" # Assuming, similar to reports
    COMPLETED = "completed"
    FAILED = "failed"
    # Add other statuses if API defines them

class Export(BaseModel):
    """
    Response model for export operations.
    Corresponds to #/definitions/Export in API spec.
    """
    # NOTE: The API documentation refers to this field as 'report_id'.
    # It likely represents the unique identifier of the export instance itself,
    # rather than a traditional report. The naming might be a legacy artifact or internal convention.
    export_id: Optional[str] = Field(None, alias="report_id", description="导出记录的唯一标识符 (UUID)") # API uses report_id, aliasing to export_id
    source: Optional[ExportSource] = None
    export_type_id: Optional[str] = Field(None, alias="template_id", description="使用的导出类型 UUID") # API uses template_id, aliasing
    template_name: Optional[str] = Field(None, description="导出类型的名称") 
    template_type: Optional[int] = Field(None, description="导出类型的类型 (整数, 含义不明确)") 
    generation_date: Optional[datetime.datetime] = None
    status: Optional[ExportStatusEnum] = Field(None, description="导出状态") 
    download: Optional[List[str]] = Field(default_factory=list, description="导出文件的下载链接列表")

    @field_validator("generation_date", mode="before")
    @classmethod
    def _validate_dates(cls, value: Any) -> Optional[datetime.datetime]:
        return parse_datetime_string(value)
    
    model_config = {"populate_by_name": True} # To allow aliases to work

class ExportIdList(BaseModel): 
    """Request body for POST /exports/delete."""
    # API spec for POST /exports/delete uses ReportIdList, which seems like an error.
    # This model assumes it should be a list of export IDs.
    # If API strictly requires ReportIdList, then models.report.ReportIdList should be used.
    export_id_list: List[str] = Field(..., description="要删除的导出 UUID 列表")
# Removed ExportList as GET /exports endpoint does not exist in the provided API spec.
