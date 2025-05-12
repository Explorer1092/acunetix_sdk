# -*- coding: utf-8 -*-

"""
CLI 命令 - Vulnerabilities 模块
"""

import logging
import argparse # 用于类型提示
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from acunetix_sdk.client_sync import AcunetixSyncClient
    from acunetix_sdk.models.vulnerability import VulnerabilityStatus, VulnStatusEnum
    from acunetix_sdk.errors import AcunetixError

def list_vulnerabilities(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """列出系统中的漏洞"""
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info(f"正在获取漏洞列表... (查询: '{args.query}', 限制: {args.limit or 100})")
    try:
        response = client.vulnerabilities.list(query=args.query, limit=args.limit or 100, sort=args.sort)
        if not response.items:
            cli_logger.info("未找到任何漏洞。")
            return
        
        cli_logger.info(f"找到 {response.pagination.count if response.pagination else len(response.items)} 个漏洞 (显示 {len(response.items)} 个):")
        for vuln in response.items:
            cli_logger.info(f"  ID: {vuln.vuln_id}, 名称: {vuln.vt_name or 'N/A'}")
            cli_logger.info(f"    目标: {vuln.target_description or vuln.target_id or 'N/A'}, 地址: {vuln.affects_url or 'N/A'}")
            cli_logger.info(f"    严重性: {vuln.severity}, 状态: {vuln.status.value if vuln.status else 'N/A'}, 置信度: {vuln.confidence}")
            cli_logger.info(f"    首次发现: {vuln.first_seen or 'N/A'}, 最后发现: {vuln.last_seen or 'N/A'}")
            cli_logger.info("-" * 20)
    except AcunetixError as e:
        cli_logger.error(f"获取漏洞列表失败: {e}")

def get_vulnerability(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """获取特定漏洞的详情"""
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info(f"正在获取漏洞 ID '{args.vuln_id}' 的详情...")
    try:
        vuln = client.vulnerabilities.get_details(args.vuln_id)
        cli_logger.info(f"漏洞详情 - ID: {vuln.vuln_id}")
        cli_logger.info(f"  名称: {vuln.vt_name or 'N/A'}")
        cli_logger.info(f"  目标ID: {vuln.target_id or 'N/A'}")
        cli_logger.info(f"  目标描述: {vuln.target_description or 'N/A'}")
        cli_logger.info(f"  影响URL: {vuln.affects_url or 'N/A'}")
        cli_logger.info(f"  影响详情: {vuln.affects_detail or 'N/A'}")
        cli_logger.info(f"  严重性: {vuln.severity}, 状态: {vuln.status.value if vuln.status else 'N/A'}, 置信度: {vuln.confidence}")
        cli_logger.info(f"  首次发现: {vuln.first_seen or 'N/A'}, 最后发现: {vuln.last_seen or 'N/A'}")
        cli_logger.info(f"  CVSS2: {vuln.cvss2 or 'N/A'}, CVSS3: {vuln.cvss3 or 'N/A'}")
        cli_logger.info(f"  描述: {vuln.description or 'N/A'}")
        cli_logger.info(f"  长描述: {vuln.long_description or 'N/A'}")
        cli_logger.info(f"  影响: {vuln.impact or 'N/A'}")
        cli_logger.info(f"  建议: {vuln.recommendation or 'N/A'}")
        if vuln.details:
             cli_logger.info(f"  技术细节: {vuln.details}")
        if vuln.request:
             cli_logger.info(f"  HTTP请求: (二进制数据，长度 {len(vuln.request)} bytes)")
    except AcunetixError as e:
        cli_logger.error(f"获取漏洞 ID '{args.vuln_id}' 详情失败: {e}")

def update_vulnerabilities_status(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """更新一个或多个漏洞的状态"""
    from acunetix_sdk.models.vulnerability import VulnerabilityStatus, VulnStatusEnum
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    vuln_ids_list = args.vuln_ids.split(',')
    
    try:
        new_status = VulnStatusEnum(args.status)
    except ValueError:
        cli_logger.error(f"错误: 无效的状态 '{args.status}'. "
                         f"有效状态为: {[item.value for item in VulnStatusEnum]}")
        return

    cli_logger.info(f"正在更新漏洞 ID(s) '{', '.join(vuln_ids_list)}' 的状态为 '{new_status.value}' "
                    f"{(', 评论: ' + args.comment) if args.comment else ''}")
    
    status_update_data = VulnerabilityStatus(status=new_status, comment=args.comment)
    
    success_ids = []
    failure_ids = {}

    for vuln_id in vuln_ids_list:
        vuln_id = vuln_id.strip() # 清理可能存在的空格
        if not vuln_id:
            continue
        try:
            cli_logger.info(f"正在为漏洞 ID '{vuln_id}' 更新状态为 '{new_status.value}'...")
            client.vulnerabilities.update_status(vuln_id, status_update_data)
            success_ids.append(vuln_id)
            cli_logger.info(f"漏洞 ID '{vuln_id}' 状态更新请求已发送。")
        except AcunetixError as e:
            cli_logger.error(f"更新漏洞 ID '{vuln_id}' 状态失败: {e}")
            failure_ids[vuln_id] = str(e)
        except Exception as e:
            cli_logger.error(f"更新漏洞 ID '{vuln_id}' 状态时发生意外错误: {e}")
            failure_ids[vuln_id] = str(e)

    if success_ids:
        cli_logger.info(f"成功更新状态的漏洞 ID: {', '.join(success_ids)}")
    if failure_ids:
        cli_logger.warning(f"未能更新状态的漏洞 ID:")
        for vid, err_msg in failure_ids.items():
            cli_logger.warning(f"  - {vid}: {err_msg}")
    
    if not success_ids and not failure_ids:
        cli_logger.info("没有提供有效的漏洞ID进行更新。")
    elif not failure_ids and success_ids:
        cli_logger.info("所有指定漏洞的状态均已成功发送更新请求。")
    elif failure_ids and not success_ids:
        cli_logger.error("所有指定漏洞的状态更新均失败。")
    else: # Some succeeded, some failed
        cli_logger.warning("部分漏洞的状态更新成功，部分失败。请查看上面的日志。")

    # except AcunetixError as e: # Original block, now handled inside loop
    #     cli_logger.error(f"更新漏洞状态失败: {e}")
    # except Exception as e: # This block is now redundant as exceptions are handled inside the loop
    #     cli_logger.error(f"更新漏洞状态时发生意外错误: {e}")

def register_vulnerabilities_parser(subparsers: argparse._SubParsersAction, parent_parser: argparse.ArgumentParser):
    """注册 vulnerabilities 命令的解析器"""
    from acunetix_sdk.models.vulnerability import VulnStatusEnum # 需要在注册时访问
    vulnerabilities_parser = subparsers.add_parser("vulnerabilities", help="管理漏洞", parents=[parent_parser])
    vulnerabilities_subparsers = vulnerabilities_parser.add_subparsers(title="操作", dest="action", required=True)

    list_vulnerabilities_parser = vulnerabilities_subparsers.add_parser("list", help="列出漏洞", parents=[parent_parser])
    list_vulnerabilities_parser.add_argument("-q", "--query", help="用于过滤漏洞的查询字符串")
    list_vulnerabilities_parser.add_argument("-l", "--limit", type=int, help="限制返回的漏洞数量")
    list_vulnerabilities_parser.add_argument("-s", "--sort", help="排序字段和方向")
    list_vulnerabilities_parser.set_defaults(func=list_vulnerabilities)

    get_vulnerability_parser = vulnerabilities_subparsers.add_parser("get", help="获取特定漏洞的详情", parents=[parent_parser])
    get_vulnerability_parser.add_argument("vuln_id", help="要获取详情的漏洞ID")
    get_vulnerability_parser.set_defaults(func=get_vulnerability)

    update_vuln_status_parser = vulnerabilities_subparsers.add_parser("update_status", help="更新一个或多个漏洞的状态", parents=[parent_parser])
    update_vuln_status_parser.add_argument("vuln_ids", help="逗号分隔的要更新状态的漏洞ID列表")
    update_vuln_status_parser.add_argument("status", choices=[s.value for s in VulnStatusEnum], help="新的漏洞状态")
    update_vuln_status_parser.add_argument("--comment", help="更新状态时的评论")
    update_vuln_status_parser.set_defaults(func=update_vulnerabilities_status)
