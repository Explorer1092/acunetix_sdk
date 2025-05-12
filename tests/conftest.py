# tests/conftest.py
import pytest
import os
from typing import Optional, List
import uuid
import base64

from acunetix_sdk import AcunetixSyncClient, AcunetixError
from acunetix_sdk.models.target import TargetCreateRequest, TargetResponse
from acunetix_sdk.models.target_group import TargetGroupCreateRequest, TargetGroup # Changed TargetGroupResponse to TargetGroup
from acunetix_sdk.models.notification import Notification, NotificationCreateRequest, NotificationScope, NotificationEvent
from acunetix_sdk.models.report_template import ReportTemplate, ReportTemplateCreateRequest, ReportTemplateType
from acunetix_sdk.models.scan_profile import (
    ScanningProfile, ScanProfileCreateRequest, ScanProfileGeneralSettings,
    ScanProfileHttpSettings, ScanProfileScanningSettings, ScanProfileScriptingSettings,
    ScanProfileTechnologies, ScanProfileLogin, ScanProfileSensor, ScanProfileCustomHeader as ScanProfileCustomHeaderModel, # Renamed to avoid conflict
    ScanProfileCustomCookie, ScanProfileWaf, ScanProfileReport, ScanProfileExcludedElement,
    ScanProfilePreseedFile, ScanProfileProxy, ScanProfileCvss, ScanProfileAdvanced
)
from acunetix_sdk.models.target import TargetSettings, CustomHeader, TargetConfigurationData # Added TargetConfigurationData
# Placeholder for REAL_API_KEY and REAL_ENDPOINT
# For security, it's better to use environment variables.
# REAL_API_KEY = os.environ.get("ACUNETIX_REAL_API_KEY", "YOUR_FALLBACK_API_KEY_HERE")
# REAL_ENDPOINT = os.environ.get("ACUNETIX_REAL_ENDPOINT", "YOUR_FALLBACK_ENDPOINT_HERE")

REAL_API_KEY = ""
REAL_ENDPOINT = ""  # SDK handles https and /api/v1/

@pytest.fixture(scope="session") # Changed to session scope for client
def real_sync_client():
    """
    Provides a synchronous client instance connected to a real Acunetix server.
    SSL verification is typically disabled for IP addresses.
    """
    client = AcunetixSyncClient(
        api_key=REAL_API_KEY,
        endpoint=REAL_ENDPOINT,
        verify_ssl=False
    )
    yield client
    # If client had a close method: client.close()

@pytest.fixture(scope="function")
def managed_target(real_sync_client: AcunetixSyncClient):
    """
    Fixture to create a target before a test and delete it afterwards.
    Yields the created target object.
    """
    target_address = f"http://testhtml5.vulnweb.com/sdk-test-{uuid.uuid4().hex[:8]}/" # Unique address
    target_description = "真实服务器测试目标 (SDK Fixture)"
    created_target_object: Optional[TargetResponse] = None
    
    try:
        print(f"Fixture (conftest): 尝试创建目标: {target_address}")
        target_to_create = TargetCreateRequest(address=target_address, description=target_description, criticality=10)
        created_target_object = real_sync_client.targets.create(target_to_create)
        assert created_target_object is not None
        assert created_target_object.target_id is not None
        print(f"Fixture (conftest): 成功创建目标 ID: {created_target_object.target_id}")
        yield created_target_object
    finally:
        if created_target_object and created_target_object.target_id:
            try:
                print(f"Fixture (conftest): 尝试删除目标 ID: {created_target_object.target_id}")
                real_sync_client.targets.delete(created_target_object.target_id)
                print(f"Fixture (conftest): 成功删除目标 ID: {created_target_object.target_id}")
            except AcunetixError as e:
                print(f"Fixture (conftest): 删除目标 {created_target_object.target_id} 时发生 AcunetixError: {e}")
            except Exception as e:
                print(f"Fixture (conftest): 删除目标 {created_target_object.target_id} 时发生未知错误: {e}")

