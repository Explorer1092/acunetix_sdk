# -*- coding: utf-8 -*-

"""
CLI 命令 - WAFs 模块
"""

import logging
import argparse # 用于类型提示
from typing import TYPE_CHECKING

# 辅助函数从 cli_utils 导入
from ..cli_utils import parse_waf_config_from_json_file

if TYPE_CHECKING:
    from acunetix_sdk.client_sync import AcunetixSyncClient
    from acunetix_sdk.models.waf import WAFEntry
    from acunetix_sdk.errors import AcunetixError

def list_wafs(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """列出所有WAF配置"""
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info("正在获取WAF配置列表...")
    try:
        response = client.wafs.list()
        if not response.wafs:
            cli_logger.info("未找到任何WAF配置。")
            return
        
        cli_logger.info(f"找到 {len(response.wafs)} 个WAF配置:")
        for waf in response.wafs:
            cli_logger.info(f"  ID: {waf.waf_id}, 名称: {waf.name}")
            cli_logger.info(f"    平台: {waf.platform.value}, ACL名称: {waf.acl_name}")
            cli_logger.info(f"    范围: {waf.scope.value}" + (f", 区域: {waf.region.value}" if waf.region else ""))
            cli_logger.info("-" * 10)
    except AcunetixError as e:
        cli_logger.error(f"获取WAF列表失败: {e}")

def get_waf(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """获取特定WAF配置的详情"""
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info(f"正在获取WAF配置 ID '{args.waf_id}' 的详情...")
    try:
        waf = client.wafs.get(args.waf_id)
        cli_logger.info(f"WAF详情 - ID: {waf.waf_id}")
        cli_logger.info(f"  名称: {waf.name}")
        cli_logger.info(f"  平台: {waf.platform.value}")
        cli_logger.info(f"  ACL名称: {waf.acl_name}")
        cli_logger.info(f"  ACL ID: {waf.acl_id}")
        cli_logger.info(f"  范围: {waf.scope.value}")
        if waf.region:
            cli_logger.info(f"  区域: {waf.region.value}")
        if waf.proxy:
            cli_logger.info(f"  代理类型: {waf.proxy.proxy_type.value if waf.proxy.proxy_type else 'N/A'}")
    except AcunetixError as e:
        cli_logger.error(f"获取WAF配置 ID '{args.waf_id}' 详情失败: {e}")

def create_waf(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """创建新的WAF配置"""
    from acunetix_sdk.models.waf import WAFEntry
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info(f"正在创建WAF配置: 名称='{args.name}'")

    if not args.config_file:
        cli_logger.error("创建WAF配置失败: 必须通过 --config_file 提供包含配置的JSON文件路径。")
        return
        
    config_data = parse_waf_config_from_json_file(args.config_file)
    if not config_data:
        return

    waf_entry_data = WAFEntry(name=args.name, **config_data.model_dump())

    try:
        new_waf = client.wafs.create(waf_entry_data)
        cli_logger.info(f"WAF配置创建成功: ID='{new_waf.waf_id}', 名称='{new_waf.name}'")
    except AcunetixError as e:
        cli_logger.error(f"创建WAF配置失败: {e}")
    except Exception as e:
        cli_logger.error(f"创建WAF配置时发生意外错误: {e}")

def update_waf(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """更新WAF配置"""
    from acunetix_sdk.models.waf import WAFEntry
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info(f"正在更新WAF配置 ID '{args.waf_id}'...")

    if not args.name and not args.config_file:
        cli_logger.error("更新WAF配置失败: 必须提供 --name 或 --config_file。")
        return

    try:
        current_waf_dict = client.wafs.get(args.waf_id).model_dump(exclude={'waf_id'})
    except AcunetixError as e:
        cli_logger.error(f"无法获取当前WAF配置以进行更新: {e}")
        return
    
    if args.name:
        current_waf_dict['name'] = args.name
    
    if args.config_file:
        config_data_update = parse_waf_config_from_json_file(args.config_file)
        if not config_data_update:
            return
        config_update_dict = config_data_update.model_dump(exclude_unset=True)
        for key, value in config_update_dict.items():
             current_waf_dict[key] = value
    
    update_payload = WAFEntry(**current_waf_dict)
    
    try:
        updated_waf = client.wafs.update(args.waf_id, update_payload)
        cli_logger.info(f"WAF配置更新成功: ID='{updated_waf.waf_id}', 名称='{updated_waf.name}'")
    except AcunetixError as e:
        cli_logger.error(f"更新WAF配置 ID '{args.waf_id}' 失败: {e}")
    except Exception as e:
        cli_logger.error(f"更新WAF配置时发生意外错误: {e}")

def delete_waf(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """删除WAF配置"""
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info(f"正在删除WAF配置 ID: {args.waf_id}")
    try:
        client.wafs.delete(args.waf_id)
        cli_logger.info(f"WAF配置 ID '{args.waf_id}' 删除成功。")
    except AcunetixError as e:
        cli_logger.error(f"删除WAF配置 ID '{args.waf_id}' 失败: {e}")

def test_waf_connection(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """测试WAF连接"""
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info(f"正在测试WAF配置 ID '{args.waf_id}' 的连接...")
    try:
        status = client.wafs.test_connection(args.waf_id)
        if status.success:
            cli_logger.info(f"连接测试成功: {status.message or '无附加消息'}")
        else:
            cli_logger.error(f"连接测试失败: {status.message or '未知错误'}")
    except AcunetixError as e:
        cli_logger.error(f"测试WAF连接失败: {e}")
    except AttributeError:
        cli_logger.error("测试WAF连接失败: SDK 中可能尚未实现 'client.wafs.test_connection()' 方法。")

def register_wafs_parser(subparsers: argparse._SubParsersAction, parent_parser: argparse.ArgumentParser):
    """注册 wafs 命令的解析器"""
    wafs_parser = subparsers.add_parser("wafs", help="管理WAF配置", parents=[parent_parser])
    wafs_subparsers = wafs_parser.add_subparsers(title="操作", dest="action", required=True)

    list_wafs_parser = wafs_subparsers.add_parser("list", help="列出所有WAF配置", parents=[parent_parser])
    list_wafs_parser.set_defaults(func=list_wafs)

    get_waf_parser = wafs_subparsers.add_parser("get", help="获取特定WAF配置的详情", parents=[parent_parser])
    get_waf_parser.add_argument("waf_id", help="要获取详情的WAF ID")
    get_waf_parser.set_defaults(func=get_waf)

    create_waf_parser = wafs_subparsers.add_parser("create", help="创建新的WAF配置", parents=[parent_parser])
    create_waf_parser.add_argument("name", help="WAF配置的名称")
    create_waf_parser.add_argument("--config_file", required=True, help="包含 WAFConfig 数据的JSON文件路径")
    create_waf_parser.set_defaults(func=create_waf)

    update_waf_parser = wafs_subparsers.add_parser("update", help="更新WAF配置", parents=[parent_parser])
    update_waf_parser.add_argument("waf_id", help="要更新的WAF ID")
    update_waf_parser.add_argument("--name", help="新的WAF配置名称")
    update_waf_parser.add_argument("--config_file", help="包含 WAFConfig 更新数据的JSON文件路径")
    update_waf_parser.set_defaults(func=update_waf)

    delete_waf_parser = wafs_subparsers.add_parser("delete", help="删除WAF配置", parents=[parent_parser])
    delete_waf_parser.add_argument("waf_id", help="要删除的WAF ID")
    delete_waf_parser.set_defaults(func=delete_waf)

    test_waf_parser = wafs_subparsers.add_parser("test", help="测试WAF连接", parents=[parent_parser])
    test_waf_parser.add_argument("waf_id", help="要测试连接的WAF ID")
    test_waf_parser.set_defaults(func=test_waf_connection)
