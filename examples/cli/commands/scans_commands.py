# -*- coding: utf-8 -*-

"""
CLI 命令 - Scans 模块
"""

import logging
import argparse # 用于类型提示
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from acunetix_sdk.client_sync import AcunetixSyncClient
    from acunetix_sdk.models.scan import ScanCreateRequest
    from acunetix_sdk.errors import AcunetixError

def start_scan(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """针对指定目标启动扫描"""
    from acunetix_sdk.models.scan import ScanCreateRequest
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info(f"正在为目标 ID '{args.target_id}' 启动扫描，使用扫描配置 ID '{args.profile_id}'")
    try:
        target_details = None
        try:
            target_details = client.targets.get(args.target_id)
            cli_logger.info(f"找到目标: {target_details.address}")
        except AcunetixError:
            cli_logger.error(f"错误: 目标 ID '{args.target_id}' 未找到。")
            return

        try:
            profile = client.scan_profiles.get(args.profile_id)
            cli_logger.info(f"使用扫描配置: {profile.name}")
        except AcunetixError:
            cli_logger.error(f"错误: 扫描配置 ID '{args.profile_id}' 未找到。")
            return
            
        scan_request = ScanCreateRequest(
            target_id=args.target_id,
            profile_id=args.profile_id,
            schedule={
                "disable": False,
                "start_date": None, 
                "time_sensitive": False
            }
        )
        scan_response = client.scans.create(scan_request) 
        if scan_response and scan_response.scan_id:
            status_display = "N/A"
            if scan_response.current_session and scan_response.current_session.status:
                status_display = scan_response.current_session.status.value
            elif scan_response.schedule and not scan_response.schedule.disable:
                status_display = "scheduled"

            target_address_display = target_details.address if target_details else "N/A"
            cli_logger.info(f"扫描启动/计划成功。扫描 ID: {scan_response.scan_id}, 目标: {target_address_display}, 状态: {status_display}")
        else:
            cli_logger.error("启动扫描失败，API 未返回有效的扫描信息。")
            
    except AcunetixError as e:
        cli_logger.error(f"启动扫描失败: {e}")

def list_scans(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """列出扫描任务"""
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info("正在获取扫描任务列表...")
    try:
        scans_response = client.scans.list(limit=args.limit or 20)
        if scans_response.pagination.count == 0:
            cli_logger.info("未找到任何扫描任务。")
            return

        cli_logger.info(f"找到 {scans_response.pagination.count} 个扫描任务:")
        for scan in scans_response.items:
            status_display = "N/A"
            if scan.current_session and scan.current_session.status:
                status_display = scan.current_session.status.value
            scan_type = scan.profile_name if scan.profile_name else "N/A"
            cli_logger.info(f"  扫描 ID: {scan.scan_id}, 目标: {scan.target.address}, 类型: {scan_type}, 状态: {status_display}")
    except AcunetixError as e:
        cli_logger.error(f"获取扫描列表失败: {e}")

def get_scan_status(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """获取特定扫描的状态"""
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info(f"正在获取扫描 ID '{args.scan_id}' 的状态...")
    try:
        scan_details = client.scans.get(args.scan_id)
        if scan_details and scan_details.current_session:
            status_display = "N/A"
            if scan_details.current_session.status:
                status_display = scan_details.current_session.status.value
            progress = scan_details.current_session.progress if scan_details.current_session.progress is not None else "N/A"
            
            cli_logger.info(f"扫描 ID: {scan_details.scan_id}")
            cli_logger.info(f"  目标地址: {scan_details.target.address}")
            cli_logger.info(f"  状态: {status_display}")
            cli_logger.info(f"  进度: {progress}%")
            start_time_str = str(scan_details.current_session.start_date) if scan_details.current_session.start_date else "N/A"
            cli_logger.info(f"  会话开始时间: {start_time_str}")
            if status_display == "completed" or status_display == "aborted":
                 cli_logger.info(f"  (注意: 详细的会话结束时间目前无法直接从 current_session 获取)")
        else:
            cli_logger.error(f"未找到扫描 ID '{args.scan_id}' 或扫描无当前会话。")
    except AcunetixError as e:
        cli_logger.error(f"获取扫描 ID '{args.scan_id}' 状态失败: {e}")

def get_scan_results(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """获取特定扫描的结果 (漏洞列表)"""
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info(f"正在获取扫描 ID '{args.scan_id}' 的结果...")
    try:
        scan_details = client.scans.get(args.scan_id)
        if not scan_details or not scan_details.current_session:
            cli_logger.error(f"未找到扫描 ID '{args.scan_id}' 或扫描无当前会话。")
            return
        
        scan_session_id = scan_details.current_session.scan_session_id
        cli_logger.info(f"使用扫描 ID '{args.scan_id}' 和扫描会话 ID '{scan_session_id}' 获取漏洞...")

        query_string = None 
        vulnerabilities_response = client.scans.get_vulnerabilities(
            scan_id=args.scan_id,
            result_id=scan_session_id,
            query=query_string,
            limit=args.limit or 100
        )

        if vulnerabilities_response.pagination.count == 0:
            cli_logger.info(f"扫描 ID '{args.scan_id}' (会话 ID '{scan_session_id}') 未发现任何漏洞。")
            return

        cli_logger.info(f"扫描 ID '{args.scan_id}' (会话 ID '{scan_session_id}') 发现 {vulnerabilities_response.pagination.count} 个漏洞:")
        for vuln in vulnerabilities_response.items:
            cli_logger.info(f"  名称: {vuln.vt_name}")
            cli_logger.info(f"    漏洞 ID: {vuln.vuln_id}")
            cli_logger.info(f"    严重性: {vuln.severity}")
            cli_logger.info(f"    状态: {vuln.status}")
            cli_logger.info(f"    影响: {vuln.affects_url}")
            cli_logger.info("-" * 20)
            
    except AcunetixError as e:
        cli_logger.error(f"获取扫描 ID '{args.scan_id}' 结果失败: {e}")

def stop_scan(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """中止正在进行的扫描"""
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info(f"正在中止扫描 ID: {args.scan_id}")
    try:
        client.scans.abort(args.scan_id)
        cli_logger.info(f"扫描 ID '{args.scan_id}' 中止请求已发送。")
    except AcunetixError as e:
        cli_logger.error(f"中止扫描 ID '{args.scan_id}' 失败: {e}")

def delete_scan(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """删除扫描记录"""
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info(f"正在删除扫描 ID: {args.scan_id}")
    try:
        client.scans.delete(args.scan_id)
        cli_logger.info(f"扫描 ID '{args.scan_id}' 删除成功。")
    except AcunetixError as e:
        cli_logger.error(f"删除扫描 ID '{args.scan_id}' 失败: {e}")

def register_scans_parser(subparsers: argparse._SubParsersAction, parent_parser: argparse.ArgumentParser):
    """注册 scans 命令的解析器"""
    scans_parser = subparsers.add_parser("scans", help="管理扫描任务", parents=[parent_parser])
    scans_subparsers = scans_parser.add_subparsers(title="操作", dest="action", required=True)

    start_scan_parser = scans_subparsers.add_parser("start", help="启动新扫描", parents=[parent_parser])
    start_scan_parser.add_argument("target_id", help="要扫描的目标ID")
    start_scan_parser.add_argument("profile_id", help="使用的扫描配置ID")
    start_scan_parser.set_defaults(func=start_scan)

    list_scans_parser = scans_subparsers.add_parser("list", help="列出扫描任务", parents=[parent_parser])
    list_scans_parser.add_argument("--limit", type=int, help="限制返回的扫描数量")
    list_scans_parser.set_defaults(func=list_scans)
    
    status_scan_parser = scans_subparsers.add_parser("status", help="获取特定扫描的状态", parents=[parent_parser])
    status_scan_parser.add_argument("scan_id", help="要查询状态的扫描ID")
    status_scan_parser.set_defaults(func=get_scan_status)

    results_scan_parser = scans_subparsers.add_parser("results", help="获取特定扫描的结果 (漏洞)", parents=[parent_parser])
    results_scan_parser.add_argument("scan_id", help="要获取结果的扫描ID")
    results_scan_parser.add_argument("--limit", type=int, help="限制返回的漏洞数量")
    results_scan_parser.set_defaults(func=get_scan_results)

    stop_scan_parser = scans_subparsers.add_parser("stop", help="中止正在进行的扫描", parents=[parent_parser])
    stop_scan_parser.add_argument("scan_id", help="要中止的扫描ID")
    stop_scan_parser.set_defaults(func=stop_scan)

    delete_scan_parser = scans_subparsers.add_parser("delete", help="删除扫描记录", parents=[parent_parser])
    delete_scan_parser.add_argument("scan_id", help="要删除的扫描ID")
    delete_scan_parser.set_defaults(func=delete_scan)
