from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, field_validator
from enum import Enum
import datetime
from .utils import parse_datetime_string

class NotificationType(str, Enum):
    SCAN_COMPLETED = "scan_completed"
    SCAN_FAILED = "scan_failed"
    SCAN_ABORTED = "scan_aborted"
    REPORT_GENERATED = "report_generated"
    # Removed VULNERABILITY_FOUND and SCHEDULED_SCAN_LAUNCHED as they are not in the API spec for Notification events.
    # 若有其他枚举值，可根据实际 API 补充

NotificationEvent = NotificationType

# Removed NotificationScopeType Enum, scope.type will be str to capture raw API value
# class NotificationScopeType(str, Enum):
#     """根据 API 推断，通知范围的类型"""
#     ALL = "all" # 假设 "all_targets" 或类似
#     TARGET = "target"
#     GROUP = "group"
#     # 根据 API 文档确认实际值

class NotificationScope(BaseModel):
    """
    通知范围模型
    Corresponds to #/definitions/NotificationScope in API spec (if defined, otherwise inferred)
    """
    # API spec for Notification (config) has 'scope' as an object.
    # Assuming it has 'type', and optionally 'target_id' or 'group_id'
    type: str = Field(..., description="范围类型 (API 原始值)") # Changed from NotificationScopeType to str
    target_id: Optional[str] = Field(None, description="特定目标 ID (如果 type 为 'target')")
    group_id: Optional[str] = Field(None, description="特定目标组 ID (如果 type 为 'group')")


class NotificationCreateRequest(BaseModel):
    """
    创建通知的请求模型
    """
    name: str = Field(..., max_length=255, description="通知名称")
    event: NotificationEvent = Field(..., description="触发通知的事件类型") # Keep Enum for creation for validation
    scope: NotificationScope # Scope.type will be str, ensure CLI passes valid string if not using Enum
    disabled: Optional[bool] = Field(False, description="是否禁用通知")
    email_address: Optional[List[str]] = Field(None, description="接收通知的电子邮件地址列表")
    webhook_url: Optional[str] = Field(None, description="接收通知的 Webhook URL")
    # 根据 API 文档，可能还有其他与通知配置相关的字段


class NotificationUpdateRequest(BaseModel):
    """
    更新通知的请求模型。所有字段都是可选的。
    """
    name: Optional[str] = Field(None, max_length=255, description="通知名称")
    event: Optional[NotificationEvent] = Field(None, description="触发通知的事件类型")
    scope: Optional[NotificationScope] = Field(None, description="通知的范围")
    disabled: Optional[bool] = Field(None, description="是否禁用通知")
    email_address: Optional[List[str]] = Field(None, description="接收通知的电子邮件地址列表")
    webhook_url: Optional[str] = Field(None, description="接收通知的 Webhook URL")
    # 根据 API 文档，可能还有其他与通知配置相关的字段


class NotificationData(BaseModel):
    """通用通知数据结构，具体字段可能依据通知类型而变化。"""
    scan_id: Optional[str] = None
    target_id: Optional[str] = None
    report_id: Optional[str] = None
    message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


# This model represents a Notification Configuration as per API spec for GET /notifications
class Notification(BaseModel): # Renamed from previous Notification which was for system events
    """
    通知配置模型
    Corresponds to #/definitions/Notification in API spec.
    """
    notification_id: str = Field(..., description="通知配置的唯一标识符 (UUID)")
    name: Optional[str] = Field(None, description="通知配置名称")
    event: Optional[str] = Field(None, description="触发通知的事件类型 (API 原始值)") # Changed from NotificationEvent to str
    scope: Optional[NotificationScope] = Field(None, description="通知的范围")
    disabled: Optional[bool] = Field(False, description="通知是否被禁用")
    email_address: Optional[List[str]] = Field(default_factory=list, description="接收通知的电子邮件地址列表")
    webhook_url: Optional[str] = Field(None, description="接收通知的 Webhook URL")
    # Add other fields if present in API spec for a notification configuration item

    model_config = {"populate_by_name": True} # If any aliases are needed from API field names


# This model represents a System Event Notification (e.g., from a feed or list of past events)
# This was the original 'Notification' model. Renaming to avoid conflict.
class SystemEventNotification(BaseModel):
    notification_id: str # This might be the event's unique ID, not config ID
    type: Optional[NotificationType] = Field(None, alias="event_type", description="事件类型") # Example alias
    resource_id: Optional[str] = Field(None, description="相关资源 ID，例如 scan_id、report_id")
    creation_date: Optional[datetime.datetime] = Field(None, alias="date")
    is_read: Optional[bool] = Field(None, alias="read")
    data: Optional[NotificationData] = None # Specific payload for the event

    @field_validator("creation_date", mode="before")
    @classmethod
    def _validate_creation_date(cls, value: Any) -> Optional[datetime.datetime]:
        return parse_datetime_string(value)
    
    model_config = {"populate_by_name": True}


class NotificationIdList(BaseModel):
    """用于批量标记通知已读或删除。"""
    notification_id_list: Optional[List[str]] = Field(None, description="通知 UUID 列表，空或缺省表示全部。")


# For Paginated List of Notification Configurations
from .pagination import PaginatedList, PaginationInfo

class NotificationList(PaginatedList[Notification]):
    """
    Represents a paginated list of Notification Configurations.
    The API returns a key "notifications" for the list of items.
    """
    items: List[Notification] = Field(..., alias="notifications", description="当前页的通知配置列表")
    pagination: PaginationInfo

    model_config = {"populate_by_name": True}
