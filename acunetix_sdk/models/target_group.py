from typing import Optional, List
from pydantic import BaseModel, Field
from .common_settings import SeverityCounts  # 假设 SeverityCounts 在 common_settings.py 中


class TargetGroup(BaseModel):
    """
    Acunetix Target Group 模型
    """
    group_id: Optional[str] = Field(None, description="目标组唯一标识符")
    name: str = Field(..., max_length=256, description="目标组名称")
    target_count: Optional[int] = Field(None, description="目标组目标数量")
    description: Optional[str] = Field(None, max_length=512, description="目标组描述")
    vuln_count: Optional[SeverityCounts] = Field(None, description="漏洞数量统计")


class TargetGroupCreateRequest(BaseModel):
    """
    创建目标组的请求模型
    """
    name: str = Field(..., max_length=256, description="目标组名称")
    description: Optional[str] = Field(None, max_length=512, description="目标组描述")


class TargetGroupUpdateRequest(BaseModel):
    """
    更新目标组的请求模型。所有字段都是可选的。
    """
    name: Optional[str] = Field(None, max_length=256, description="目标组名称")
    description: Optional[str] = Field(None, max_length=512, description="目标组描述")


class TargetGroupBrief(BaseModel):
    """
    目标组的简要信息模型。
    """
    group_id: str = Field(..., description="目标组唯一标识符")
    name: str = Field(..., max_length=256, description="目标组名称")
    # target_count 可以在 brief 中可选地包含
    target_count: Optional[int] = Field(None, description="目标组目标数量")


class TargetGroupIdList(BaseModel):
    """
    目标组 ID 列表模型
    """
    group_id_list: Optional[List[str]] = Field(None, description="组唯一标识符列表")


class TargetGroupListResponse(BaseModel):
    """
    目标组列表响应模型
    """
    groups: Optional[List[TargetGroup]] = None
    # pagination 字段在 API 文档中存在，但为了简化，这里暂时省略，
    # 如果需要，可以从 acunetix_sdk/models/pagination.py 导入 PaginationExt
    # pagination: Optional[PaginationExt] = None
