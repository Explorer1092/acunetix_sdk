from typing import TYPE_CHECKING, List # Removed Optional, Dict, Any

from ..models.report_template import ReportTemplate # Removed ReportTemplateCreateRequest, ReportTemplateUpdateRequest
from .base_resource import BaseResource
from ..errors import AcunetixError

if TYPE_CHECKING:
    from ..client_sync import AcunetixSyncClient
    from ..client_async import AcunetixAsyncClient

class ReportTemplatesSyncResource(BaseResource["AcunetixSyncClient"]):
    """Handles synchronous operations related to Acunetix report templates."""

    def list(self) -> List[ReportTemplate]:
        """
        Lists report templates.
        Corresponds to GET /report_templates in API.
        API operationId: get_report_templates.
        This endpoint does not support pagination or filtering according to the API spec.
        """
        response = self._client._request("GET", "report_templates")
        
        # API spec for GET /report_templates returns ReportTemplateList, 
        # which has a "templates" property (array of ReportTemplate).
        if not isinstance(response, dict) or "templates" not in response:
            # Fallback if API returns a direct list (though spec says ReportTemplateList object)
            if isinstance(response, list):
                return [ReportTemplate.model_validate(item) for item in response]
            raise AcunetixError("Unexpected response structure for list report templates. Expected a dictionary with a 'templates' key or a direct list.")
        
        items = response.get("templates", [])
        return [ReportTemplate.model_validate(item) for item in items]

    def get(self, template_id: str) -> ReportTemplate:
        """获取单个报告模板的详细信息。"""
        response = self._client._request("GET", f"report_templates/{template_id}")
        if not isinstance(response, dict):
            raise AcunetixError("Unexpected response structure for get report template.")
        return ReportTemplate.model_validate(response)


class ReportTemplatesAsyncResource(BaseResource["AcunetixAsyncClient"]):
    """Handles asynchronous operations related to Acunetix report templates."""

    async def list(self) -> List[ReportTemplate]:
        """
        Lists report templates asynchronously.
        Corresponds to GET /report_templates in API.
        This endpoint does not support pagination or filtering according to the API spec.
        """
        response = await self._client._arequest("GET", "report_templates")

        if not isinstance(response, dict) or "templates" not in response:
            if isinstance(response, list):
                return [ReportTemplate.model_validate(item) for item in response]
            raise AcunetixError("Unexpected response structure for list report templates. Expected a dictionary with a 'templates' key or a direct list.")
            
        items = response.get("templates", [])
        return [ReportTemplate.model_validate(item) for item in items]

    async def get(self, template_id: str) -> ReportTemplate:
        """异步获取单个报告模板的详细信息。"""
        response = await self._client._arequest("GET", f"report_templates/{template_id}")
        if not isinstance(response, dict):
            raise AcunetixError("Unexpected response structure for get report template.")
        return ReportTemplate.model_validate(response)
