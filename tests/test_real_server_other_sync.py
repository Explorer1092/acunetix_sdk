# tests/test_real_server_other_sync.py
import pytest
from typing import List, Optional # For type hinting if needed
import uuid # For managed fixtures if any were left here (they are in conftest)

from acunetix_sdk import AcunetixSyncClient, AcunetixError

# Models for tests in this file
from acunetix_sdk.models.notification import Notification, NotificationUpdateRequest, NotificationScope, NotificationEvent
from acunetix_sdk.models.report_template import ReportTemplate, ReportTemplateUpdateRequest, ReportTemplateType
from acunetix_sdk.models.user import UserBrief, RoleDetails # Added RoleDetails
from acunetix_sdk.models.excluded_hours import ExcludedHoursProfile # Changed from ExcludedHours
from acunetix_sdk.models.issue_tracker import IssueTrackerEntry as IssueTracker, IssueTrackerList # Changed from IssueTracker, Added IssueTrackerList
from acunetix_sdk.models.waf import WAFEntry as WAF, WAFsList # Changed from WAF, Added WAFsList
from acunetix_sdk.models.worker import Worker
from acunetix_sdk.models.agent import AgentsConfig
from acunetix_sdk.models.export import Export
from acunetix_sdk.models.report import Report
from acunetix_sdk.models.pagination import PaginatedList # Added PaginatedList

# Fixtures real_sync_client, managed_notification, managed_report_template
# are implicitly available from conftest.py

