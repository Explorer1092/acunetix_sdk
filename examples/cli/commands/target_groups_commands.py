# -*- coding: utf-8 -*-

"""
CLI 命令 - Target Groups 模块
"""

import logging
import argparse # 用于类型提示
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from acunetix_sdk.client_sync import AcunetixSyncClient
    from acunetix_sdk.models.target_group import TargetGroupCreateRequest, TargetGroupUpdateRequest
    from acunetix_sdk.errors import AcunetixError

def list_target_groups(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """列出所有目标组"""
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info("正在获取目标组列表...")
    try:
        response = client.target_groups.list(limit=args.limit or 100)
        if not response.groups:
            cli_logger.info("未找到任何目标组。")
            return
        
        cli_logger.info(f"找到 {len(response.groups)} 个目标组:")
        for group in response.groups:
            cli_logger.info(f"  ID: {group.group_id}, 名称: {group.name}, 描述: {group.description or 'N/A'}, 目标数量: {group.target_count or 0}")
    except AcunetixError as e:
        cli_logger.error(f"获取目标组列表失败: {e}")

def create_target_group(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """创建新目标组"""
    from acunetix_sdk.models.target_group import TargetGroupCreateRequest
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info(f"正在创建目标组: 名称='{args.name}', 描述='{args.description}'")
    try:
        group_data = TargetGroupCreateRequest(
            name=args.name,
            description=args.description
        )
        new_group = client.target_groups.create(group_data)
        cli_logger.info(f"目标组创建成功: ID='{new_group.group_id}', 名称='{new_group.name}'")
    except AcunetixError as e:
        cli_logger.error(f"创建目标组失败: {e}")

def get_target_group(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """获取特定目标组的详情"""
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info(f"正在获取目标组 ID '{args.group_id}' 的详情...")
    try:
        group = client.target_groups.get(args.group_id)
        cli_logger.info(f"目标组详情 - ID: {group.group_id}")
        cli_logger.info(f"  名称: {group.name}")
        cli_logger.info(f"  描述: {group.description or 'N/A'}")
        cli_logger.info(f"  目标数量: {group.target_count or 0}")
        if group.vuln_count:
            cli_logger.info(f"  漏洞统计:")
            cli_logger.info(f"    高危: {group.vuln_count.high}")
            cli_logger.info(f"    中危: {group.vuln_count.medium}")
            cli_logger.info(f"    低危: {group.vuln_count.low}")
            cli_logger.info(f"    信息: {group.vuln_count.info}")
    except AcunetixError as e:
        cli_logger.error(f"获取目标组 ID '{args.group_id}' 详情失败: {e}")

def update_target_group(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """更新目标组"""
    from acunetix_sdk.models.target_group import TargetGroupUpdateRequest
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    if not args.name and not args.description:
        cli_logger.error("错误: 至少需要提供 --name 或 --description 中的一个参数进行更新。")
        return

    cli_logger.info(f"正在更新目标组 ID '{args.group_id}'...")
    update_data = TargetGroupUpdateRequest()
    if args.name:
        update_data.name = args.name
    if args.description:
        update_data.description = args.description
    
    try:
        client.target_groups.update(args.group_id, update_data) # This returns None
        cli_logger.info(f"目标组 ID '{args.group_id}' 更新请求已发送。正在获取更新后的信息...")
        # Fetch the updated group to display its details
        refetched_group = client.target_groups.get(args.group_id)
        cli_logger.info(f"目标组更新成功: ID='{refetched_group.group_id}', 名称='{refetched_group.name}', 描述='{refetched_group.description or 'N/A'}'")
    except AcunetixError as e:
        cli_logger.error(f"更新目标组 ID '{args.group_id}' 失败: {e}")

def delete_target_group(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """删除目标组"""
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info(f"正在删除目标组 ID: {args.group_id}")
    try:
        client.target_groups.delete(args.group_id)
        cli_logger.info(f"目标组 ID '{args.group_id}' 删除成功。")
    except AcunetixError as e:
        cli_logger.error(f"删除目标组 ID '{args.group_id}' 失败: {e}")

def register_target_groups_parser(subparsers: argparse._SubParsersAction, parent_parser: argparse.ArgumentParser):
    """注册 target_groups 命令的解析器"""
    target_groups_parser = subparsers.add_parser("target_groups", help="管理目标组", parents=[parent_parser])
    target_groups_subparsers = target_groups_parser.add_subparsers(title="操作", dest="action", required=True)

    list_target_groups_parser = target_groups_subparsers.add_parser("list", help="列出所有目标组", parents=[parent_parser])
    list_target_groups_parser.add_argument("--limit", type=int, help="限制返回的目标组数量")
    list_target_groups_parser.set_defaults(func=list_target_groups)

    create_target_group_parser = target_groups_subparsers.add_parser("create", help="创建新目标组", parents=[parent_parser])
    create_target_group_parser.add_argument("name", help="目标组名称")
    create_target_group_parser.add_argument("--description", help="目标组描述", default=None)
    create_target_group_parser.set_defaults(func=create_target_group)

    get_target_group_parser = target_groups_subparsers.add_parser("get", help="获取特定目标组的详情", parents=[parent_parser])
    get_target_group_parser.add_argument("group_id", help="要获取详情的目标组ID")
    get_target_group_parser.set_defaults(func=get_target_group)

    update_target_group_parser = target_groups_subparsers.add_parser("update", help="更新目标组", parents=[parent_parser])
    update_target_group_parser.add_argument("group_id", help="要更新的目标组ID")
    update_target_group_parser.add_argument("--name", help="新的目标组名称")
    update_target_group_parser.add_argument("--description", help="新的目标组描述")
    update_target_group_parser.set_defaults(func=update_target_group)

    delete_target_group_parser = target_groups_subparsers.add_parser("delete", help="删除目标组", parents=[parent_parser])
    delete_target_group_parser.add_argument("group_id", help="要删除的目标组ID")
    delete_target_group_parser.set_defaults(func=delete_target_group)
