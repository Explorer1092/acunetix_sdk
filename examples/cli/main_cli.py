#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Acunetix AWVS CLI - 用于管理目标、扫描和报告的命令行工具 (模块化版本)。
"""

import argparse
import logging
import sys
from pathlib import Path
from urllib.parse import urlparse

# 将项目根目录添加到 sys.path，以便导入 acunetix_sdk 和 examples.cli.*
project_root = Path(__file__).resolve().parent.parent.parent # main_cli.py 在 examples/cli/ 下
sys.path.insert(0, str(project_root))

from acunetix_sdk.client_sync import AcunetixSyncClient
from acunetix_sdk.errors import AcunetixError

# from examples.cli.cli_config import (
#     load_config, AWVS_API_URL, AWVS_API_KEY, register_login_parser, cli_login
# )
from examples.cli import cli_config # 导入整个模块
from examples.cli.cli_config import register_login_parser # 单独导入 login 相关，因为它不依赖全局变量
from examples.cli.commands.targets_commands import register_targets_parser
from examples.cli.commands.scans_commands import register_scans_parser
from examples.cli.commands.scan_profiles_commands import register_scan_profiles_parser
from examples.cli.commands.target_groups_commands import register_target_groups_parser
from examples.cli.commands.reports_commands import register_reports_parser
from examples.cli.commands.report_templates_commands import register_report_templates_parser
from examples.cli.commands.users_commands import register_users_parser
from examples.cli.commands.user_groups_commands import register_user_groups_parser
from examples.cli.commands.roles_commands import register_roles_parser
from examples.cli.commands.vulnerabilities_commands import register_vulnerabilities_parser
from examples.cli.commands.exports_commands import register_exports_parser
from examples.cli.commands.notifications_commands import register_notifications_parser
from examples.cli.commands.issue_trackers_commands import register_issue_trackers_parser
from examples.cli.commands.wafs_commands import register_wafs_parser
from examples.cli.commands.excluded_hours_commands import register_excluded_hours_parser
from examples.cli.commands.agents_config_commands import register_agents_config_parser
from examples.cli.commands.workers_commands import register_workers_parser


def main():
    """主函数，解析参数并执行相应操作"""
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument('--debug', action='store_true', help='Enable debug logging for SDK and CLI.')

    # 1. 解析父解析器参数以获取 --debug 状态
    parent_args, remaining_argv = parent_parser.parse_known_args()

    # 2. 基于 --debug 状态配置日志
    log_level = logging.DEBUG if parent_args.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stdout # 输出到标准输出
    )
    # 后续获取的 logger (e.g., logging.getLogger("awvs_cli")) 将继承此配置

    # 3. 创建主解析器和子解析器
    parser = argparse.ArgumentParser(description="Acunetix AWVS 命令行工具 (模块化)", parents=[parent_parser])
    subparsers = parser.add_subparsers(title="模块", dest="module", help="可用的模块")
    
    # 4. 注册所有命令模块
    register_login_parser(subparsers, parent_parser) # login 是特殊顶级命令
    register_targets_parser(subparsers, parent_parser)
    register_scans_parser(subparsers, parent_parser)
    register_scan_profiles_parser(subparsers, parent_parser)
    register_target_groups_parser(subparsers, parent_parser)
    register_reports_parser(subparsers, parent_parser)
    register_report_templates_parser(subparsers, parent_parser)
    register_users_parser(subparsers, parent_parser)
    register_user_groups_parser(subparsers, parent_parser)
    register_roles_parser(subparsers, parent_parser)
    register_vulnerabilities_parser(subparsers, parent_parser)
    register_exports_parser(subparsers, parent_parser)
    register_notifications_parser(subparsers, parent_parser)
    register_issue_trackers_parser(subparsers, parent_parser)
    register_wafs_parser(subparsers, parent_parser)
    register_excluded_hours_parser(subparsers, parent_parser)
    register_agents_config_parser(subparsers, parent_parser)
    register_workers_parser(subparsers, parent_parser)

    # 5. 解析所有参数 (包括主命令和子命令的参数)
    # 使用 remaining_argv (来自 parent_parser.parse_known_args) 确保 --debug 不被再次解析
    # 或者，由于 parser 现在将 parent_parser 作为 parents，可以直接解析 sys.argv[1:]
    # 但为了安全，如果 parse_known_args 消耗了 --debug, 那么 parse_args 应该处理剩余的
    # 实际上，由于 parent_parser 是 parser 的一部分，parser.parse_args() 会处理所有参数
    args = parser.parse_args()

    # 如果是 login 命令，则不需要 client
    if args.module == "login" and hasattr(args, 'func'):
        args.func(args) 
        sys.exit(0)

    if not args.module or (args.module != "login" and (not hasattr(args, 'action') or not args.action)):
        parser.print_help()
        sys.exit(1)
        
    if not hasattr(args, 'func'):
        if args.module in subparsers.choices:
            subparsers.choices[args.module].print_help()
        else:
            parser.print_help()
        sys.exit(1)
            
    # 获取 logger 实例 (它们现在应该已由 basicConfig 根据 --debug 状态配置)
    cli_logger = logging.getLogger("awvs_cli") 
    sdk_logger_instance = logging.getLogger("acunetix_sdk")
    # http_logger = logging.getLogger("acunetix_sdk.http") # 也会继承

    if not cli_config.load_config():
        cli_logger.error("错误：API 配置未找到。请运行 'login' 命令进行配置，或设置 AWVS_API_URL 和 AWVS_API_KEY 环境变量。")
        sys.exit(1)
    if not cli_config.AWVS_API_URL or not cli_config.AWVS_API_KEY:
        cli_logger.error("错误：API URL 或 API Key 为空。请检查配置或环境变量。")
        sys.exit(1)
    
    parsed_url = urlparse(cli_config.AWVS_API_URL)
    if not parsed_url.scheme or not parsed_url.netloc:
        cli_logger.error(f"错误：AWVS_API_URL '{cli_config.AWVS_API_URL}' 格式无效。应为例如 'https://acunetix.example.com'")
        sys.exit(1)

    try:
        # 将 sdk_logger_instance (即 logging.getLogger("acunetix_sdk")) 传递给客户端
        # BaseAcunetixClient 将使用这个 logger。
        # AcunetixSyncClient 内部会为 http_client 创建一个子 logger "acunetix_sdk.http"
        client = AcunetixSyncClient(endpoint=cli_config.AWVS_API_URL, api_key=cli_config.AWVS_API_KEY, logger=sdk_logger_instance)
        
        # 简单的连接验证
        client.targets.list(limit=1) 
        sdk_logger_instance.info(f"成功连接到 Acunetix API: {cli_config.AWVS_API_URL}")

    except AcunetixError as e:
        cli_logger.error(f"连接 Acunetix API 失败: {e}")
        sys.exit(1)
    except Exception as e:
        cli_logger.error(f"初始化 API 客户端时发生未知错误: {e}", exc_info=True if args.debug else False)
        sys.exit(1)
        
    # 所有命令函数期望 (client, args) 作为参数
    args.func(client, args)

if __name__ == "__main__":
    main()