class TestAcunetixRealServerOtherSync:
    def test_list_notifications(self, real_sync_client: AcunetixSyncClient):
        """测试列出通知。"""
        try:
            print("测试: 尝试列出通知")
            notifications_list = real_sync_client.notifications.list()
            assert notifications_list is not None
            assert isinstance(notifications_list, list)
            print(f"测试: 成功获取到 {len(notifications_list)} 条通知。")
            if notifications_list:
                for notification_item in notifications_list: # Renamed to avoid conflict
                    assert isinstance(notification_item, Notification)
                    print(f"  - 通知 ID: {notification_item.notification_id}, 名称: {notification_item.name}, 事件: {notification_item.event}")
            else:
                print("服务器上没有通知，或者当前用户无权查看。")
        except AcunetixError as e:
            pytest.fail(f"列出通知时发生 AcunetixError: {e}")
        except Exception as e:
            pytest.fail(f"列出通知时发生未知错误: {e}")

    def test_notification_lifecycle(self, real_sync_client: AcunetixSyncClient, managed_notification: Notification):
        """测试通知的创建 (通过 fixture)、获取和更新。"""
        created_notification_id = managed_notification.notification_id
        original_name = managed_notification.name
        original_event = managed_notification.event

        print(f"测试: 使用 fixture 创建的通知 ID: {created_notification_id}, 名称: {original_name}")

        # 1. 获取通知
        try:
            print(f"测试: 尝试获取通知 ID: {created_notification_id}")
            fetched_notification = real_sync_client.notifications.get(created_notification_id)
            assert fetched_notification is not None
            assert fetched_notification.notification_id == created_notification_id
            assert fetched_notification.name == original_name
            assert fetched_notification.event == original_event
            print(f"测试: 成功获取通知 ID: {fetched_notification.notification_id}")
        except AcunetixError as e:
            pytest.fail(f"获取通知 {created_notification_id} 时发生 AcunetixError: {e}")
        except Exception as e:
            pytest.fail(f"获取通知 {created_notification_id} 时发生未知错误: {e}")

        # 2. 更新通知
        updated_name = f"{original_name} (已更新)"
        updated_disabled_status = True
        try:
            print(f"测试: 尝试更新通知 ID: {created_notification_id}")
            current_notification = real_sync_client.notifications.get(created_notification_id)
            update_payload = NotificationUpdateRequest(
                name=updated_name,
                event=current_notification.event, 
                scope=current_notification.scope, 
                disabled=updated_disabled_status,
                email_address=current_notification.email_address,
            )
            updated_notification_response = real_sync_client.notifications.update(created_notification_id, update_payload)
            assert updated_notification_response is not None
            print(f"测试: 更新通知 ID: {created_notification_id} 的请求已发送")

            verified_updated_notification = real_sync_client.notifications.get(created_notification_id)
            assert verified_updated_notification.name == updated_name
            assert verified_updated_notification.disabled == updated_disabled_status
            print(f"测试: 成功验证通知 ID: {created_notification_id} 的更新")
        except AcunetixError as e:
            pytest.fail(f"更新通知 {created_notification_id} 时发生 AcunetixError: {e}")
        except Exception as e:
            pytest.fail(f"更新通知 {created_notification_id} 时发生未知错误: {e}")

    def test_list_report_templates(self, real_sync_client: AcunetixSyncClient):
        """测试列出报告模板。"""
        try:
            print("测试: 尝试列出报告模板")
            templates_list = real_sync_client.report_templates.list()
            assert templates_list is not None
            assert isinstance(templates_list, list)
            print(f"测试: 成功获取到 {len(templates_list)} 个报告模板。")
            if templates_list:
                for template in templates_list:
                    assert isinstance(template, ReportTemplate)
                    print(f"  - 模板 ID: {template.template_id}, 名称: {template.name}")
            else:
                print("服务器上没有报告模板。")
        except AcunetixError as e:
            pytest.fail(f"列出报告模板时发生 AcunetixError: {e}")
        except Exception as e:
            pytest.fail(f"列出报告模板时发生未知错误: {e}")

    def test_report_template_lifecycle(self, real_sync_client: AcunetixSyncClient, managed_report_template: ReportTemplate):
        """测试报告模板的创建 (通过 fixture)、获取和更新。"""
        created_template_id = managed_report_template.template_id
        original_name = managed_report_template.name
        original_description = managed_report_template.description

        print(f"测试: 使用 fixture 创建的报告模板 ID: {created_template_id}, 名称: {original_name}")

        # 1. 获取报告模板
        try:
            print(f"测试: 尝试获取报告模板 ID: {created_template_id}")
            fetched_template = real_sync_client.report_templates.get(created_template_id)
            assert fetched_template is not None
            assert fetched_template.template_id == created_template_id
            assert fetched_template.name == original_name
            if fetched_template.description is not None:
                 assert fetched_template.description == original_description
            print(f"测试: 成功获取报告模板 ID: {fetched_template.template_id}")
        except AcunetixError as e:
            pytest.fail(f"获取报告模板 {created_template_id} 时发生 AcunetixError: {e}")
        except Exception as e:
            pytest.fail(f"获取报告模板 {created_template_id} 时发生未知错误: {e}")

        # 2. 更新报告模板 (元数据)
        updated_name = f"{original_name} (已更新)"
        updated_description = f"{original_description} - (已更新描述)"
        try:
            print(f"测试: 尝试更新报告模板 ID: {created_template_id}")
            current_template = real_sync_client.report_templates.get(created_template_id)
            
            import base64 # Required for content
            minimal_xslt_content_for_update = '<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"><xsl:template match="/">UPDATED</xsl:template></xsl:stylesheet>'
            base64_content_for_update = base64.b64encode(minimal_xslt_content_for_update.encode('utf-8')).decode('utf-8')

            update_payload = ReportTemplateUpdateRequest(
                name=updated_name,
                description=updated_description,
                type=current_template.type, 
                content=base64_content_for_update 
            )
            
            updated_template_response = real_sync_client.report_templates.update(created_template_id, update_payload)
            assert updated_template_response is not None
            print(f"测试: 更新报告模板 ID: {created_template_id} 的请求已发送")

            verified_updated_template = real_sync_client.report_templates.get(created_template_id)
            assert verified_updated_template.name == updated_name
            if verified_updated_template.description is not None: 
                assert verified_updated_template.description == updated_description
            print(f"测试: 成功验证报告模板 ID: {created_template_id} 的更新")
        except AcunetixError as e:
            pytest.fail(f"更新报告模板 {created_template_id} 时发生 AcunetixError: {e}")
        except Exception as e:
            pytest.fail(f"更新报告模板 {created_template_id} 时发生未知错误: {e}")

    def test_list_users(self, real_sync_client: AcunetixSyncClient):
        """测试列出用户。"""
        try:
            print("测试: 尝试列出用户")
            users_paginated_list = real_sync_client.users.list(limit=5)
            assert users_paginated_list is not None
            assert hasattr(users_paginated_list, 'items') 
            assert isinstance(users_paginated_list.items, list)
            print(f"测试: 成功获取到 {len(users_paginated_list.items)} 个用户 (最多5个)。")
            if users_paginated_list.items:
                for user_brief in users_paginated_list.items:
                    assert isinstance(user_brief, UserBrief)
                    print(f"  - 用户 ID: {user_brief.user_id}, 邮箱: {user_brief.email}, 姓名: {user_brief.name}")
            else:
                print("服务器上没有用户，或者当前用户无权查看。")
        except AcunetixError as e:
            if "access denied" in str(e).lower() or "forbidden" in str(e).lower() or "unauthorized" in str(e).lower():
                 pytest.skip(f"跳过列出用户测试：API密钥可能无权访问 ({e})")
            pytest.fail(f"列出用户时发生 AcunetixError: {e}")
        except Exception as e:
            pytest.fail(f"列出用户时发生未知错误: {e}")

    def test_list_roles(self, real_sync_client: AcunetixSyncClient):
        """测试列出角色。"""
        try:
            print("测试: 尝试列出角色")
            roles_list = real_sync_client.roles.list()
            assert roles_list is not None
            assert isinstance(roles_list, PaginatedList) # Changed to PaginatedList
            print(f"测试: 成功获取到 {len(roles_list.items)} 个角色。") # Use roles_list.items
            if roles_list.items:
                for role in roles_list.items: # Iterate over roles_list.items
                    assert isinstance(role, RoleDetails) # Changed to RoleDetails
                    assert role.role_id is not None
                    assert role.name is not None
                    print(f"  - 角色 ID: {role.role_id}, 名称: {role.name}")
            else:
                print("服务器上没有角色。")
        except AcunetixError as e:
            if "access denied" in str(e).lower() or "forbidden" in str(e).lower() or "unauthorized" in str(e).lower():
                 pytest.skip(f"跳过列出角色测试：API密钥可能无权访问 ({e})")
            pytest.fail(f"列出角色时发生 AcunetixError: {e}")
        except Exception as e:
            pytest.fail(f"列出角色时发生未知错误: {e}")

    def test_list_excluded_hours(self, real_sync_client: AcunetixSyncClient):
        """测试列出排除的时间段。"""
        try:
            print("测试: 尝试列出排除的时间段")
            excluded_hours_list_response = real_sync_client.excluded_hours.list() # Renamed variable
            assert excluded_hours_list_response is not None
            assert isinstance(excluded_hours_list_response, ExcludedHoursProfilesList) # Changed to ExcludedHoursProfilesList
            print(f"测试: 成功获取到 {len(excluded_hours_list_response.values) if excluded_hours_list_response.values else 0} 个排除的时间段配置。") # Use .values
            if excluded_hours_list_response.values: # Iterate over .values
                for eh in excluded_hours_list_response.values:
                    assert isinstance(eh, ExcludedHoursProfile)
                    print(f"  - 排除时间 ID: {eh.excluded_hours_id}, 名称: {eh.name}")
            else:
                print("服务器上没有配置排除的时间段。")
        except AcunetixError as e:
            pytest.fail(f"列出排除的时间段时发生 AcunetixError: {e}")
        except Exception as e:
            pytest.fail(f"列出排除的时间段时发生未知错误: {e}")

    def test_list_issue_trackers(self, real_sync_client: AcunetixSyncClient):
        """测试列出问题跟踪器。"""
        try:
            print("测试: 尝试列出问题跟踪器")
            issue_trackers_list_response = real_sync_client.issue_trackers.list() # Renamed variable
            assert issue_trackers_list_response is not None
            assert isinstance(issue_trackers_list_response, IssueTrackerList) # Changed to IssueTrackerList
            print(f"测试: 成功获取到 {len(issue_trackers_list_response.issue_trackers) if issue_trackers_list_response.issue_trackers else 0} 个问题跟踪器配置。") # Use .issue_trackers
            if issue_trackers_list_response.issue_trackers: # Iterate over .issue_trackers
                for it in issue_trackers_list_response.issue_trackers:
                    assert isinstance(it, IssueTracker) # This will now correctly refer to IssueTrackerEntry
                    print(f"  - 问题跟踪器 ID: {it.issue_tracker_id}, 名称: {it.name}, 类型: {it.platform}")
            else:
                print("服务器上没有配置问题跟踪器。")
        except AcunetixError as e:
            pytest.fail(f"列出问题跟踪器时发生 AcunetixError: {e}")
        except Exception as e:
            pytest.fail(f"列出问题跟踪器时发生未知错误: {e}")

    def test_list_wafs(self, real_sync_client: AcunetixSyncClient):
        """测试列出 WAFs。"""
        try:
            print("测试: 尝试列出 WAFs")
            wafs_list_response = real_sync_client.wafs.list() # Renamed variable
            assert wafs_list_response is not None
            assert isinstance(wafs_list_response, WAFsList) # Changed to WAFsList
            print(f"测试: 成功获取到 {len(wafs_list_response.wafs) if wafs_list_response.wafs else 0} 个 WAF 配置。") # Use .wafs
            if wafs_list_response.wafs: # Iterate over .wafs
                for waf_item in wafs_list_response.wafs:
                    assert isinstance(waf_item, WAF) # This will now correctly refer to WAFEntry
                    print(f"  - WAF ID: {waf_item.waf_id}, 名称: {waf_item.name}, 类型: {waf_item.platform}")
            else:
                print("服务器上没有配置 WAFs。")
        except AcunetixError as e:
            pytest.fail(f"列出 WAFs 时发生 AcunetixError: {e}")
        except Exception as e:
            pytest.fail(f"列出 WAFs 时发生未知错误: {e}")

    def test_list_workers(self, real_sync_client: AcunetixSyncClient):
        """测试列出工作程序 (扫描代理)。"""
        try:
            print("测试: 尝试列出工作程序")
            workers_list_response = real_sync_client.workers.list() # Renamed variable
            assert workers_list_response is not None
            assert isinstance(workers_list_response, WorkerList) # Changed to WorkerList
            print(f"测试: 成功获取到 {len(workers_list_response.workers) if workers_list_response.workers else 0} 个工作程序。") # Use .workers
            if workers_list_response.workers: # Iterate over .workers
                for worker in workers_list_response.workers:
                    assert isinstance(worker, Worker)
                    # Assuming Worker model has 'worker_id' and 'endpoint' (now str) and 'status'
                    print(f"  - 工作程序 ID: {worker.worker_id}, 端点: {worker.endpoint}, 状态: {worker.status}")
            else:
                print("服务器上没有工作程序 (扫描代理)。")
        except AcunetixError as e:
            pytest.fail(f"列出工作程序时发生 AcunetixError: {e}")
        except Exception as e:
            pytest.fail(f"列出工作程序时发生未知错误: {e}")

    def test_get_agents_config(self, real_sync_client: AcunetixSyncClient):
        """测试获取代理配置。"""
        try:
            print("测试: 尝试获取代理配置")
            agents_config = real_sync_client.agents_config.get()
            assert agents_config is not None
            assert isinstance(agents_config, AgentsConfig)
            print(f"测试: 成功获取代理配置。自动更新: {agents_config.auto_update}, 类型: {agents_config.type}")
        except AcunetixError as e:
            if "not found" in str(e).lower() or ("status_code" in dir(e) and e.status_code == 404):
                 pytest.skip(f"跳过获取代理配置测试：功能可能不可用或未配置 ({e})")
            pytest.fail(f"获取代理配置时发生 AcunetixError: {e}")
        except Exception as e:
            pytest.fail(f"获取代理配置时发生未知错误: {e}")

    def test_list_exports(self, real_sync_client: AcunetixSyncClient):
        """测试列出导出记录。"""
        try:
            print("测试: 尝试列出导出记录")
            exports_paginated_list = real_sync_client.exports.list(limit=5)
            assert exports_paginated_list is not None
            assert hasattr(exports_paginated_list, 'items')
            assert isinstance(exports_paginated_list.items, list)
            print(f"测试: 成功获取到 {len(exports_paginated_list.items)} 条导出记录 (最多5条)。")
            if exports_paginated_list.items:
                for export_item in exports_paginated_list.items:
                    assert isinstance(export_item, Export)
                    print(f"  - 导出 ID: {export_item.export_id}, 状态: {export_item.status}, 下载: {export_item.download_link}")
            else:
                print("服务器上没有导出记录，或者当前用户无权查看。")
        except AcunetixError as e:
            pytest.fail(f"列出导出记录时发生 AcunetixError: {e}")
        except Exception as e:
            pytest.fail(f"列出导出记录时发生未知错误: {e}")

    def test_list_reports(self, real_sync_client: AcunetixSyncClient):
        """测试列出报告。"""
        try:
            print("测试: 尝试列出报告")
            reports_paginated_list = real_sync_client.reports.list(limit=5)
            assert reports_paginated_list is not None
            assert hasattr(reports_paginated_list, 'items')
            assert isinstance(reports_paginated_list.items, list)
            print(f"测试: 成功获取到 {len(reports_paginated_list.items)} 条报告记录 (最多5条)。")
            if reports_paginated_list.items:
                for report_item in reports_paginated_list.items:
                    assert isinstance(report_item, Report)
                    print(f"  - 报告 ID: {report_item.report_id}, 模板: {report_item.template_name}, 状态: {report_item.status}")
            else:
                print("服务器上没有报告记录，或者当前用户无权查看。")
        except AcunetixError as e:
            pytest.fail(f"列出报告时发生 AcunetixError: {e}")
        except Exception as e:
            pytest.fail(f"列出报告时发生未知错误: {e}")

    def test_list_user_groups(self, real_sync_client: AcunetixSyncClient):
        """测试列出用户组。"""
        try:
            print("测试: 尝试列出用户组")
            user_groups_list = real_sync_client.user_groups.list()
            assert user_groups_list is not None
            assert isinstance(user_groups_list, list)
            print(f"测试: 成功获取到 {len(user_groups_list)} 个用户组。")
            if user_groups_list:
                for group in user_groups_list:
                    assert isinstance(group, dict)
                    assert "group_id" in group
                    assert "name" in group
                    print(f"  - 用户组 ID: {group.get('group_id')}, 名称: {group.get('name')}")
            else:
                print("服务器上没有用户组，或者当前用户无权查看。")
        except AcunetixError as e:
            if "access denied" in str(e).lower() or "forbidden" in str(e).lower() or "unauthorized" in str(e).lower():
                 pytest.skip(f"跳过列出用户组测试：API密钥可能无权访问 ({e})")
            pytest.fail(f"列出用户组时发生 AcunetixError: {e}")
        except Exception as e:
            pytest.fail(f"列出用户组时发生未知错误: {e}")
