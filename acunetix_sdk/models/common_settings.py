# acunetix_sdk/models/common_settings.py
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, HttpUrl, EmailStr # Added EmailStr
import datetime
from enum import Enum

# --- User Credentials ---
class UserCredentials(BaseModel):
    """
    User credentials for various authentication purposes.
    Corresponds to #/definitions/UserCredentials in API spec.
    """
    enabled: Optional[bool] = Field(default=False)
    username: Optional[str] = Field(None, max_length=128)
    password: Optional[str] = Field(None, max_length=128) # API spec says hash, but client sends plain
    url: Optional[HttpUrl] = Field(None, max_length=256)


# --- Site Login ---
class SiteLoginKind(str, Enum):
    NONE = "none"
    AUTOMATIC = "automatic"
    SEQUENCE = "sequence"
    OAUTH = "oauth"

class SiteLogin(BaseModel):
    """
    Site login configuration.
    Corresponds to #/definitions/SiteLogin in API spec.
    """
    kind: SiteLoginKind = Field(...)
    credentials: Optional[UserCredentials] = None
    # sequence field removed as API spec for SiteLogin does not include a structured sequence. Login sequence files (.lsr) are uploaded.


# --- SSH Credentials ---
class SSHCredentialsKind(str, Enum):
    NONE = "none"
    KEY = "key"
    PASSWORD = "password"

class SSHCredentials(BaseModel):
    """
    SSH credentials.
    Corresponds to #/definitions/SSHCredentials in API spec.
    """
    kind: Optional[SSHCredentialsKind] = Field(default=SSHCredentialsKind.NONE)
    username: Optional[str] = Field(None, max_length=128)
    port: Optional[int] = Field(default=22)
    password: Optional[str] = Field(None, max_length=128)
    ssh_key: Optional[str] = Field(None, description="SSH private key content")
    key_password: Optional[str] = Field(None, max_length=128, description="Passphrase for the SSH key")


# --- Proxy Settings ---
class ProxyProtocol(str, Enum):
    HTTP = "http"
    # Add other protocols if supported, e.g., SOCKS5

class ProxySettings(BaseModel):
    """
    Proxy settings.
    Corresponds to #/definitions/ProxySettings in API spec.
    """
    enabled: Optional[bool] = Field(default=False)
    protocol: Optional[ProxyProtocol] = Field(default=ProxyProtocol.HTTP)
    address: Optional[str] = Field(None, max_length=256) # API spec says format: host
    port: Optional[int] = Field(None)
    username: Optional[str] = Field(None, max_length=64)
    password: Optional[str] = Field(None, max_length=64)


# --- OTP Settings ---
class OtpType(str, Enum):
    TOTP = "totp"
    HOTP = "hotp"

class OtpAlgorithm(str, Enum):
    SHA1 = "sha1"
    SHA256 = "sha256"
    SHA512 = "sha512"

class OtpSettings(BaseModel):
    """
    OTP settings.
    Corresponds to #/definitions/OtpSettings in API spec.
    """
    otp_type: Optional[OtpType] = Field(default=OtpType.TOTP)
    secret_key: str = Field(...) # Marked as required in API spec example
    digit: Optional[int] = Field(default=6)
    period: Optional[int] = Field(default=30) # Only for TOTP
    algorithm: Optional[OtpAlgorithm] = Field(default=OtpAlgorithm.SHA1)


# --- Custom Cookies (API specific format) ---
class ApiCustomCookie(BaseModel):
    """
    Custom cookie in the format expected by Acunetix API TargetConfiguration.
    Corresponds to items in custom_cookies array in #/definitions/TargetConfiguration.
    """
    cookie: str = Field(..., description="The full cookie string (e.g., 'name=value; Domain=example.com')")
    url: HttpUrl = Field(..., description="URL to which the cookie applies")

# LoginSequenceStep, CrawlSettings, CustomHeader, and the generic Cookie model
# are removed as they do not directly correspond to fields in the current API specification
# for TargetConfiguration or other clearly defined request/response bodies.
# ApiCustomCookie is retained as it matches the custom_cookies structure in TargetConfiguration.

# --- File Upload Models (Common for Login Sequence, Client Cert, Imports) ---
class FileUploadDescriptor(BaseModel):
    """
    Descriptor for initiating a file upload.
    Corresponds to #/definitions/FileUploadDescriptor in API spec.
    """
    name: str = Field(..., max_length=128, description="File name") # API spec has format: filename
    size: int = Field(..., description="File size in bytes") # API spec has format: int32

class UploadLocationResponse(BaseModel):
    """
    Response containing the temporary URL for file upload.
    Corresponds to #/definitions/UploadLocationResponse in API spec.
    """
    upload_url: HttpUrl

class UploadedFile(BaseModel):
    """
    Information about an uploaded file.
    Corresponds to #/definitions/UploadedFile in API spec.
    """
    upload_id: str = Field(..., description="Uploaded file unique identifier (UUID)")
    name: str = Field(..., description="Uploaded file name")
    size: int = Field(..., description="Uploaded file size")
    status: bool = Field(..., description="Uploaded file status (e.g., true if fully uploaded/processed)")
    current_size: Optional[int] = Field(None, description="Uploaded file current size (for chunked uploads)")
    retrieve_url: Optional[HttpUrl] = Field(None, description="URL to retrieve/download the file if applicable")

class UploadedFilesResponse(BaseModel):
    """
    Response containing a list of uploaded files (e.g., for Imports).
    Corresponds to #/definitions/UploadedFilesResponse in API spec.
    """
    files: Optional[List[UploadedFile]] = Field(default_factory=list)

# --- Placeholder classes for backward compatibility ---
class LoginSettings(BaseModel):
    """占位符，仅用于测试向后兼容。实际登录配置请使用 SiteLogin。"""
    username: Optional[str] = None
    password: Optional[str] = None

class CrawlSettings(BaseModel):
    """占位符，用于测试向后兼容原 SDK 的爬虫相关设置。"""
    max_depth: Optional[int] = None
    scope: Optional[str] = None


# --- Severity Counts ---
class SeverityCounts(BaseModel):
    """
    Represents the count of vulnerabilities categorized by severity.
    Corresponds to #/definitions/SeverityCounts or similar structures in API responses.
    """
    high: Optional[int] = Field(default=0, description="高危漏洞数量")
    medium: Optional[int] = Field(default=0, description="中危漏洞数量")
    low: Optional[int] = Field(default=0, description="低危漏洞数量")
    info: Optional[int] = Field(default=0, description="信息类漏洞数量")
