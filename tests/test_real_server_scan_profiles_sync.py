# tests/test_real_server_scan_profiles_sync.py
import pytest
from typing import List # For type hinting if needed

from acunetix_sdk import AcunetixSyncClient, AcunetixError
from acunetix_sdk.models.scan_profile import (
    ScanProfile, ScanningProfile, ScanProfileUpdateRequest, ScanProfileGeneralSettings
)
# Fixtures real_sync_client and managed_scan_profile are implicitly available from conftest.py

class TestAcunetixRealServerScanProfilesSync:
    def test_list_scan_profiles(self, real_sync_client: AcunetixSyncClient):
        """测试列出扫描配置文件。"""
        try:
            print("测试: 尝试列出扫描配置文件")
            profile_list = real_sync_client.scan_profiles.list() # list() returns List[ScanningProfile]
            assert profile_list is not None
            assert isinstance(profile_list, list)
            print(f"测试: 成功获取到 {len(profile_list)} 个扫描配置文件。")
            if profile_list:
                for profile in profile_list:
                    assert isinstance(profile, ScanningProfile)
                    print(f"  - 配置文件 ID: {profile.profile_id}, 名称: {profile.name}")
            else:
                print("服务器上没有扫描配置文件。")
        except AcunetixError as e:
            pytest.fail(f"列出扫描配置文件时发生 AcunetixError: {e}")
        except Exception as e:
            pytest.fail(f"列出扫描配置文件时发生未知错误: {e}")

    def test_scan_profile_lifecycle(self, real_sync_client: AcunetixSyncClient, managed_scan_profile: ScanningProfile):
        """测试扫描配置文件的创建 (通过 fixture)、获取和更新。"""
        created_profile_id = managed_scan_profile.profile_id
        original_name = managed_scan_profile.name
        # original_description will be None as per current API behavior and SDK model
        original_description = managed_scan_profile.description 
        assert original_description is None, "Expected original description to be None based on API spec"

        print(f"测试: 使用 fixture 创建的扫描配置文件 ID: {created_profile_id}, 名称: {original_name}, 原始描述: {original_description}")

        # 1. 获取扫描配置文件
        try:
            print(f"测试: 尝试获取扫描配置文件 ID: {created_profile_id}")
            fetched_profile = real_sync_client.scan_profiles.get(created_profile_id) # Returns ScanningProfile
            assert fetched_profile is not None
            assert isinstance(fetched_profile, ScanningProfile) # Changed to ScanningProfile
            assert fetched_profile.profile_id == created_profile_id
            assert fetched_profile.name == original_name
            assert fetched_profile.description == original_description # This will assert None == None
            print(f"测试: 成功获取扫描配置文件 ID: {fetched_profile.profile_id}")
        except AcunetixError as e:
            pytest.fail(f"获取扫描配置文件 {created_profile_id} 时发生 AcunetixError: {e}")
        except Exception as e:
            pytest.fail(f"获取扫描配置文件 {created_profile_id} 时发生未知错误: {e}")

        # 2. 更新扫描配置文件
        updated_name = f"{original_name} (已更新)"
        # updated_description = f"{original_description} - (已更新描述)" # Not updating description as it's not in API spec
        # updated_scan_speed = "slow" # Cannot update scan_speed this way
        try:
            print(f"测试: 尝试更新扫描配置文件 ID: {created_profile_id} (只更新名称)")
            
            # Only update fields that are part of the API's ScanningProfile definition for PATCH.
            # This means 'name' and 'checks'. 'description' is not in the API spec for ScanningProfile.
            update_payload_for_api = ScanningProfile(
                name=updated_name,
                checks=managed_scan_profile.checks, # Preserve original checks
                # description is omitted as it's not in the API spec's ScanningProfile definition
                # and appears to be ignored by the server or not settable.
            )
            
            real_sync_client.scan_profiles.update(created_profile_id, update_payload_for_api)
            print(f"测试: 更新扫描配置文件 ID: {created_profile_id} 的请求已发送")

            verified_updated_profile = real_sync_client.scan_profiles.get(created_profile_id)
            assert verified_updated_profile.name == updated_name
            # Since description is not updated, it should remain as it was (None).
            assert verified_updated_profile.description is None 
            print(f"测试: 成功验证扫描配置文件 ID: {created_profile_id} 的更新 (名称已更新, 描述应为 None)")

        except AcunetixError as e:
            pytest.fail(f"更新扫描配置文件 {created_profile_id} 时发生 AcunetixError: {e}")
        except Exception as e:
            pytest.fail(f"更新扫描配置文件 {created_profile_id} 时发生未知错误: {e}")
