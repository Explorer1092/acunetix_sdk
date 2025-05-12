# tests/test_real_server_targets_sync.py
import pytest
from typing import Optional # For type hinting if needed directly in tests

from acunetix_sdk import AcunetixSyncClient, AcunetixError
from acunetix_sdk.models.target import (
    TargetResponse, 
    TargetUpdateRequest, 
    TargetSettings, 
    CustomHeader,
    TargetConfigurationData # Added import
)
# Fixtures real_sync_client, managed_target, managed_target_with_custom_settings 
# are implicitly available from conftest.py

class TestAcunetixRealServerTargetsSync:
    def test_connection_and_list_targets(self, real_sync_client: AcunetixSyncClient):
        """
        测试与真实服务器的连接并通过列出目标来进行基本API调用。
        """
        try:
            targets_paginated_list = real_sync_client.targets.list(limit=5)
            assert targets_paginated_list is not None
            assert isinstance(targets_paginated_list.items, list)
            print(f"成功连接到服务器并获取到 {len(targets_paginated_list.items)} 个目标。")
            if targets_paginated_list.items:
                for target in targets_paginated_list.items:
                    # In conftest, managed_target creates TargetResponse, so list items should also be TargetResponse
                    # The API for GET /targets returns TargetResponse objects in the list.
                    assert isinstance(target, TargetResponse) 
                    print(f"  - 目标 ID: {target.target_id}, 地址: {target.address}")
            else:
                print("服务器上没有配置目标，或者API密钥权限不足以查看。")

        except AcunetixError as e:
            pytest.fail(f"与真实服务器交互时发生 AcunetixError: {e}")
        except Exception as e:
            pytest.fail(f"与真实服务器交互时发生未知错误: {e}")

    def test_target_lifecycle(self, real_sync_client: AcunetixSyncClient, managed_target: TargetResponse):
        """
        测试获取和更新由 fixture 管理的目标。
        """
        created_target_id = managed_target.target_id
        original_address = str(managed_target.address) # Address can be HttpUrl type
        original_description = managed_target.description
        
        print(f"测试: 使用 fixture 创建的目标 ID: {created_target_id}")

        # 1. 获取目标
        try:
            print(f"测试: 尝试获取目标 ID: {created_target_id}")
            fetched_target = real_sync_client.targets.get(created_target_id)
            assert fetched_target is not None
            assert fetched_target.target_id == created_target_id
            assert str(fetched_target.address) == original_address
            assert fetched_target.description == original_description
            print(f"测试: 成功获取目标 ID: {fetched_target.target_id}")
        except AcunetixError as e:
            pytest.fail(f"获取目标 {created_target_id} 时发生 AcunetixError: {e}")
        except Exception as e:
            pytest.fail(f"获取目标 {created_target_id} 时发生未知错误: {e}")

        # 2. 更新目标
        updated_description = f"{original_description} (已更新)"
        updated_criticality = 20
        try:
            print(f"测试: 尝试更新目标 ID: {created_target_id}")
            update_payload = TargetUpdateRequest(description=updated_description, criticality=updated_criticality)
            real_sync_client.targets.update(created_target_id, update_payload) # Update method returns None
            # assert updated_target_response is not None # This was the error
            # assert updated_target_response.target_id == created_target_id # Cannot check response object
            print(f"测试: 更新目标 ID: {created_target_id} 的请求已发送。")

            # 验证更新
            verified_updated_target = real_sync_client.targets.get(created_target_id)
            assert verified_updated_target.description == updated_description
            assert verified_updated_target.criticality == updated_criticality
            print(f"测试: 成功验证目标 ID: {created_target_id} 的更新")

        except AcunetixError as e:
            pytest.fail(f"更新目标 {created_target_id} 时发生 AcunetixError: {e}")
        except Exception as e:
            pytest.fail(f"更新目标 {created_target_id} 时发生未知错误: {e}")

    def test_target_creation_with_custom_settings(self, real_sync_client: AcunetixSyncClient, managed_target_with_custom_settings: TargetResponse):
        """
        测试创建具有自定义设置（用户代理、自定义头部）的目标，并验证这些设置。
        """
        target_id = managed_target_with_custom_settings.target_id
        print(f"测试: 使用 fixture 创建的带自定义设置的目标 ID: {target_id}")

        expected_user_agent = "SDK Test Custom Agent/1.0" # Must match what's in conftest.py
        expected_custom_header = CustomHeader(name="X-Custom-Test-Header", value="SDK-Test-Value")

        try:
            print(f"测试: 尝试获取目标 ID: {target_id} 的配置以验证自定义设置")
            # fetched_target = real_sync_client.targets.get(target_id) # This does not return settings
            target_config = real_sync_client.targets.get_configuration(target_id)
            
            assert target_config is not None, "获取到的目标配置不应为 None"
            
            # 验证 User-Agent from TargetConfigurationData
            assert target_config.user_agent == expected_user_agent, \
                f"User-Agent 不匹配。预期: '{expected_user_agent}', 实际: '{target_config.user_agent}'"
            print(f"测试: User-Agent 验证成功: '{target_config.user_agent}'")

            # 验证自定义头部 from TargetConfigurationData
            assert target_config.custom_headers is not None, "自定义头部列表不应为 None"
            # The custom_headers in TargetConfigurationData is List[str] in "Header: Value" format
            # Need to parse it or compare differently if CustomHeader model is used for expected.
            # For now, let's check if the expected header string is present.
            expected_header_string = f"{expected_custom_header.name}: {expected_custom_header.value}"
            
            found_header = False
            for header_str in target_config.custom_headers:
                if header_str.strip() == expected_header_string.strip():
                    found_header = True
                    break
            assert found_header, f"未能找到预期的自定义头部 '{expected_header_string}'"
            print(f"测试: 自定义头部验证成功: '{expected_header_string}'")
            
            print(f"测试: 成功验证目标 ID: {target_id} 的自定义设置")

        except AcunetixError as e:
            pytest.fail(f"获取或验证带自定义设置的目标 {target_id} 时发生 AcunetixError: {e}")
        except AssertionError as e:
            pytest.fail(f"验证带自定义设置的目标 {target_id} 时断言失败: {e}")
        except Exception as e:
            pytest.fail(f"获取或验证带自定义设置的目标 {target_id} 时发生未知错误 ({type(e).__name__}): {e}")
