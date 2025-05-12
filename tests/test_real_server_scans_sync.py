# tests/test_real_server_scans_sync.py
import pytest
from typing import List, Optional # For type hinting if needed
import time # For delays in polling status

from acunetix_sdk import AcunetixSyncClient, AcunetixError
from acunetix_sdk.models.target import TargetResponse # For managed_target type hint
from acunetix_sdk.models.scan import (
    ScanCreateRequest as ScanScheduleRequest, 
    Schedule as ScanSchedule, 
    ScanResponse, 
    ScanBrief, 
    ScanInfo, 
    SeverityCounts as VulnerabilitySummary,
    ScanResultItemResponse # Added import
)
from acunetix_sdk.models.scan_profile import ScanningProfile, ScanProfile # For managed_scan_profile type hint
from acunetix_sdk.models.vulnerability import Vulnerability # For listing scan vulnerabilities
from pydantic import ValidationError # Added for specific exception handling
# Fixtures real_sync_client, managed_target, managed_scan_profile are implicitly available from conftest.py

class TestAcunetixRealServerScansSync:
    def test_start_scan_on_managed_target(self, real_sync_client: AcunetixSyncClient, managed_target: TargetResponse, managed_scan_profile: ScanningProfile):
        """测试在托管目标上启动扫描。"""
        target_id = managed_target.target_id
        
        try:
            print(f"测试: 尝试为目标 {target_id} 启动扫描")
            # Use the managed_scan_profile fixture
            profile_id_to_use = managed_scan_profile.profile_id
            assert profile_id_to_use is not None, "托管的扫描配置文件没有 profile_id"
            print(f"测试: 将使用扫描配置文件 ID: {profile_id_to_use} ({managed_scan_profile.name}) 来自 fixture")

            schedule_config = ScanSchedule(disable=False)
            
            scan_request_payload = ScanScheduleRequest(
                target_id=target_id,
                profile_id=profile_id_to_use, # Use profile_id from managed_scan_profile
                schedule=schedule_config
            )
            
            print(f"测试: 发起扫描请求: {scan_request_payload.model_dump_json(exclude_none=True)}")
            created_scan_response = real_sync_client.scans.create(scan_request_payload)
            
            assert created_scan_response is not None
            assert isinstance(created_scan_response, ScanResponse)
            assert created_scan_response.scan_id is not None
            assert created_scan_response.target_id == target_id
            assert created_scan_response.profile_id == profile_id_to_use
            print(f"测试: 成功为目标 {target_id} 创建扫描，扫描 ID: {created_scan_response.scan_id}")
            print(f"  扫描状态: {created_scan_response.current_session.status if created_scan_response.current_session else 'N/A'}")

        except AcunetixError as e:
            pytest.fail(f"为目标 {target_id} 启动扫描时发生 AcunetixError: {e}")
        except AssertionError as e:
            pytest.fail(f"为目标 {target_id} 启动扫描断言失败: {e}")
        except Exception as e:
            pytest.fail(f"为目标 {target_id} 启动扫描时发生未知错误: {e}")

    def test_list_scans(self, real_sync_client: AcunetixSyncClient):
        """测试列出扫描记录。"""
        try:
            print("测试: 尝试列出扫描记录")
            scans_paginated_list = real_sync_client.scans.list(limit=5)
            assert scans_paginated_list is not None
            assert isinstance(scans_paginated_list.items, list)
            print(f"测试: 成功获取到 {len(scans_paginated_list.items)} 条扫描记录 (最多5条)。")
            if scans_paginated_list.items:
                for scan_item in scans_paginated_list.items: # Changed variable name for clarity
                    assert isinstance(scan_item, ScanResponse) # Changed to ScanResponse
                    print(f"  - 扫描 ID: {scan_item.scan_id}, 目标 ID: {scan_item.target_id}, 状态: {scan_item.current_session.status if scan_item.current_session else 'N/A'}")
            else:
                print("服务器上没有扫描记录，或者当前用户无权查看。")
        except AcunetixError as e:
            pytest.fail(f"列出扫描记录时发生 AcunetixError: {e}")
        except Exception as e:
            pytest.fail(f"列出扫描记录时发生未知错误: {e}")

    def test_get_scan_details(self, real_sync_client: AcunetixSyncClient):
        """测试获取单个扫描的详细信息。"""
        try:
            print("测试: 尝试获取扫描详情")
            scans_paginated_list = real_sync_client.scans.list(limit=1)
            if not scans_paginated_list.items:
                pytest.skip("服务器上没有可用的扫描记录来获取详情。")

            first_scan_brief = scans_paginated_list.items[0]
            assert first_scan_brief.scan_id is not None
            scan_id_to_get = first_scan_brief.scan_id
            
            print(f"测试: 尝试获取扫描 ID: {scan_id_to_get} 的详细信息")
            scan_details = real_sync_client.scans.get(scan_id_to_get)
            
            assert scan_details is not None
            assert isinstance(scan_details, ScanResponse)
            assert scan_details.scan_id == scan_id_to_get
            
            # Ensure we are comparing the top-level target_id from both ScanResponse objects
            assert hasattr(first_scan_brief, 'target_id'), "first_scan_brief (ScanResponse) should have target_id"
            assert first_scan_brief.target_id is not None, "first_scan_brief.target_id should not be None"
            assert scan_details.target_id == first_scan_brief.target_id

            print(f"测试: 成功获取扫描 ID: {scan_details.scan_id} 的详细信息。")
            # scan_details.target is an EmbeddedTarget which might have a None address if not fully populated by API
            # For address, it's safer to rely on the target details from a dedicated target get if needed,
            # or ensure the EmbeddedTarget in ScanResponse is consistently populated.
            # For now, let's check if scan_details.target exists before accessing its address.
            target_address_info = "N/A"
            if scan_details.target and scan_details.target.address:
                target_address_info = str(scan_details.target.address)
            print(f"  目标地址: {target_address_info}")
            print(f"  当前状态: {scan_details.current_session.status if scan_details.current_session else 'N/A'}")

        except AcunetixError as e:
            pytest.fail(f"获取扫描详情时发生 AcunetixError: {e}")
        except Exception as e:
            pytest.fail(f"获取扫描详情时发生未知错误: {e}")

    def test_scan_actions_abort(self, real_sync_client: AcunetixSyncClient, managed_target: TargetResponse, managed_scan_profile: ScanningProfile):
        """测试启动扫描然后中止它。"""
        target_id = managed_target.target_id
        profile_id = managed_scan_profile.profile_id
        scan_id: Optional[str] = None

        try:
            print(f"测试: 准备为目标 {target_id} 使用配置文件 {profile_id} 启动扫描以进行中止测试。")
            schedule_config = ScanSchedule(disable=False)
            scan_request = ScanScheduleRequest(target_id=target_id, profile_id=profile_id, schedule=schedule_config)
            
            created_scan = real_sync_client.scans.create(scan_request)
            assert created_scan and created_scan.scan_id
            scan_id = created_scan.scan_id
            print(f"测试: 扫描 {scan_id} 已创建。等待其进入 'scanning' 状态...")

            # 等待扫描开始 (轮询状态)
            max_wait_time_seconds = 120  # 等待最多2分钟
            poll_interval_seconds = 5
            start_time = time.time()
            current_status = ""

            while time.time() - start_time < max_wait_time_seconds:
                scan_details = real_sync_client.scans.get(scan_id)
                current_status = scan_details.current_session.status if scan_details.current_session else "unknown"
                print(f"测试: 扫描 {scan_id} 当前状态: {current_status}")
                if current_status == "scanning":
                    break
                if current_status in ["completed", "aborted", "failed"]: # 最终状态
                    pytest.fail(f"扫描 {scan_id} 在尝试中止前已进入最终状态: {current_status}")
                time.sleep(poll_interval_seconds)
            
            if current_status != "scanning":
                pytest.skip(f"扫描 {scan_id} 在 {max_wait_time_seconds} 秒内未进入 'scanning' 状态 (当前: {current_status})。跳过中止测试。")

            # 中止扫描
            print(f"测试: 尝试中止扫描 {scan_id}")
            real_sync_client.scans.abort(scan_id)
            print(f"测试: 中止扫描 {scan_id} 的请求已发送。等待其进入 'aborted' 状态...")

            # 等待扫描中止
            start_time_abort = time.time()
            aborted_status_verified = False
            while time.time() - start_time_abort < max_wait_time_seconds: # Re-use max_wait_time for abort confirmation
                scan_details_after_abort = real_sync_client.scans.get(scan_id)
                current_status_after_abort = scan_details_after_abort.current_session.status if scan_details_after_abort.current_session else "unknown"
                print(f"测试: 扫描 {scan_id} 中止后状态: {current_status_after_abort}")
                if current_status_after_abort == "aborted":
                    aborted_status_verified = True
                    break
                time.sleep(poll_interval_seconds)
            
            assert aborted_status_verified, f"扫描 {scan_id} 在中止后 {max_wait_time_seconds} 秒内未确认为 'aborted' 状态 (当前: {current_status_after_abort})。"
            print(f"测试: 扫描 {scan_id} 已成功中止并验证。")

        except AcunetixError as e:
            pytest.fail(f"中止扫描 {scan_id} 测试时发生 AcunetixError: {e}")
        except Exception as e:
            pytest.fail(f"中止扫描 {scan_id} 测试时发生未知错误: {e}")
        finally:
            # 虽然扫描已中止，但记录可能仍然存在。通常不需要显式删除扫描记录。
            # 如果需要，可以在这里添加清理逻辑，但 Acunetix 通常会自行管理扫描历史。
            pass

    def test_list_scan_vulnerabilities(self, real_sync_client: AcunetixSyncClient):
        """测试列出特定扫描的漏洞。"""
        # 首先，找到一个已完成的扫描以获取漏洞
        # 为了测试的独立性和速度，理想情况下我们应该有一个已知的已完成扫描ID
        # 或者，我们可以启动一个扫描并等待它完成，但这会使测试非常慢。
        # 这里我们尝试获取最近的已完成扫描。
        print("测试: 尝试查找一个已完成的扫描以列出其漏洞。")
        # Removed sort="-start_date" as it caused an API error.
        # Rely on query="status:completed" and then pick one.
        scans_paginated_list = real_sync_client.scans.list(limit=10, query="status:completed") 
        
        completed_scan_item: Optional[ScanResponse] = None
        if scans_paginated_list.items:
            for scan_item in scans_paginated_list.items: # scan_item is ScanResponse
                if scan_item.current_session and scan_item.current_session.severity_counts: # Check severity_counts
                    counts = scan_item.current_session.severity_counts
                    if (counts.critical or 0) + (counts.high or 0) + (counts.medium or 0) + (counts.low or 0) + (counts.info or 0) > 0:
                        completed_scan_item = scan_item
                        print(f"测试: 找到已完成且有漏洞的扫描: {completed_scan_item.scan_id}")
                        break
            if not completed_scan_item and scans_paginated_list.items: # Fallback
                completed_scan_item = scans_paginated_list.items[0]
                print(f"测试: 未找到有漏洞的已完成扫描，使用第一个已完成扫描: {completed_scan_item.scan_id} (可能没有漏洞)")

        if not completed_scan_item:
            pytest.skip("未能找到已完成的扫描来测试列出漏洞。请确保服务器上有已完成的扫描。")
            return

        scan_id_for_vulns = completed_scan_item.scan_id
        assert completed_scan_item.current_session is not None, "已完成的扫描应有 current_session"
        assert completed_scan_item.current_session.scan_session_id is not None, "已完成扫描的 current_session 应有 scan_session_id (即 result_id)"
        result_id_for_vulns = completed_scan_item.current_session.scan_session_id
        
        print(f"测试: 将使用扫描 ID: {scan_id_for_vulns} 和结果 ID: {result_id_for_vulns} 来列出漏洞。")
        
        vulnerabilities_paginated = None # Initialize to None
        try:
            vulnerabilities_paginated = real_sync_client.scans.get_vulnerabilities(
                scan_id=scan_id_for_vulns,
                result_id=result_id_for_vulns,
                limit=5
            )
            assert vulnerabilities_paginated is not None, "get_vulnerabilities 应返回 PaginatedList 对象，而不是 None"
            assert isinstance(vulnerabilities_paginated.items, list), "PaginatedList.items 应为列表"
            print(f"测试: 成功为扫描 {scan_id_for_vulns} (结果 {result_id_for_vulns}) 获取到 {len(vulnerabilities_paginated.items)} 条漏洞 (最多5条)。")

            if vulnerabilities_paginated.items:
                for vuln in vulnerabilities_paginated.items:
                    assert isinstance(vuln, Vulnerability)
                    print(f"  - 漏洞 ID: {vuln.vuln_id}, 名称: {vuln.vt_name}, 严重性: {vuln.severity}")
            else:
                print(f"扫描 {scan_id_for_vulns} (结果 {result_id_for_vulns}) 没有发现漏洞，或者当前用户无权查看。")

        except AcunetixError as e:
            pytest.fail(f"为扫描 {scan_id_for_vulns} (结果 {result_id_for_vulns}) 列出漏洞时发生 AcunetixError: {e}")
        except ValidationError as ve:
            pytest.fail(f"为扫描 {scan_id_for_vulns} (结果 {result_id_for_vulns}) 列出漏洞时发生 Pydantic ValidationError: {ve}")
        except Exception as e:
            # Print type of exception for better debugging
            error_type = type(e).__name__
            # If vulnerabilities_paginated is still None here, it means the call to get_vulnerabilities failed before assignment
            # or it was assigned None and the first assert failed.
            if vulnerabilities_paginated is None and not isinstance(e, (AcunetixError, ValidationError)):
                 pytest.fail(f"调用 get_vulnerabilities 失败或返回 None (扫描 {scan_id_for_vulns}, 结果 {result_id_for_vulns})，原始错误 ({error_type}): {e}")
            else:
                 pytest.fail(f"为扫描 {scan_id_for_vulns} (结果 {result_id_for_vulns}) 列出漏洞时发生未知错误 ({error_type}): {e}")

    def test_list_scan_sessions(self, real_sync_client: AcunetixSyncClient):
        """测试列出特定扫描的会话。"""
        print("测试: 尝试查找一个扫描以列出其会话。")
        scans_list = real_sync_client.scans.list(limit=1) # Get any recent scan
        
        if not scans_list.items:
            pytest.skip("未能找到扫描来测试列出其会话。")
            return
            
        scan_id_for_sessions = scans_list.items[0].scan_id
        assert scan_id_for_sessions is not None
        print(f"测试: 将使用扫描 ID: {scan_id_for_sessions} 来列出扫描会话。")

        try:
            # Use client.scans.get_results(scan_id) which returns PaginatedList[ScanResultItemResponse]
            scan_results_paginated = real_sync_client.scans.get_results(scan_id_for_sessions, limit=5) 
            
            assert scan_results_paginated is not None
            assert isinstance(scan_results_paginated.items, list)
            print(f"测试: 成功为扫描 {scan_id_for_sessions} 获取到 {len(scan_results_paginated.items)} 个扫描结果/会话 (最多5个)。")

            if scan_results_paginated.items:
                for result_item in scan_results_paginated.items: # result_item is ScanResultItemResponse
                    assert isinstance(result_item, ScanResultItemResponse) 
                    print(f"  - 结果/会话 ID: {result_item.result_id}, 状态: {result_item.status}, 开始日期: {result_item.start_date}, 结束日期: {result_item.end_date}")
            else:
                print(f"扫描 {scan_id_for_sessions} 没有结果/会话记录。")

        except AcunetixError as e:
            pytest.fail(f"为扫描 {scan_id_for_sessions} 列出扫描会话时发生 AcunetixError: {e}")
        except Exception as e:
            pytest.fail(f"为扫描 {scan_id_for_sessions} 列出扫描会话时发生未知错误: {e}")
