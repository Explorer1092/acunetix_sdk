from typing import Optional, List
from pydantic import BaseModel, Field, field_validator # Changed validator to field_validator
from enum import Enum
# Assuming ProxySettings is in common_settings
from .common_settings import ProxySettings 

class WAFPlatform(str, Enum):
    AWS = "AWS"
    # Add other platforms if supported

class WAFScope(str, Enum):
    CLOUDFRONT = "CLOUDFRONT"
    REGIONAL = "REGIONAL"

class WAFRegion(str, Enum): # AWS Regions
    US_EAST_1 = "us-east-1"
    US_EAST_2 = "us-east-2"
    US_WEST_1 = "us-west-1"
    US_WEST_2 = "us-west-2"
    CA_CENTRAL_1 = "ca-central-1"
    EU_NORTH_1 = "eu-north-1"
    EU_WEST_3 = "eu-west-3"
    EU_WEST_2 = "eu-west-2"
    EU_WEST_1 = "eu-west-1"
    EU_CENTRAL_1 = "eu-central-1"
    AP_SOUTH_1 = "ap-south-1"
    AP_SOUTHEAST_1 = "ap-southeast-1"
    AP_NORTHEAST_2 = "ap-northeast-2"
    AP_SOUTHEAST_2 = "ap-southeast-2"
    AP_NORTHEAST_1 = "ap-northeast-1"
    SA_EAST_1 = "sa-east-1"

class WAFConfigProxyTypeEnum(str, Enum):
    SYSTEM = "system"
    NO_PROXY = "no_proxy"
    CUSTOM = "custom"
    NONE_EMPTY = "" # Representing the empty string option from API spec for WAFConfig.proxy.proxy_type

class WAFConfigProxy(BaseModel): # This model represents the 'proxy' object within WAFConfig
    proxy_type: Optional[WAFConfigProxyTypeEnum] = Field(None, description="WAF代理类型")
    settings: Optional[ProxySettings] = Field(None, description="自定义代理设置 (仅当 proxy_type 为 custom 时需要)")

    @field_validator('proxy_type', mode='before')
    def empty_str_to_enum_value(cls, v):
        if v == "":
            return WAFConfigProxyTypeEnum.NONE_EMPTY
        if isinstance(v, WAFConfigProxyTypeEnum):
            return v
        if v is None: # If API sends null for proxy_type
            return None 
        try:
            return WAFConfigProxyTypeEnum(v)
        except ValueError:
             # Log or handle unknown proxy_type value from API if necessary
            return None # Or raise
        return v


class WAFConfig(BaseModel):
    """Corresponds to #/definitions/WAFConfig in API spec."""
    platform: WAFPlatform = Field(..., alias="Platform", description="WAF平台类型") 
    acl_name: str = Field(..., max_length=128, description="Web ACL 名称")
    access_key_id: str = Field(..., max_length=128, description="AWS Access Key Id")
    secret_key: str = Field(..., max_length=128, description="AWS Secret Access Key")
    acl_id: str = Field(..., max_length=128, description="Web ACL ID")
    scope: WAFScope = Field(..., description="Web ACL 的范围")
    region: Optional[WAFRegion] = Field(None, description="Web ACL 的区域 (如果范围是 REGIONAL 则必需)") 
    proxy: Optional[WAFConfigProxy] = Field(None, description="WAF连接的代理设置")

    model_config = {"populate_by_name": True}

class WAFConnectionStatus(BaseModel):
    """Corresponds to #/definitions/WAFConnectionStatus in API spec."""
    success: bool
    message: Optional[str] = None

class WAFEntry(WAFConfig):
    """Corresponds to #/definitions/WAFEntry in API spec."""
    waf_id: Optional[str] = Field(None, description="WAF唯一标识符 (UUID, GET时只读)")
    name: str = Field(..., max_length=128, description="WAF条目名称")

class WAFsList(BaseModel):
    """Corresponds to #/definitions/WAFsList in API spec."""
    wafs: Optional[List[WAFEntry]] = Field(default_factory=list)

# 为向后兼容 __all__ 中的导出名，创建别名
WAFProxyType = WAFConfigProxyTypeEnum
WAFProxy = WAFConfigProxy
