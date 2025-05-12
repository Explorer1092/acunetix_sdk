# -*- coding: utf-8 -*-

"""
CLI 命令 - Targets 模块
"""

import logging
import argparse # 用于类型提示
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from acunetix_sdk.client_sync import AcunetixSyncClient
    from acunetix_sdk.models.target import TargetCreateRequest
    from acunetix_sdk.errors import AcunetixError

def list_targets(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """列出所有目标"""
    # 导入移到函数内部，以避免在模块加载时因 sys.path 问题而失败
    # 主 CLI 文件应确保 acunetix_sdk 在 sys.path 中
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info("正在获取目标列表...")
    try:
        targets = client.targets.list(limit=args.limit or 100) # 默认列出100个
        if targets.pagination.count == 0:
            cli_logger.info("未找到任何目标。")
            return
        
        cli_logger.info(f"找到 {targets.pagination.count} 个目标:")
        for target in targets.items:
            cli_logger.info(f"  ID: {target.target_id}, 地址: {target.address}, 描述: {target.description or 'N/A'}")
    except AcunetixError as e:
        cli_logger.error(f"获取目标列表失败: {e}")

def add_target(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """添加新目标"""
    from acunetix_sdk.models.target import TargetCreateRequest
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info(f"正在添加目标: 地址='{args.address}', 描述='{args.description}'")
    try:
        target_data = TargetCreateRequest(
            address=args.address,
            description=args.description,
            type="default",  # 或者其他类型，根据需要
            criticality=args.criticality or 10 # 默认重要性
        )
        new_target = client.targets.create(target_data)
        cli_logger.info(f"目标添加成功: ID='{new_target.target_id}', 地址='{new_target.address}'")
    except AcunetixError as e:
        cli_logger.error(f"添加目标失败: {e}")

def delete_target(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """删除目标"""
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info(f"正在删除目标 ID: {args.target_id}")
    try:
        client.targets.delete(args.target_id)
        cli_logger.info(f"目标 ID '{args.target_id}' 删除成功。")
    except AcunetixError as e:
        cli_logger.error(f"删除目标 ID '{args.target_id}' 失败: {e}")

def register_targets_parser(subparsers: argparse._SubParsersAction, parent_parser: argparse.ArgumentParser):
    """注册 targets 命令的解析器"""
    targets_parser = subparsers.add_parser("targets", help="管理目标", parents=[parent_parser])
    targets_subparsers = targets_parser.add_subparsers(title="操作", dest="action", required=True)

    # targets list
    list_targets_parser = targets_subparsers.add_parser("list", help="列出所有目标", parents=[parent_parser])
    list_targets_parser.add_argument("--limit", type=int, help="限制返回的目标数量")
    list_targets_parser.set_defaults(func=list_targets)

    # targets add
    add_target_parser = targets_subparsers.add_parser("add", help="添加新目标", parents=[parent_parser])
    add_target_parser.add_argument("address", help="目标地址 (例如 http://example.com)")
    add_target_parser.add_argument("description", help="目标描述")
    add_target_parser.add_argument("--criticality", type=int, choices=range(0, 101, 10), help="目标重要性 (0-100, 10的倍数)")
    add_target_parser.set_defaults(func=add_target)

    # targets delete
    delete_target_parser = targets_subparsers.add_parser("delete", help="删除目标", parents=[parent_parser])
    delete_target_parser.add_argument("target_id", help="要删除的目标ID")
    delete_target_parser.set_defaults(func=delete_target)
