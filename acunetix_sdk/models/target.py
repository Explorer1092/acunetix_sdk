from typing import Optional, List, Any, Dict
from pydantic import BaseModel, HttpUrl, Field, field_validator # Removed validator
import datetime
from enum import Enum 
from .utils import parse_datetime_string
from .common_settings import ( 
    SiteLogin, 
    SSHCredentials, 
    ProxySettings, 
    UserCredentials, 
    OtpSettings,
    ApiCustomCookie
)

class SeverityCounts(BaseModel): 
    critical: Optional[int] = 0
    high: Optional[int] = 0
    medium: Optional[int] = 0
    low: Optional[int] = 0
    info: Optional[int] = 0

class Link(BaseModel): 
    rel: str
    href: HttpUrl

class ScanAuthorizationInfo(BaseModel): 
    url: Optional[HttpUrl] = None
    content: Optional[str] = None

class TargetTypeEnum(str, Enum):
    DEFAULT = "default"
    DEMO = "demo"
    NETWORK = "network"

class ScanSpeedEnum(str, Enum):
    FAST = "fast"
    MODERATE = "moderate"
    SLOW = "slow"
    SEQUENTIAL = "sequential"
    SLOWER = "slower"

class CaseSensitiveEnum(str, Enum):
    YES = "yes"
    NO = "no"
    AUTO = "auto"

class TechnologyEnum(str, Enum):
    ASP = "ASP"
    ASP_NET = "ASP.NET"
    PHP = "PHP"
    PERL = "Perl"
    JAVA_J2EE = "Java/J2EE"
    COLDFUSION_JRUN = "ColdFusion/Jrun"
    PYTHON = "Python"
    RAILS = "Rails"
    FRONTPAGE = "FrontPage"
    NODE_JS = "Node.js"

class CustomHeader(BaseModel):
    """自定义 HTTP 头部模型"""
    name: str = Field(..., description="头部名称")
    value: str = Field(..., description="头部值")

class TargetSettings(BaseModel):
    """目标特定设置模型"""
    user_agent: Optional[str] = Field(None, max_length=256, description="自定义 User-Agent")
    custom_headers: Optional[List[CustomHeader]] = Field(default_factory=list, description="自定义 HTTP 头部列表")
    # 可以根据 conftest.py 或 API 文档添加其他设置字段

# --- Target Request Models ---
class TargetBase(BaseModel):
    address: HttpUrl = Field(..., description="目标 URL 或主机名")
    description: Optional[str] = Field(default="", max_length=1024, description="目标描述")
    type: Optional[TargetTypeEnum] = Field(default=TargetTypeEnum.DEFAULT, description="目标类型") 
    criticality: Optional[int] = Field(default=10, description="目标重要性 (30, 20, 10, 0)") 

class TargetCreateRequest(TargetBase):
    """
    POST /targets 的请求体。
    对应 API规范中的 #/definitions/Target (用于请求)。
    """
    settings: Optional[TargetSettings] = Field(None, description="目标的特定扫描设置")

class TargetUpdateRequest(BaseModel):
    """
    PATCH /targets/{target_id} 的请求体。
    所有字段都是可选的。对应 API规范中的 #/definitions/Target (用于请求)。
    """
    address: Optional[HttpUrl] = Field(None, description="目标 URL 或主机名")
    description: Optional[str] = Field(None, max_length=1024, description="目标描述")
    type: Optional[TargetTypeEnum] = Field(None, description="目标类型")
    criticality: Optional[int] = Field(None, description="目标重要性 (30, 20, 10, 0)")
    settings: Optional[TargetSettings] = Field(None, description="目标的特定扫描设置") # 也添加到更新请求中

# --- Target Response Model ---
class TargetResponse(TargetBase):
    """
    GET /targets/{target_id} 和 GET /targets 列表中项目的响应模型。
    对应 API规范中的 #/definitions/TargetItemResponse。
    """
    target_id: str = Field(..., description="目标唯一标识符 (UUID)")
    settings: Optional[TargetSettings] = Field(None, description="目标的特定扫描设置") # 从创建/基础模型继承或显式添加
    
    fqdn_status: Optional[str] = None
    fqdn_tm_hash: Optional[str] = None
    deleted_at: Optional[datetime.datetime] = None
    fqdn: Optional[str] = None
    fqdn_hash: Optional[str] = None
    
    scan_authorization: Optional[ScanAuthorizationInfo] = None
    continuous_mode: Optional[bool] = None
    last_scan_date: Optional[datetime.datetime] = None
    last_scan_id: Optional[str] = Field(None, pattern=r"^[0-9a-fA-F-]{36}$") 
    last_scan_session_id: Optional[str] = Field(None, pattern=r"^[0-9a-fA-F-]{36}$") 
    last_scan_session_status: Optional[str] = None
    severity_counts: Optional[SeverityCounts] = None
    threat: Optional[int] = None
    links: Optional[List[Link]] = Field(default_factory=list)
    manual_intervention: Optional[bool] = None
    verification: Optional[str] = None

    @field_validator("deleted_at", "last_scan_date", mode="before")
    @classmethod
    def _validate_dates(cls, value: Any) -> Optional[datetime.datetime]:
        return parse_datetime_string(value)

