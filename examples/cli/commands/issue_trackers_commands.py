# -*- coding: utf-8 -*-

"""
CLI 命令 - Issue Trackers 模块
"""

import logging
import argparse # 用于类型提示
from typing import TYPE_CHECKING

# 辅助函数从 cli_utils 导入
from ..cli_utils import parse_issue_tracker_config_from_json_file

if TYPE_CHECKING:
    from acunetix_sdk.client_sync import AcunetixSyncClient
    from acunetix_sdk.models.issue_tracker import IssueTrackerEntry
    from acunetix_sdk.errors import AcunetixError

def list_issue_trackers(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """列出所有问题跟踪器配置"""
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info("正在获取问题跟踪器配置列表...")
    try:
        response = client.issue_trackers.list() 
        if not response.issue_trackers:
            cli_logger.info("未找到任何问题跟踪器配置。")
            return
        
        cli_logger.info(f"找到 {len(response.issue_trackers)} 个问题跟踪器配置:")
        for tracker in response.issue_trackers:
            cli_logger.info(f"  ID: {tracker.issue_tracker_id}, 名称: {tracker.name}")
            cli_logger.info(f"    平台: {tracker.platform.value}, URL: {tracker.url}")
            cli_logger.info(f"    认证类型: {tracker.auth.kind.value if tracker.auth else 'N/A'}")
            if tracker.project:
                cli_logger.info(f"    项目: {tracker.project.project_name or tracker.project.project_id or 'N/A'}")
            if tracker.issue_type:
                cli_logger.info(f"    问题类型: {tracker.issue_type.issue_name or tracker.issue_type.issue_id or 'N/A'}")
            cli_logger.info("-" * 10)
    except AcunetixError as e:
        cli_logger.error(f"获取问题跟踪器列表失败: {e}")

def get_issue_tracker(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """获取特定问题跟踪器配置的详情"""
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info(f"正在获取问题跟踪器配置 ID '{args.tracker_id}' 的详情...")
    try:
        tracker = client.issue_trackers.get(args.tracker_id)
        cli_logger.info(f"问题跟踪器详情 - ID: {tracker.issue_tracker_id}")
        cli_logger.info(f"  名称: {tracker.name}")
        cli_logger.info(f"  平台: {tracker.platform.value}")
        cli_logger.info(f"  URL: {tracker.url}")
        if tracker.auth:
            cli_logger.info(f"  认证类型: {tracker.auth.kind.value}")
            cli_logger.info(f"    用户: {tracker.auth.user or 'N/A'}")
        if tracker.project:
            cli_logger.info(f"  项目: ID='{tracker.project.project_id or 'N/A'}', 名称='{tracker.project.project_name or 'N/A'}'")
        if tracker.issue_type:
            cli_logger.info(f"  问题类型: ID='{tracker.issue_type.issue_id or 'N/A'}', 名称='{tracker.issue_type.issue_name or 'N/A'}'")
        if tracker.proxy:
            cli_logger.info(f"  代理类型: {tracker.proxy.proxy_type.value if tracker.proxy.proxy_type else 'N/A'}")
    except AcunetixError as e:
        cli_logger.error(f"获取问题跟踪器配置 ID '{args.tracker_id}' 详情失败: {e}")

def create_issue_tracker(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """创建新的问题跟踪器配置"""
    from acunetix_sdk.models.issue_tracker import IssueTrackerEntry
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info(f"正在创建问题跟踪器配置: 名称='{args.name}'")

    if not args.config_file:
        cli_logger.error("创建问题跟踪器失败: 必须通过 --config_file 提供包含配置的JSON文件路径。")
        return
        
    config_data = parse_issue_tracker_config_from_json_file(args.config_file)
    if not config_data:
        return

    tracker_entry_data = IssueTrackerEntry(name=args.name, **config_data.model_dump())

    try:
        new_tracker = client.issue_trackers.create(tracker_entry_data)
        cli_logger.info(f"问题跟踪器配置创建成功: ID='{new_tracker.issue_tracker_id}', 名称='{new_tracker.name}'")
    except AcunetixError as e:
        cli_logger.error(f"创建问题跟踪器配置失败: {e}")
    except Exception as e:
        cli_logger.error(f"创建问题跟踪器配置时发生意外错误: {e}")

def update_issue_tracker(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """更新问题跟踪器配置"""
    from acunetix_sdk.models.issue_tracker import IssueTrackerEntry
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info(f"正在更新问题跟踪器配置 ID '{args.tracker_id}'...")

    if not args.name and not args.config_file:
        cli_logger.error("更新问题跟踪器失败: 必须提供 --name 或 --config_file。")
        return

    try:
        current_tracker_dict = client.issue_trackers.get(args.tracker_id).model_dump()
    except AcunetixError as e:
        cli_logger.error(f"无法获取当前跟踪器配置以进行更新: {e}")
        return

    if args.name:
        current_tracker_dict['name'] = args.name
    
    if args.config_file:
        config_data_update = parse_issue_tracker_config_from_json_file(args.config_file)
        if not config_data_update:
            return
        config_update_dict = config_data_update.model_dump(exclude_unset=True)
        for key, value in config_update_dict.items():
            if key not in ['name', 'issue_tracker_id']:
                 current_tracker_dict[key] = value

    update_payload = IssueTrackerEntry(**current_tracker_dict)
    
    try:
        updated_tracker = client.issue_trackers.update(args.tracker_id, update_payload)
        cli_logger.info(f"问题跟踪器配置更新成功: ID='{updated_tracker.issue_tracker_id}', 名称='{updated_tracker.name}'")
    except AcunetixError as e:
        cli_logger.error(f"更新问题跟踪器配置 ID '{args.tracker_id}' 失败: {e}")
    except Exception as e:
        cli_logger.error(f"更新问题跟踪器配置时发生意外错误: {e}")

def delete_issue_tracker(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """删除问题跟踪器配置"""
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info(f"正在删除问题跟踪器配置 ID: {args.tracker_id}")
    try:
        client.issue_trackers.delete(args.tracker_id)
        cli_logger.info(f"问题跟踪器配置 ID '{args.tracker_id}' 删除成功。")
    except AcunetixError as e:
        cli_logger.error(f"删除问题跟踪器配置 ID '{args.tracker_id}' 失败: {e}")

def test_issue_tracker(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """测试问题跟踪器连接"""
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info(f"正在测试问题跟踪器配置 ID '{args.tracker_id}' 的连接...")
    try:
        status = client.issue_trackers.test_connection(args.tracker_id)
        if status.success:
            cli_logger.info(f"连接测试成功: {status.message or '无附加消息'}")
        else:
            cli_logger.error(f"连接测试失败: {status.message or '未知错误'}")
    except AcunetixError as e:
        cli_logger.error(f"测试问题跟踪器连接失败: {e}")
    except AttributeError:
        cli_logger.error("测试连接失败: SDK 中可能尚未实现 'client.issue_trackers.test_connection()' 方法。")

def register_issue_trackers_parser(subparsers: argparse._SubParsersAction, parent_parser: argparse.ArgumentParser):
    """注册 issue_trackers 命令的解析器"""
    issue_trackers_parser = subparsers.add_parser("issue_trackers", help="管理问题跟踪器配置", parents=[parent_parser])
    issue_trackers_subparsers = issue_trackers_parser.add_subparsers(title="操作", dest="action", required=True)

    list_issue_trackers_parser = issue_trackers_subparsers.add_parser("list", help="列出所有问题跟踪器配置", parents=[parent_parser])
    list_issue_trackers_parser.set_defaults(func=list_issue_trackers)

    get_issue_tracker_parser = issue_trackers_subparsers.add_parser("get", help="获取特定问题跟踪器配置的详情", parents=[parent_parser])
    get_issue_tracker_parser.add_argument("tracker_id", help="要获取详情的问题跟踪器ID")
    get_issue_tracker_parser.set_defaults(func=get_issue_tracker)

    create_issue_tracker_parser = issue_trackers_subparsers.add_parser("create", help="创建新的问题跟踪器配置", parents=[parent_parser])
    create_issue_tracker_parser.add_argument("name", help="问题跟踪器配置的名称")
    create_issue_tracker_parser.add_argument("--config_file", required=True, help="包含 IssueTrackerConfig 数据的JSON文件路径")
    create_issue_tracker_parser.set_defaults(func=create_issue_tracker)

    update_issue_tracker_parser = issue_trackers_subparsers.add_parser("update", help="更新问题跟踪器配置", parents=[parent_parser])
    update_issue_tracker_parser.add_argument("tracker_id", help="要更新的问题跟踪器ID")
    update_issue_tracker_parser.add_argument("--name", help="新的问题跟踪器配置名称")
    update_issue_tracker_parser.add_argument("--config_file", help="包含 IssueTrackerConfig 更新数据的JSON文件路径")
    update_issue_tracker_parser.set_defaults(func=update_issue_tracker)

    delete_issue_tracker_parser = issue_trackers_subparsers.add_parser("delete", help="删除问题跟踪器配置", parents=[parent_parser])
    delete_issue_tracker_parser.add_argument("tracker_id", help="要删除的问题跟踪器ID")
    delete_issue_tracker_parser.set_defaults(func=delete_issue_tracker)

    test_issue_tracker_parser = issue_trackers_subparsers.add_parser("test", help="测试问题跟踪器连接", parents=[parent_parser])
    test_issue_tracker_parser.add_argument("tracker_id", help="要测试连接的问题跟踪器ID")
    test_issue_tracker_parser.set_defaults(func=test_issue_tracker)
