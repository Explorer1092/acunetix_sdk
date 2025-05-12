from typing import Optional, List, Any
from pydantic import BaseModel, Field, constr, conlist
from enum import Enum

# --- Existing Models (Potentially for API Responses) ---
class ScanningProfile(BaseModel):
    """
    Corresponds to #/definitions/ScanningProfile in API spec.
    Used for GET responses.
    """
    name: constr(min_length=1, max_length=256) = Field(..., description="Scan Type (Scanning Profile) name")
    checks: Optional[conlist(item_type=constr(min_length=1, max_length=128), max_length=800)] = Field(
        None, # Made optional as create request doesn't have it directly
        description="Vulnerability test names. Array must contain names of checks which are NOT to be performed."
    )
    profile_id: Optional[str] = Field(None, description="Scan Type (Scanning Profile) unique identifier (UUID, read-only for GET)")
    sort_order: Optional[int] = Field(default=1000, ge=1, description="Sort order value")
    custom: Optional[bool] = Field(None, description="Describes if the Scan Type (Scanning Profile) is user-editable (read-only for GET)")
    # Fields from create request that might appear in response
    description: Optional[str] = Field(None, max_length=512, description="扫描配置描述")


# --- Backwards-compatibility aliases ---
class ScanProfile(ScanningProfile):
    """向后兼容旧名称。"""
    pass

class ScanProfileType(str, Enum):
    """占位枚举，实际可根据 API 常见的扫描类型进行补充。"""
    FULL = "full"
    HIGH_RISK = "high_risk"
    QUICK = "quick"
    CUSTOM = "custom" # Assuming custom might be a type

# --- Models for ScanProfileCreateRequest based on conftest.py ---

class ScanProfileGeneralSettings(BaseModel):
    scan_speed: Optional[str] = "fast" # Default from conftest

class ScanProfileHttpSettings(BaseModel):
    user_agent: Optional[str] = "Acunetix SDK Test Agent"
    request_concurrency: Optional[int] = 10
    # Add other fields if necessary

class ScanProfileScanningSettings(BaseModel):
    case_sensitive: Optional[bool] = True
    limit_crawler_scope: Optional[bool] = True
    excluded_paths: Optional[List[str]] = []
    # Add other fields if necessary

class ScanProfileScriptingSettings(BaseModel):
    custom_scripts: Optional[List[Any]] = [] # Type of items in custom_scripts is unknown, using Any
    # Add other fields if necessary

class ScanProfileTechnologies(BaseModel):
    server: Optional[List[str]] = ["Apache"]
    os: Optional[List[str]] = ["Linux"]
    backend: Optional[List[str]] = ["PHP"]
    # Add other fields if necessary

class ScanProfileLogin(BaseModel):
    kind: Optional[str] = "none"
    # Add other fields for different kinds of login

class ScanProfileSensor(BaseModel):
    sensor_token: Optional[str] = None
    sensor_secret: Optional[str] = None
    acu_sensor_bridge: Optional[str] = None
    # Add other fields if necessary

class ScanProfileCustomHeader(BaseModel):
    name: str
    value: str
    # Add other fields if necessary

class ScanProfileCustomCookie(BaseModel):
    url: Optional[str] = None # Assuming URL might be needed
    cookie: Optional[str] = None
    # Add other fields if necessary

class ScanProfileWaf(BaseModel):
    name: Optional[str] = "generic"
    bypass_rules: Optional[List[Any]] = [] # Type of items in bypass_rules is unknown
    # Add other fields if necessary

class ScanProfileReport(BaseModel):
    false_positives: Optional[bool] = False
    format: Optional[str] = "html"
    generate: Optional[bool] = False
    type: Optional[str] = "scan" # Could be an Enum
    email_address: Optional[str] = None
    # Add other fields if necessary

class ScanProfileExcludedElement(BaseModel):
    path_regex: Optional[str] = None # Assuming structure
    element_xpath: Optional[str] = None
    # Add other fields if necessary

class ScanProfilePreseedFile(BaseModel):
    name: Optional[str] = None # Assuming structure
    content_base64: Optional[str] = None
    # Add other fields if necessary

class ScanProfileProxy(BaseModel):
    enabled: Optional[bool] = False
    address: Optional[str] = None
    port: Optional[int] = None
    protocol: Optional[str] = None # e.g., http, socks5
    username: Optional[str] = None
    password: Optional[str] = None
    use_auth: Optional[bool] = False
    # Add other fields if necessary

class ScanProfileCvss(BaseModel):
    enabled: Optional[bool] = False
    # Add other fields if necessary

