from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, HttpUrl, field_validator, conlist
from enum import Enum
# Assuming ProxySettings is in common_settings
from .common_settings import ProxySettings 

class IssueTrackerAuthKind(str, Enum):
    COOKIE = "cookie"
    HTTP_BASIC = "http_basic"
    NTLM = "ntlm"
    HTTP_BASIC_TOKEN = "http_basic_token"
    OAUTH = "oauth"
    IMPERSONATION_HTTP_BASIC_TOKEN = "impersonation_http_basic_token"

class IssueTrackerAuth(BaseModel):
    """Corresponds to #/definitions/IssueTrackerAuth"""
    kind: IssueTrackerAuthKind
    user: Optional[str] = Field(None, max_length=128)
    password: Optional[str] = Field(None, max_length=256)
    consumer_key: Optional[str] = Field(None, max_length=256)
    private_key: Optional[str] = Field(None, max_length=5120)

class IssueTrackerCollection(BaseModel):
    """Corresponds to #/definitions/IssueTrackerCollection"""
    collection_name: Optional[str] = Field(None, max_length=128)

class IssueTrackerCollections(BaseModel):
    """Corresponds to #/definitions/IssueTrackerCollections"""
    collections: Optional[List[IssueTrackerCollection]] = Field(default_factory=list)

class IssueTrackerCustomField(BaseModel):
    """Corresponds to #/definitions/IssueTrackerCustomField"""
    custom_field_name: Optional[str] = Field(None, max_length=256)
    custom_field_id: Optional[str] = Field(None, max_length=256)

class IssueTrackerCustomFields(BaseModel):
    """Corresponds to #/definitions/IssueTrackerCustomFields"""
    custom_fields: Optional[conlist(IssueTrackerCustomField, max_length=50)] = Field(default_factory=list)

class IssueTrackerProject(BaseModel):
    """Corresponds to #/definitions/IssueTrackerProject"""
    project_id: Optional[str] = Field(None, max_length=128)
    project_name: Optional[str] = Field(None, max_length=128)
    project_key: Optional[str] = Field(None, max_length=128)

class IssueTrackerProjects(BaseModel):
    """Corresponds to #/definitions/IssueTrackerProjects"""
    # Assuming API returns list of project objects for consistency, not just strings.
    projects: Optional[List[IssueTrackerProject]] = Field(default_factory=list) 

class IssueTrackerIssueType(BaseModel):
    """Corresponds to #/definitions/IssueTrackerIssueType"""
    issue_id: Optional[str] = Field(None, max_length=128)
    issue_name: Optional[str] = Field(None, max_length=128)

class IssueTrackerIssueTypes(BaseModel):
    """Corresponds to #/definitions/IssueTrackerIssueTypes"""
    # Assuming API returns list of issue type objects for consistency.
    issue_types: Optional[List[IssueTrackerIssueType]] = Field(default_factory=list)

class IssueTrackerPlatform(str, Enum):
    GITHUB = "github"
    JIRA = "jira"
    TFS = "tfs"
    GITLAB = "gitlab"
    BUGZILLA = "bugzilla"
    MANTIS = "mantis"
    AZURESERVICE = "azureservice"

class IssueTrackerProxyType(str, Enum):
    SYSTEM = "system"
    NO_PROXY = "no_proxy"
    CUSTOM = "custom"
    NONE_EMPTY = "" # Representing the empty string option from API

class IssueTrackerProxy(BaseModel):
    proxy_type: Optional[IssueTrackerProxyType] = None 
    settings: Optional[ProxySettings] = None

    @field_validator('proxy_type', mode='before')
    def empty_str_to_none_or_enum(cls, v):
        if v == "":
            return IssueTrackerProxyType.NONE_EMPTY # Or map to None if preferred
        if isinstance(v, IssueTrackerProxyType):
            return v
        if v is None:
            return None
        try:
            return IssueTrackerProxyType(v)
        except ValueError:
            # Handle cases where v is not a valid enum member and not empty string
            # This might indicate an unexpected value from the API
            # For now, let it pass to Pydantic's default validation or return None
            return None # Or raise ValueError(f"Invalid proxy_type: {v}")
        return v


class IssueTrackerCustomFieldEntry(BaseModel): 
    id: Optional[str] = None
    value: str
    name: Optional[str] = None


class IssueTrackerConfig(BaseModel):
    """Corresponds to #/definitions/IssueTrackerConfig"""
    platform: IssueTrackerPlatform
    url: HttpUrl = Field(..., max_length=128)
    auth: IssueTrackerAuth
    collection: Optional[IssueTrackerCollection] = None
    project: Optional[IssueTrackerProject] = None
    issue_type: Optional[IssueTrackerIssueType] = None
    proxy: Optional[IssueTrackerProxy] = None
    access_from_any_groups: Optional[bool] = None
    groups_access: Optional[List[str]] = Field(default_factory=list, description="List of group UUIDs") 
    tags: Optional[conlist(str, max_length=20)] = Field(default_factory=list)
    labels: Optional[conlist(str, max_length=20)] = Field(default_factory=list)
    custom_fields: Optional[conlist(IssueTrackerCustomFieldEntry, max_length=20)] = Field(default_factory=list)


class IssueTrackerConnectionStatus(BaseModel):
    """Corresponds to #/definitions/IssueTrackerConnectionStatus"""
    success: bool
    message: Optional[str] = None

class IssueTrackerEntry(IssueTrackerConfig):
    """Corresponds to #/definitions/IssueTrackerEntry"""
    issue_tracker_id: Optional[str] = Field(None, description="UUID, read-only for GET")
    name: str = Field(..., max_length=128)

class IssueTrackerList(BaseModel):
    """Corresponds to #/definitions/IssueTrackerList"""
    issue_trackers: Optional[List[IssueTrackerEntry]] = Field(default_factory=list)
