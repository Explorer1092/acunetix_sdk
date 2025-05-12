from typing import Optional, Any
from pydantic import BaseModel, Field, field_validator
import datetime
from .utils import parse_datetime_string # Assuming you might need this for 'created'

class AgentRegistrationToken(BaseModel):
    """
    Corresponds to #/definitions/AgentRegistrationToken in API spec.
    """
    token: Optional[str] = Field(None, description="Registration token (UUID)")
    description: Optional[str] = Field(None, description="Registration token description")
    created: Optional[datetime.datetime] = Field(None, description="Registration token creation timestamp")

    @field_validator("created", mode="before")
    @classmethod
    def _validate_created_at(cls, value: Any) -> Optional[datetime.datetime]:
        return parse_datetime_string(value)

class NewAgentRegistrationToken(BaseModel):
    """
    Corresponds to #/definitions/NewAgentRegistrationToken in API spec.
    Used as request body for POST /config/agents/registration_token.
    """
    description: Optional[str] = Field(None, max_length=255, description="Registration token description")

class AgentsConfig(BaseModel):
    """
    代理配置模型。
    对应 GET /config/agents 的响应。
    """
    auto_update: Optional[bool] = Field(None, description="代理是否自动更新")
    type: Optional[str] = Field(None, description="代理类型或配置模式") # 具体类型未知，用 str
    # 根据 API 实际响应，可能还有其他字段