@pytest.fixture(scope="function")
def managed_target_group(real_sync_client: AcunetixSyncClient):
    """
    Fixture to create a target group before a test and delete it afterwards.
    Yields the created target group object.
    """
    group_name = f"测试目标组 (SDK Fixture {uuid.uuid4()})"
    group_description = "这是一个通过 SDK Fixture 创建和管理的临时目标组"
    created_group_object: Optional[TargetGroup] = None # Changed TargetGroupResponse to TargetGroup

    try:
        print(f"Fixture (conftest): 尝试创建目标组: {group_name}")
        group_to_create = TargetGroupCreateRequest(name=group_name, description=group_description)
        created_group_object = real_sync_client.target_groups.create(group_to_create)
        assert created_group_object is not None
        assert created_group_object.group_id is not None
        print(f"Fixture (conftest): 成功创建目标组 ID: {created_group_object.group_id}, 名称: {created_group_object.name}")
        yield created_group_object
    finally:
        if created_group_object and created_group_object.group_id:
            try:
                print(f"Fixture (conftest): 尝试删除目标组 ID: {created_group_object.group_id}")
                real_sync_client.target_groups.delete(created_group_object.group_id)
                print(f"Fixture (conftest): 成功删除目标组 ID: {created_group_object.group_id}")
            except AcunetixError as e:
                print(f"Fixture (conftest): 删除目标组 {created_group_object.group_id} 时发生 AcunetixError: {e}")
            except Exception as e:
                print(f"Fixture (conftest): 删除目标组 {created_group_object.group_id} 时发生未知错误: {e}")

@pytest.fixture(scope="function")
def managed_notification(real_sync_client: AcunetixSyncClient):
    """
    Fixture to create a notification before a test and delete it afterwards.
    Yields the created notification object.
    """
    notification_name = f"测试通知 (SDK Fixture {uuid.uuid4()})"
    notification_to_create = NotificationCreateRequest(
        name=notification_name,
        event=NotificationEvent.SCAN_COMPLETED,
        scope=NotificationScope(type="all_targets"),
        disabled=False,
        email_address=["test@example.com"],
    )
    created_notification_object: Optional[Notification] = None

    try:
        print(f"Fixture (conftest): 尝试创建通知: {notification_name}")
        created_notification_object = real_sync_client.notifications.create(notification_to_create)
        assert created_notification_object is not None
        assert created_notification_object.notification_id is not None
        print(f"Fixture (conftest): 成功创建通知 ID: {created_notification_object.notification_id}, 名称: {created_notification_object.name}")
        yield created_notification_object
    finally:
        if created_notification_object and created_notification_object.notification_id:
            try:
                print(f"Fixture (conftest): 尝试删除通知 ID: {created_notification_object.notification_id}")
                real_sync_client.notifications.delete(created_notification_object.notification_id)
                print(f"Fixture (conftest): 成功删除通知 ID: {created_notification_object.notification_id}")
            except AcunetixError as e:
                print(f"Fixture (conftest): 删除通知 {created_notification_object.notification_id} 时发生 AcunetixError: {e}")
            except Exception as e:
                print(f"Fixture (conftest): 删除通知 {created_notification_object.notification_id} 时发生未知错误: {e}")

