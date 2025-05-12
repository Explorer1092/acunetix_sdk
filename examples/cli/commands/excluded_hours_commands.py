# -*- coding: utf-8 -*-

"""
CLI 命令 - Excluded Hours 模块
"""

import logging
import argparse # 用于类型提示
from typing import TYPE_CHECKING

# 辅助函数从 cli_utils 导入
from ..cli_utils import parse_exclusion_matrix

if TYPE_CHECKING:
    from acunetix_sdk.client_sync import AcunetixSyncClient
    from acunetix_sdk.models.excluded_hours import ExcludedHoursProfile
    from acunetix_sdk.errors import AcunetixError

def list_excluded_hours(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """列出所有排除时段配置"""
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info("正在获取排除时段配置列表...")
    try:
        response = client.excluded_hours.list()
        if not response.values:
            cli_logger.info("未找到任何排除时段配置。")
            return
        
        cli_logger.info(f"找到 {len(response.values)} 个排除时段配置:")
        for profile in response.values:
            cli_logger.info(f"  ID: {profile.excluded_hours_id}, 名称: {profile.name}")
            cli_logger.info(f"    时间偏移: {profile.time_offset} 分钟")
            cli_logger.info(f"    排除矩阵: (共168个条目, true表示排除)")
            cli_logger.info("-" * 10)
    except AcunetixError as e:
        cli_logger.error(f"获取排除时段列表失败: {e}")

def get_excluded_hours(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """获取特定排除时段配置的详情"""
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info(f"正在获取排除时段配置 ID '{args.profile_id}' 的详情...")
    try:
        profile = client.excluded_hours.get(args.profile_id)
        cli_logger.info(f"排除时段详情 - ID: {profile.excluded_hours_id}")
        cli_logger.info(f"  名称: {profile.name}")
        cli_logger.info(f"  时间偏移: {profile.time_offset} 分钟")
        cli_logger.info(f"  排除矩阵 (前24项示例): {profile.exclusion_matrix[:24]}")
    except AcunetixError as e:
        cli_logger.error(f"获取排除时段配置 ID '{args.profile_id}' 详情失败: {e}")

def create_excluded_hours(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """创建新的排除时段配置"""
    from acunetix_sdk.models.excluded_hours import ExcludedHoursProfile
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info(f"正在创建排除时段配置: 名称='{args.name}'")

    matrix = parse_exclusion_matrix(args.exclusion_matrix_json)
    if matrix is None:
        return

    profile_data = ExcludedHoursProfile(
        name=args.name,
        time_offset=args.time_offset,
        exclusion_matrix=matrix
    )
    
    try:
        new_profile = client.excluded_hours.create(profile_data)
        cli_logger.info(f"排除时段配置创建成功: ID='{new_profile.excluded_hours_id}', 名称='{new_profile.name}'")
    except AcunetixError as e:
        cli_logger.error(f"创建排除时段配置失败: {e}")
    except Exception as e:
        cli_logger.error(f"创建排除时段配置时发生意外错误: {e}")

def update_excluded_hours(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """更新排除时段配置"""
    from acunetix_sdk.models.excluded_hours import ExcludedHoursProfile
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info(f"正在更新排除时段配置 ID '{args.profile_id}'...")

    if not any([args.name, args.time_offset is not None, args.exclusion_matrix_json]):
        cli_logger.error("错误: 至少需要提供一个更新参数 (--name, --time_offset, --exclusion_matrix_json)。")
        return

    try:
        current_profile = client.excluded_hours.get(args.profile_id)
    except AcunetixError as e:
        cli_logger.error(f"无法获取当前排除时段配置以进行更新: {e}")
        return

    update_data = current_profile.model_dump(exclude={'excluded_hours_id'})

    if args.name:
        update_data['name'] = args.name
    if args.time_offset is not None:
        update_data['time_offset'] = args.time_offset
    if args.exclusion_matrix_json:
        matrix = parse_exclusion_matrix(args.exclusion_matrix_json)
        if matrix is None:
            return
        update_data['exclusion_matrix'] = matrix
    
    update_payload = ExcludedHoursProfile(**update_data)
    
    try:
        updated_profile = client.excluded_hours.update(args.profile_id, update_payload)
        cli_logger.info(f"排除时段配置更新成功: ID='{updated_profile.excluded_hours_id}', 名称='{updated_profile.name}'")
    except AcunetixError as e:
        cli_logger.error(f"更新排除时段配置 ID '{args.profile_id}' 失败: {e}")
    except Exception as e:
        cli_logger.error(f"更新排除时段配置时发生意外错误: {e}")

def delete_excluded_hours(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """删除排除时段配置"""
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info(f"正在删除排除时段配置 ID: {args.profile_id}")
    try:
        client.excluded_hours.delete(args.profile_id)
        cli_logger.info(f"排除时段配置 ID '{args.profile_id}' 删除成功。")
    except AcunetixError as e:
        cli_logger.error(f"删除排除时段配置 ID '{args.profile_id}' 失败: {e}")

def register_excluded_hours_parser(subparsers: argparse._SubParsersAction, parent_parser: argparse.ArgumentParser):
    """注册 excluded_hours 命令的解析器"""
    excluded_hours_parser = subparsers.add_parser("excluded_hours", help="管理排除时段配置", parents=[parent_parser])
    excluded_hours_subparsers = excluded_hours_parser.add_subparsers(title="操作", dest="action", required=True)

    list_excluded_hours_parser = excluded_hours_subparsers.add_parser("list", help="列出所有排除时段配置", parents=[parent_parser])
    list_excluded_hours_parser.set_defaults(func=list_excluded_hours)

    get_excluded_hours_parser = excluded_hours_subparsers.add_parser("get", help="获取特定排除时段配置的详情", parents=[parent_parser])
    get_excluded_hours_parser.add_argument("profile_id", help="要获取详情的排除时段配置ID")
    get_excluded_hours_parser.set_defaults(func=get_excluded_hours)

    create_excluded_hours_parser = excluded_hours_subparsers.add_parser("create", help="创建新的排除时段配置", parents=[parent_parser])
    create_excluded_hours_parser.add_argument("name", help="排除时段配置的名称")
    create_excluded_hours_parser.add_argument("exclusion_matrix_json", help="包含168个布尔值的JSON数组字符串")
    create_excluded_hours_parser.add_argument("--time_offset", type=int, default=0, help="时间偏移量 (分钟, 默认 0)")
    create_excluded_hours_parser.set_defaults(func=create_excluded_hours)

    update_excluded_hours_parser = excluded_hours_subparsers.add_parser("update", help="更新排除时段配置", parents=[parent_parser])
    update_excluded_hours_parser.add_argument("profile_id", help="要更新的排除时段配置ID")
    update_excluded_hours_parser.add_argument("--name", help="新的排除时段配置名称")
    update_excluded_hours_parser.add_argument("--exclusion_matrix_json", help="新的排除矩阵JSON字符串")
    update_excluded_hours_parser.add_argument("--time_offset", type=int, help="新的时间偏移量 (分钟)")
    update_excluded_hours_parser.set_defaults(func=update_excluded_hours)

    delete_excluded_hours_parser = excluded_hours_subparsers.add_parser("delete", help="删除排除时段配置", parents=[parent_parser])
    delete_excluded_hours_parser.add_argument("profile_id", help="要删除的排除时段配置ID")
    delete_excluded_hours_parser.set_defaults(func=delete_excluded_hours)