class ScanProfileAdvanced(BaseModel):
    enable_port_scanning: Optional[bool] = False
    network_scan_type: Optional[str] = None # Could be an Enum
    enable_audio_import: Optional[bool] = False
    enable_crl_check: Optional[bool] = False
    parallel_scans: Optional[int] = None
    client_certificate_password: Optional[str] = None
    custom_settings: Optional[List[Any]] = [] # Type of items in custom_settings is unknown
    # Add other fields if necessary

class ScanProfileCreateRequest(BaseModel):
    name: str = Field(..., max_length=256, description="扫描配置名称")
    description: Optional[str] = Field(None, max_length=512, description="扫描配置描述")
    general: Optional[ScanProfileGeneralSettings] = Field(default_factory=ScanProfileGeneralSettings)
    http: Optional[ScanProfileHttpSettings] = Field(default_factory=ScanProfileHttpSettings)
    scanning: Optional[ScanProfileScanningSettings] = Field(default_factory=ScanProfileScanningSettings)
    scripting: Optional[ScanProfileScriptingSettings] = Field(default_factory=ScanProfileScriptingSettings)
    technologies: Optional[ScanProfileTechnologies] = Field(default_factory=ScanProfileTechnologies)
    login: Optional[ScanProfileLogin] = Field(default_factory=ScanProfileLogin)
    sensor: Optional[ScanProfileSensor] = Field(default_factory=ScanProfileSensor)
    custom_headers: Optional[List[ScanProfileCustomHeader]] = Field(default_factory=list)
    custom_cookies: Optional[List[ScanProfileCustomCookie]] = Field(default_factory=list)
    waf: Optional[ScanProfileWaf] = Field(default_factory=ScanProfileWaf)
    report: Optional[ScanProfileReport] = Field(default_factory=ScanProfileReport)
    excluded_elements: Optional[List[ScanProfileExcludedElement]] = Field(default_factory=list)
    preseed_files: Optional[List[ScanProfilePreseedFile]] = Field(default_factory=list)
    proxy: Optional[ScanProfileProxy] = Field(default_factory=ScanProfileProxy)
    cvss: Optional[ScanProfileCvss] = Field(default_factory=ScanProfileCvss)
    advanced: Optional[ScanProfileAdvanced] = Field(default_factory=ScanProfileAdvanced)

    # The 'checks' field from ScanningProfile is not part of this create request
    # as per conftest.py usage. It might be set by server or through other means.
    # 'sort_order' and 'custom' are also typically server-set or read-only.
    checks: Optional[conlist(item_type=constr(min_length=1, max_length=128), max_length=800)] = Field(
        None,
        description="Vulnerability test names. Array must contain names of checks which are NOT to be performed."
    ) # Added checks field

class ScanProfileUpdateRequest(BaseModel):
    """
    更新扫描配置的请求模型。所有字段都是可选的。
    """
    name: Optional[str] = Field(None, max_length=256, description="扫描配置名称")
    description: Optional[str] = Field(None, max_length=512, description="扫描配置描述")
    general: Optional[ScanProfileGeneralSettings] = Field(None)
    http: Optional[ScanProfileHttpSettings] = Field(None)
    scanning: Optional[ScanProfileScanningSettings] = Field(None)
    scripting: Optional[ScanProfileScriptingSettings] = Field(None)
    technologies: Optional[ScanProfileTechnologies] = Field(None)
    login: Optional[ScanProfileLogin] = Field(None)
    sensor: Optional[ScanProfileSensor] = Field(None)
    custom_headers: Optional[List[ScanProfileCustomHeader]] = Field(None)
    custom_cookies: Optional[List[ScanProfileCustomCookie]] = Field(None)
    waf: Optional[ScanProfileWaf] = Field(None)
    report: Optional[ScanProfileReport] = Field(None)
    excluded_elements: Optional[List[ScanProfileExcludedElement]] = Field(None)
    preseed_files: Optional[List[ScanProfilePreseedFile]] = Field(None)
    proxy: Optional[ScanProfileProxy] = Field(None)
    cvss: Optional[ScanProfileCvss] = Field(None)
    advanced: Optional[ScanProfileAdvanced] = Field(None)
    # 'checks' 字段通常在更新时也可能被修改，如果 API 支持的话。
    # 根据 API 规范，ScanningProfile (用于 GET/POST/PATCH) 包含 'checks'。
    # 如果更新时允许修改 checks，则应在此处添加。
    checks: Optional[conlist(item_type=constr(min_length=1, max_length=128), max_length=800)] = Field(
        None,
        description="Vulnerability test names. Array must contain names of checks which are NOT to be performed."
    ) # Added checks field to update request as well