@pytest.fixture(scope="function")
def managed_report_template(real_sync_client: AcunetixSyncClient):
    """
    Fixture to create a report template before a test and delete it afterwards.
    Yields the created report template object.
    """
    template_name = f"测试报告模板 (SDK Fixture {uuid.uuid4()})"
    template_description = "这是一个通过 SDK Fixture 创建和管理的临时报告模板"
    minimal_xslt_content = '<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"></xsl:stylesheet>'
    base64_content = base64.b64encode(minimal_xslt_content.encode('utf-8')).decode('utf-8')

    template_to_create = ReportTemplateCreateRequest(
        name=template_name,
        description=template_description,
        type=ReportTemplateType.SCAN,
        content=base64_content
    )
    created_template_object: Optional[ReportTemplate] = None

    try:
        print(f"Fixture (conftest): 尝试创建报告模板: {template_name}")
        created_template_object = real_sync_client.report_templates.create(template_to_create)
        assert created_template_object is not None
        assert created_template_object.template_id is not None
        print(f"Fixture (conftest): 成功创建报告模板 ID: {created_template_object.template_id}, 名称: {created_template_object.name}")
        yield created_template_object
    finally:
        if created_template_object and created_template_object.template_id:
            try:
                print(f"Fixture (conftest): 尝试删除报告模板 ID: {created_template_object.template_id}")
                real_sync_client.report_templates.delete(created_template_object.template_id)
                print(f"Fixture (conftest): 成功删除报告模板 ID: {created_template_object.template_id}")
            except AcunetixError as e:
                print(f"Fixture (conftest): 删除报告模板 {created_template_object.template_id} 时发生 AcunetixError: {e}")
            except Exception as e:
                print(f"Fixture (conftest): 删除报告模板 {created_template_object.template_id} 时发生未知错误: {e}")

@pytest.fixture(scope="function")
def managed_scan_profile(real_sync_client: AcunetixSyncClient):
    """
    Fixture to create a scan profile before a test and delete it afterwards.
    Yields the created scan profile object.
    """
    profile_name = f"测试扫描配置 (SDK Fixture {uuid.uuid4()})"
    profile_description = "这是一个通过 SDK Fixture 创建和管理的临时扫描配置"
    general_settings = ScanProfileGeneralSettings(scan_speed="fast")
    http_settings = ScanProfileHttpSettings(user_agent="Acunetix SDK Test Agent", request_concurrency=10)
    scanning_settings = ScanProfileScanningSettings(case_sensitive=True, limit_crawler_scope=True, excluded_paths=[])
    scripting_settings = ScanProfileScriptingSettings(custom_scripts=[])
    technologies = ScanProfileTechnologies(server=["Apache"], os=["Linux"], backend=["PHP"])
    login = ScanProfileLogin(kind="none")
    sensor = ScanProfileSensor(sensor_token=None, sensor_secret=None, acu_sensor_bridge=None)
    custom_headers: List[ScanProfileCustomHeader] = []
    custom_cookies: List[ScanProfileCustomCookie] = []
    waf = ScanProfileWaf(name="generic", bypass_rules=[])
    report = ScanProfileReport(false_positives=False, format="html", generate=False, type="scan", email_address=None)
    excluded_elements: List[ScanProfileExcludedElement] = []
    preseed_files: List[ScanProfilePreseedFile] = []
    proxy = ScanProfileProxy(enabled=False, address=None, port=None, protocol=None, username=None, password=None, use_auth=False)
    cvss = ScanProfileCvss(enabled=False)
    advanced = ScanProfileAdvanced(enable_port_scanning=False, network_scan_type=None, enable_audio_import=False, enable_crl_check=False, parallel_scans=None, client_certificate_password=None, custom_settings=[])

    profile_to_create = ScanProfileCreateRequest(
        name=profile_name, description=profile_description, general=general_settings, http=http_settings,
        scanning=scanning_settings, scripting=scripting_settings, technologies=technologies, login=login,
        sensor=sensor, custom_headers=custom_headers, custom_cookies=custom_cookies, waf=waf, report=report,
        excluded_elements=excluded_elements, preseed_files=preseed_files, proxy=proxy, cvss=cvss, advanced=advanced,
        checks=[]  # 添加 checks 字段，默认为空列表
    )
    created_profile_object: Optional[ScanningProfile] = None

    try:
        print(f"Fixture (conftest): 尝试创建扫描配置: {profile_name}")
        created_profile_object = real_sync_client.scan_profiles.create(profile_to_create)
        assert created_profile_object is not None
        assert created_profile_object.profile_id is not None
        print(f"Fixture (conftest): 成功创建扫描配置 ID: {created_profile_object.profile_id}, 名称: {created_profile_object.name}")
        yield created_profile_object
    finally:
        if created_profile_object and created_profile_object.profile_id:
            try:
                print(f"Fixture (conftest): 尝试删除扫描配置 ID: {created_profile_object.profile_id}")
                real_sync_client.scan_profiles.delete(created_profile_object.profile_id)
                print(f"Fixture (conftest): 成功删除扫描配置 ID: {created_profile_object.profile_id}")
            except AcunetixError as e:
                print(f"Fixture (conftest): 删除扫描配置 {created_profile_object.profile_id} 时发生 AcunetixError: {e}")
            except Exception as e:
                print(f"Fixture (conftest): 删除扫描配置 {created_profile_object.profile_id} 时发生未知错误: {e}")

