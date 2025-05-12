# -*- coding: utf-8 -*-

"""
CLI 命令 - Scan Profiles 模块
"""

import logging
import argparse # 用于类型提示
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from acunetix_sdk.client_sync import AcunetixSyncClient
    from acunetix_sdk.errors import AcunetixError

def list_scan_profiles(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """列出所有扫描配置"""
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info("正在获取扫描配置列表...")
    try:
        profiles_list = client.scan_profiles.list() # 移除 limit 参数
        if not profiles_list: # 直接检查列表是否为空
            cli_logger.info("未找到任何扫描配置。")
            return
        
        cli_logger.info(f"找到 {len(profiles_list)} 个扫描配置:")
        for profile in profiles_list: # 直接遍历列表
            # 移除 profile.type 因为 ScanningProfile 模型中没有此字段
            cli_logger.info(f"  ID: {profile.profile_id}, 名称: {profile.name}")
    except AcunetixError as e:
        cli_logger.error(f"获取扫描配置列表失败: {e}")

def get_scan_profile(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """获取特定扫描配置的详情"""
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info(f"正在获取扫描配置 ID '{args.profile_id}' 的详情...")
    try:
        profile = client.scan_profiles.get(args.profile_id)
        cli_logger.info(f"扫描配置详情 - ID: {profile.profile_id}")
        cli_logger.info(f"  名称: {profile.name}")
        cli_logger.info(f"  描述: {profile.description or 'N/A'}")
        # 移除 profile.type 和 profile.default 因为 ScanningProfile 模型中没有这些字段
        # cli_logger.info(f"  类型: {profile.type.value if profile.type else 'N/A'}")
        # cli_logger.info(f"  默认: {'是' if profile.default else '否'}")
        cli_logger.info(f"  自定义: {'是' if profile.custom else '否'}") # custom 字段存在
        cli_logger.info(f"  排序: {profile.sort_order}") # sort_order 字段存在
    except AcunetixError as e:
        cli_logger.error(f"获取扫描配置 ID '{args.profile_id}' 详情失败: {e}")

def register_scan_profiles_parser(subparsers: argparse._SubParsersAction, parent_parser: argparse.ArgumentParser):
    """注册 scan_profiles 命令的解析器"""
    scan_profiles_parser = subparsers.add_parser("scan_profiles", help="管理扫描配置", parents=[parent_parser])
    scan_profiles_subparsers = scan_profiles_parser.add_subparsers(title="操作", dest="action", required=True)

    list_scan_profiles_parser = scan_profiles_subparsers.add_parser("list", help="列出所有扫描配置", parents=[parent_parser])
    # list_scan_profiles_parser.add_argument("--limit", type=int, help="限制返回的扫描配置数量") # 移除 limit 参数定义
    list_scan_profiles_parser.set_defaults(func=list_scan_profiles)

    get_scan_profile_parser = scan_profiles_subparsers.add_parser("get", help="获取特定扫描配置的详情", parents=[parent_parser])
    get_scan_profile_parser.add_argument("profile_id", help="要获取详情的扫描配置ID")
    get_scan_profile_parser.set_defaults(func=get_scan_profile)
