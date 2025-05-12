# -*- coding: utf-8 -*-

"""
CLI 命令 - Reports 模块
"""

import logging
import argparse # 用于类型提示
from typing import TYPE_CHECKING

# 假设 AWVS_API_URL 将从 cli_config 模块导入或由主程序设置
# from ..cli_config import AWVS_API_URL # 这种相对导入可能不适用于脚本执行方式
# 更好的方式是在 main_cli.py 中加载配置，然后按需传递或使其可访问

if TYPE_CHECKING:
    from acunetix_sdk.client_sync import AcunetixSyncClient
    from acunetix_sdk.models.report import ReportCreate, ReportSource, ReportSourceListType, ReportStatus
    from acunetix_sdk.errors import AcunetixError
    from ..cli_config import AWVS_API_URL # For type hinting if used directly

def list_reports(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """列出所有已生成的报告"""
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info("正在获取报告列表...")
    try:
        response = client.reports.list(limit=args.limit or 20)
        if not response.reports:
            cli_logger.info("未找到任何报告。")
            return
        
        cli_logger.info(f"找到 {len(response.reports)} 个报告:")
        for report in response.reports:
            cli_logger.info(f"  ID: {report.report_id}, 模板: {report.template_name or 'N/A'}, "
                            f"状态: {report.status.value}, 生成日期: {report.generation_date or 'N/A'}")
    except AcunetixError as e:
        cli_logger.error(f"获取报告列表失败: {e}")

def generate_report(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """生成新报告"""
    from acunetix_sdk.models.report import ReportCreate, ReportSource, ReportSourceListType
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info(f"正在生成报告: 模板 ID='{args.template_id}', 来源类型='{args.source_type}', 来源 ID(s)='{args.source_ids}'")
    try:
        source_list_type = ReportSourceListType(args.source_type)
        report_source = ReportSource(list_type=source_list_type, id_list=args.source_ids)
        report_data = ReportCreate(template_id=args.template_id, source=report_source)
        
        new_report_info = client.reports.create(report_data)
        cli_logger.info(f"报告生成请求已提交。报告 ID: {new_report_info.report_id}, 状态: {new_report_info.status.value}")
        cli_logger.info("请使用 'reports get <report_id>' 或 'reports list' 命令检查报告状态和下载链接。")
    except ValueError as e:
        cli_logger.error(f"生成报告失败: 无效的来源类型 '{args.source_type}'. 错误: {e}")
        cli_logger.error(f"有效的来源类型包括: {[item.value for item in ReportSourceListType]}")
    except AcunetixError as e:
        cli_logger.error(f"生成报告失败: {e}")

def get_report(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """获取特定报告的详情和下载链接"""
    from acunetix_sdk.models.report import ReportStatus
    from acunetix_sdk.errors import AcunetixError
    from examples.cli.cli_config import AWVS_API_URL # 直接从配置模块获取

    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info(f"正在获取报告 ID '{args.report_id}' 的详情...")

    if not AWVS_API_URL: # 确保 API URL 已加载
        cli_logger.error("错误: AWVS_API_URL 未配置。请先运行 login 命令。")
        return

    try:
        report = client.reports.get(args.report_id)
        cli_logger.info(f"报告详情 - ID: {report.report_id}")
        cli_logger.info(f"  模板 ID: {report.template_id}")
        cli_logger.info(f"  模板名称: {report.template_name or 'N/A'}")
        cli_logger.info(f"  状态: {report.status.value}")
        cli_logger.info(f"  生成日期: {report.generation_date or 'N/A'}")
        if report.source:
            cli_logger.info(f"  来源类型: {report.source.list_type.value}")
            cli_logger.info(f"  来源 ID(s): {', '.join(report.source.id_list)}")
            if report.source.description:
                cli_logger.info(f"  来源描述: {report.source.description}")
        
        if report.status == ReportStatus.COMPLETED and report.download:
            cli_logger.info("  下载链接:")
            for link in report.download:
                full_download_link = f"{AWVS_API_URL.rstrip('/')}{link}"
                cli_logger.info(f"    {full_download_link}")
        elif report.status == ReportStatus.FAILED:
            cli_logger.warning("  报告生成失败。")
        elif report.status in [ReportStatus.PENDING, ReportStatus.GENERATING]:
            cli_logger.info("  报告仍在生成中。请稍后再试。")
        else:
            cli_logger.info("  未找到下载链接或报告未完成。")
            
    except AcunetixError as e:
        cli_logger.error(f"获取报告 ID '{args.report_id}' 详情失败: {e}")

def delete_report(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """删除报告"""
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info(f"正在删除报告 ID: {args.report_id}")
    try:
        client.reports.delete(args.report_id)
        cli_logger.info(f"报告 ID '{args.report_id}' 删除成功。")
    except AcunetixError as e:
        cli_logger.error(f"删除报告 ID '{args.report_id}' 失败: {e}")

def register_reports_parser(subparsers: argparse._SubParsersAction, parent_parser: argparse.ArgumentParser):
    """注册 reports 命令的解析器"""
    from acunetix_sdk.models.report import ReportSourceListType # 需要在注册时访问
    reports_parser = subparsers.add_parser("reports", help="管理报告", parents=[parent_parser])
    reports_subparsers = reports_parser.add_subparsers(title="操作", dest="action", required=True)

    list_reports_parser = reports_subparsers.add_parser("list", help="列出已生成的报告", parents=[parent_parser])
    list_reports_parser.add_argument("--limit", type=int, help="限制返回的报告数量")
    list_reports_parser.set_defaults(func=list_reports)

    generate_report_parser = reports_subparsers.add_parser("generate", help="生成新报告", parents=[parent_parser])
    generate_report_parser.add_argument("template_id", help="报告模板ID")
    generate_report_parser.add_argument("source_type", choices=[item.value for item in ReportSourceListType], help="报告来源类型")
    generate_report_parser.add_argument("source_ids", nargs='+', help="来源ID列表 (例如: 扫描ID, 目标ID)")
    generate_report_parser.set_defaults(func=generate_report)

    get_report_parser = reports_subparsers.add_parser("get", help="获取特定报告的详情和下载链接", parents=[parent_parser])
    get_report_parser.add_argument("report_id", help="要获取详情的报告ID")
    get_report_parser.set_defaults(func=get_report)
    
    delete_report_parser = reports_subparsers.add_parser("delete", help="删除报告", parents=[parent_parser])
    delete_report_parser.add_argument("report_id", help="要删除的报告ID")
    delete_report_parser.set_defaults(func=delete_report)