@pytest.fixture(scope="function")
def managed_target_with_custom_settings(real_sync_client: AcunetixSyncClient):
    """
    Fixture to create a target with custom settings (headers, user_agent)
    and delete it afterwards. Yields the created target object.
    """
    target_address = f"http://testhtml5.vulnweb.com/sdk-custom-{uuid.uuid4().hex[:8]}/"
    target_description = "真实服务器自定义设置测试目标 (SDK Fixture)"
    custom_user_agent = "SDK Test Custom Agent/1.0"
    custom_headers_list = [CustomHeader(name="X-Custom-Test-Header", value="SDK-Test-Value")]
    
    # Step 1: Create target without custom settings initially
    target_to_create = TargetCreateRequest(
        address=target_address,
        description=target_description,
        criticality=10
        # settings are not part of the main Target creation payload as per API spec
    )
    created_target_object: Optional[TargetResponse] = None
    
    try:
        print(f"Fixture (conftest): 尝试创建目标 (无自定义设置): {target_address}")
        created_target_object = real_sync_client.targets.create(target_to_create)
        assert created_target_object is not None
        assert created_target_object.target_id is not None
        target_id = created_target_object.target_id
        print(f"Fixture (conftest): 成功创建目标 ID: {target_id}")

        # Step 2: Update configuration with custom settings
        print(f"Fixture (conftest): 尝试为目标 ID: {target_id} 更新配置")
        # Convert List[CustomHeader] to List[str] for TargetConfigurationData
        custom_headers_str_list = [f"{h.name}: {h.value}" for h in custom_headers_list]
        
        # Construct TargetConfigurationData with only the fields to update
        # Other fields in TargetConfigurationData are Optional, so they won't be sent if None.
        config_to_update = TargetConfigurationData(
            user_agent=custom_user_agent,
            custom_headers=custom_headers_str_list
            # Ensure other fields are not unintentionally set to defaults if they should be inherited
            # For a clean update, only provide fields that are being explicitly set.
            # Pydantic's model_dump(exclude_none=True) in the resource method will handle this.
        )
        real_sync_client.targets.update_configuration(target_id, config_to_update)
        print(f"Fixture (conftest): 成功为目标 ID: {target_id} 更新配置")
        
        # Yield the original created_target_object (TargetResponse) as the fixture value
        # The test will then use get_configuration to verify.
        yield created_target_object
    finally:
        if created_target_object and created_target_object.target_id:
            try:
                print(f"Fixture (conftest): 尝试删除带自定义设置的目标 ID: {created_target_object.target_id}")
                real_sync_client.targets.delete(created_target_object.target_id)
                print(f"Fixture (conftest): 成功删除带自定义设置的目标 ID: {created_target_object.target_id}")
            except AcunetixError as e:
                print(f"Fixture (conftest): 删除带自定义设置的目标 {created_target_object.target_id} 时发生 AcunetixError: {e}")
            except Exception as e:
                print(f"Fixture (conftest): 删除带自定义设置的目标 {created_target_object.target_id} 时发生未知错误: {e}")
