from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum

class ReportTemplateAcceptedSourceEnum(str, Enum):
    # Keeping existing valid values if they are still possible
    IGNORE_ENTRY = "ignore_entry"
    UN_IGNORE_ENTRY = "un_ignore_entry"
    BLACKLIST_IP = "blacklist_ip"
    UN_BLACKLIST_IP = "un_blacklist_ip"
    BLACKLIST_SECOND_LEVEL_DOMAIN = "blacklist_second_level_domain"
    UN_BLACKLIST_SECOND_LEVEL_DOMAIN = "un_blacklist_second_level_domain"
    BLACKLIST_TOP_LEVEL_DOMAIN = "blacklist_top_level_domain"
    UN_BLACKLIST_TOP_LEVEL_DOMAIN = "un_blacklist_top_level_domain"
    BLACKLIST_ORGANIZATION = "blacklist_organization"
    UN_BLACKLIST_ORGANIZATION = "un_blacklist_organization"
    
    # Adding values observed from the test failure
    ALL_VULNERABILITIES = "all_vulnerabilities"
    TARGETS = "targets"
    GROUPS = "groups"
    SCANS = "scans"
    SCAN_RESULT = "scan_result" # "scan_result" from error, API might use "scan_results"
    VULNERABILITIES = "vulnerabilities"
    SCAN_VULNERABILITIES = "scan_vulnerabilities"
    SCAN_PAIR = "scan_pair"  # 从 ValidationError 添加
    SCAN_RESULT_PAIR = "scan_result_pair"  # 从 ValidationError 添加
    # It's possible the API uses slightly different casing or pluralization,
    # this is based on the exact strings from the error.


class ReportTemplate(BaseModel):
    """
    Corresponds to #/definitions/ReportTemplate in API spec.
    """
    template_id: str = Field(..., description="报告模板唯一标识符")
    name: Optional[str] = Field(None, description="报告模板名称") # API spec does not mark name as required for ReportTemplate
    group: Optional[str] = Field(None, description="报告模板所属的组") # API spec does not mark group as required for ReportTemplate
    accepted_sources: List[ReportTemplateAcceptedSourceEnum] = Field(..., description="此模板接受的源类型列表")

# ReportTemplateBrief, ReportTemplateCreate, ReportTemplateUpdate are removed
# as the API spec only defines GET /report_templates and a single ReportTemplate model.
# The API spec for ReportTemplate model itself does not mark 'name' or 'group' as required, only 'template_id'.
# 'accepted_sources' is also not marked as required in the ReportTemplate definition, but it's present.
# For consistency with the API spec's definition of ReportTemplate, making accepted_sources required.
# If the API returns templates without 'name' or 'group', Optional is correct.
# If 'accepted_sources' can be missing, it should also be Optional.
# Based on the provided API spec for ReportTemplate model:
# template_id: required
# name: not marked required
# group: not marked required
# accepted_sources: not marked required (but present as an array)
# Let's assume accepted_sources is required as it's a key part of the definition.
# Name and group will remain Optional.

class ReportTemplateType(str, Enum):
    """报告模板类型/组。"""
    STANDARD = "standard"
    COMPLIANCE = "compliance"
    EXECUTIVE = "executive"
    SCAN = "scan" # 从 conftest.py 添加
