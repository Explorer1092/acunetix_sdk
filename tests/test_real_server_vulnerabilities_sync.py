# tests/test_real_server_vulnerabilities_sync.py
import pytest
from typing import List # For type hinting if needed

from acunetix_sdk import AcunetixSyncClient, AcunetixError
from acunetix_sdk.models.vulnerability import Vulnerability
# Fixture real_sync_client is implicitly available from conftest.py

class TestAcunetixRealServerVulnerabilitiesSync:
    def test_list_vulnerabilities(self, real_sync_client: AcunetixSyncClient):
        """测试列出漏洞。"""
        try:
            print("测试: 尝试列出漏洞")
            # Listing all vulnerabilities might be very large, so use a small limit.
            # It might also require specific filters (e.g., target_id, scan_id, status) to be useful.
            # For a general list test, a small limit and a common query is fine.
            vulnerabilities_paginated_list = real_sync_client.vulnerabilities.list(limit=5, query="status:open") # Changed q to query
            assert vulnerabilities_paginated_list is not None
            assert hasattr(vulnerabilities_paginated_list, 'items') # PaginatedList has 'items'
            assert isinstance(vulnerabilities_paginated_list.items, list)
            print(f"测试: 成功获取到 {len(vulnerabilities_paginated_list.items)} 条漏洞记录 (最多5条, 状态为open)。")
            if vulnerabilities_paginated_list.items:
                for vuln in vulnerabilities_paginated_list.items:
                    assert isinstance(vuln, Vulnerability)
                    target_info = f"描述: {vuln.target_description or 'N/A'}, ID: {vuln.target_id or 'N/A'}"
                    print(f"  - 漏洞 ID: {vuln.vuln_id}, 目标: ({target_info}), 严重性: {vuln.severity}")
            else:
                print("服务器上没有符合条件的漏洞记录（状态为open），或者当前用户无权查看。")
        except AcunetixError as e:
            pytest.fail(f"列出漏洞时发生 AcunetixError: {e}")
        except Exception as e:
            pytest.fail(f"列出漏洞时发生未知错误: {e}")