# --- Models for Bulk Operations ---
class AddTargetsDescriptor(BaseModel):
    """
    POST /targets/add 的请求体。
    对应 API规范中的 #/definitions/AddTargetsDescriptor。
    """
    targets: List[TargetCreateRequest] 
    groups: Optional[List[str]] = Field(default_factory=list, description="组 UUID 列表")

class TargetIdList(BaseModel):
    """
    POST /targets/delete 的请求体。
    对应 API规范中的 #/definitions/TargetIdList。
    """
    target_id_list: List[str] = Field(..., description="目标 UUID 列表")

# --- Target Configuration Model ---
class TargetConfigurationData(BaseModel):
    """
    对应 API规范中的 #/definitions/TargetConfiguration。
    用于 GET 和 PATCH /targets/{target_id}/configuration。
    """
    issue_tracker_id: Optional[str] = Field(None, description="UUID 或空字符串")
    plugin_instance_id: Optional[str] = Field(None, description="UUID 或空字符串")
    limit_crawler_scope: Optional[bool] = None
    login: Optional[SiteLogin] = None
    sensor: Optional[bool] = None
    sensor_secret: Optional[str] = None
    ssh_credentials: Optional[SSHCredentials] = None
    proxy: Optional[ProxySettings] = None
    authentication: Optional[UserCredentials] = None 
    otp: Optional[OtpSettings] = None
    client_certificate_password: Optional[str] = Field(None, max_length=128)
    client_certificate_url: Optional[HttpUrl] = Field(None, description="URL, null, 或空字符串")
    scan_speed: Optional[ScanSpeedEnum] = Field(None, description="扫描速度") 
    case_sensitive: Optional[CaseSensitiveEnum] = Field(None, description="大小写敏感") 
    technologies: Optional[List[TechnologyEnum]] = Field(default_factory=list, description="技术名称列表") 
    custom_headers: Optional[List[str]] = Field(default_factory=list, description="自定义 HTTP 头部列表 ('Header: Value' 字符串)")
    custom_cookies: Optional[List[ApiCustomCookie]] = Field(default_factory=list)
    excluded_paths: Optional[List[str]] = Field(default_factory=list, description="从扫描范围排除的路径列表 (路径匹配字符串)")
    user_agent: Optional[str] = Field(None, max_length=256)
    debug: Optional[bool] = None
    excluded_hours_id: Optional[str] = Field(None, description="UUID, 空, 或 null")
    ad_blocker: Optional[bool] = Field(default=True)
    restrict_scans_to_import_files: Optional[bool] = None
    default_scanning_profile_id: Optional[str] = Field(None, description="UUID, null, 或空字符串")
    preseed_mode: Optional[str] = None
    skip_login_form: Optional[bool] = Field(default=False)

    @field_validator('client_certificate_url', mode='before')
    def empty_str_to_none(cls, v):
        if isinstance(v, str) and v == '':
            return None
        return v

    model_config = {"extra": "allow"}

class ContinuousScanMode(BaseModel):
    """
    对应 API规范中的 #/definitions/ContinuousScanMode。
    用于 GET 和 POST /targets/{target_id}/continuous_scan。
    """
    enabled: bool

class SensorType(str, Enum):
    PHP = "php"
    NET = "net"
    JAVA = "java"
    JAVA3 = "java3"
    NODE = "node"
    NET3 = "net3"

class SensorSecretContainer(BaseModel):
    """
    对应 API规范中的 #/definitions/SensorSecretContainer。
    用于 POST /targets/{target_id}/sensor/reset。
    """
    secret: Optional[str] = Field(None, description="AcuSensor 密钥 (MD5)。如果未设置，服务器将生成一个随机密钥。")

# --- Excluded Paths Models ---
class ExcludedPathList(BaseModel):
    """
    对应 API规范中的 #/definitions/ExcludedPathList。
    包含排除的路径字符串列表。
    """
    excluded_paths: Optional[List[str]] = Field(default_factory=list, description="从扫描范围排除的路径列表，每个路径最多512个字符，路径匹配格式")

class ExcludedPathListUpdate(BaseModel):
    """
    对应 API规范中的 #/definitions/ExcludedPathListUpdate。
    用作 POST /targets/{target_id}/configuration/exclusions 的请求体。
    """
    add: Optional[ExcludedPathList] = None
    delete: Optional[ExcludedPathList] = None

# --- Allowed Hosts Models ---
class AllowedHost(BaseModel):
    """
    对应 API规范中的 #/definitions/AllowedHost。
    """
    target_id: str = Field(..., description="允许主机的目标唯一标识符")
    address: HttpUrl = Field(..., description="允许主机的目标 URL 或主机名")
    description: Optional[str] = Field(default="", max_length=1024)

class AllowedHosts(BaseModel):
    """
    对应 API规范中的 #/definitions/AllowedHosts。
    GET /targets/{target_id}/allowed_hosts 的响应。
    """
    hosts: Optional[List[AllowedHost]] = Field(default_factory=list)

class TargetIdContainer(BaseModel):
    """
    对应 API规范中的 #/definitions/TargetIdContainer。
    用作 POST /targets/{target_id}/allowed_hosts 的请求体。
    """
    target_id: str = Field(..., description="要添加为允许主机的目标唯一标识符")

class TargetGroupIdList(BaseModel):
    """
    对应 API规范中的 #/definitions/TargetGroupIdList。
    GET /targets/{target_id}/target_groups 的响应。
    """
    group_id_list: Optional[List[str]] = Field(default_factory=list, description="目标所属的组 UUID 列表")

# --- Technologies Models ---
class TechnologyVersion(BaseModel):
    """对应 API规范中的 #/definitions/TechnologyVersion"""
    start: Optional[str] = Field(None, max_length=256)
    end: Optional[str] = Field(None, max_length=256)
    cvss_score: Optional[float] = None

class UpgradeVersion(BaseModel):
    """对应 API规范中的 #/definitions/UpgradeVersion"""
    version: Optional[str] = Field(None, max_length=256)
    cvss_score: Optional[float] = None

class Technology(BaseModel):
    """对应 API规范中的 #/definitions/Technology"""
    tech_id: Optional[str] = None
    name: Optional[str] = Field(None, max_length=256)
    description: Optional[str] = Field(None, max_length=65535)
    type: Optional[str] = Field(None, max_length=256) # Could be TechnologyEnum if values are known and fixed
    link: Optional[HttpUrl] = Field(None) 
    outdated: Optional[bool] = None
    loc_id: Optional[int] = None
    loc_url: Optional[HttpUrl] = Field(None) 
    detected_version: Optional[TechnologyVersion] = None
    branch_upgrade: Optional[UpgradeVersion] = None
    upgrade: Optional[UpgradeVersion] = None

class TechnologiesListResponse(BaseModel): 
    """对应 API规范中的 #/definitions/TechnologiesListResponse"""
    technologies: Optional[List[Technology]] = Field(default_factory=list)

# --- Target Deletion Notification Model ---
class TargetDeletionNotification(BaseModel):
    """
    对应 API规范中的 #/definitions/TargetDeletionNotification。
    当 DELETE /targets/{target_id} 返回 200 时，此模型作为响应体。
    """
    target_deletion_allowance: Optional[int] = None
    target_deletion_consumed: Optional[bool] = None

class TargetBrief(BaseModel):
    """简要目标信息，用于分页列表等场景。"""
    target_id: str = Field(..., description="目标唯一标识符 (UUID)")
    address: HttpUrl = Field(...)
    description: Optional[str] = None

# TargetCreate 作为 TargetCreateRequest 的语义别名，方便向后兼容
TargetCreate = TargetCreateRequest


class ContinuousScanItemResponse(BaseModel):
    """
    响应模型，用于描述目标的连续扫描配置或状态。
    具体字段可能需要根据实际 API 响应调整。
    """
    enabled: bool = Field(..., description="连续扫描是否启用")
    scan_profile_id: Optional[str] = Field(None, description="用于连续扫描的扫描配置文件ID (UUID)")
    next_run_time: Optional[datetime.datetime] = Field(None, description="下一次计划运行时间")
    # 可以根据需要添加更多字段，例如 last_run_time, status 等

    @field_validator("next_run_time", mode="before")
    @classmethod
    def _validate_next_run_time(cls, value: Any) -> Optional[datetime.datetime]:
        return parse_datetime_string(value)


class Target(TargetResponse):
    """向后兼容的完整 Target 模型。"""
    created_at: Optional[datetime.datetime] = Field(None, alias="created_at")

    @field_validator("created_at", mode="before")
    @classmethod
    def _validate_created_at(cls, value: Any) -> Optional[datetime.datetime]:
        return parse_datetime_string(value)

# 向后兼容别名
TargetUpdate = TargetUpdateRequest
TargetConfig = TargetConfigurationData


class GroupChangeTargetIdList(BaseModel):
    """
    用于在目标组中添加或移除目标的请求体模型。
    对应 PATCH /target_groups/{group_id}/targets 的请求体。
    """
    add: Optional[List[str]] = Field(default_factory=list, description="要添加到组的目标ID列表")
    remove: Optional[List[str]] = Field(default_factory=list, description="要从组中移除的目标ID列表")
