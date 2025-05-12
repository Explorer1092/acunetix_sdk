# -*- coding: utf-8 -*-

"""
CLI 命令 - Exports 模块
"""

import logging
import argparse # 用于类型提示
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from acunetix_sdk.client_sync import AcunetixSyncClient
    from acunetix_sdk.models.export import NewExport, ExportSource, ExportStatusEnum
    from acunetix_sdk.models.report import ReportSourceListType # Reused
    from acunetix_sdk.errors import AcunetixError
    # from ..cli_config import AWVS_API_URL # For type hinting if used directly

def list_export_types(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """列出所有可用的导出类型/模板"""
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info("正在获取可用导出类型列表...")
    try:
        response = client.exports.list_export_types()
        if not response.templates:
            cli_logger.info("未找到任何导出类型。")
            return
        
        cli_logger.info(f"找到 {len(response.templates)} 个导出类型:")
        for export_type in response.templates:
            cli_logger.info(f"  导出类型ID (用于创建): {export_type.export_id}")
            cli_logger.info(f"    名称: {export_type.name or 'N/A'}")
            cli_logger.info(f"    内容类型: {export_type.content_type or 'N/A'}")
            if export_type.accepted_sources:
                sources_str = ", ".join([s.value for s in export_type.accepted_sources])
                cli_logger.info(f"    可接受来源: {sources_str}")
            cli_logger.info("-" * 10)
    except AcunetixError as e:
        cli_logger.error(f"获取导出类型列表失败: {e}")
    except AttributeError:
        cli_logger.error("获取导出类型列表失败: SDK 中可能尚未实现 'client.exports.list_export_types()' 方法。")

# Removed list_exports function as the GET /exports endpoint does not exist in the API.

def create_export(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """创建新的导出任务"""
    from acunetix_sdk.models.export import NewExport, ExportSource
    from acunetix_sdk.models.report import ReportSourceListType # Reused
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info(f"正在创建导出任务: 导出类型ID='{args.export_type_id}', "
                    f"来源类型='{args.source_type}', 来源ID(s)='{args.source_ids}'")
    try:
        source_list_type = ReportSourceListType(args.source_type)
        export_source = ExportSource(list_type=source_list_type, id_list=args.source_ids, waf_id=args.waf_id)
        export_data = NewExport(export_id=args.export_type_id, source=export_source)
        
        new_export_info_tuple = client.exports.create_export(export_data) # Changed from create to create_export
        new_export_info = new_export_info_tuple[0] # The Export object is the first element
        cli_logger.info(f"导出任务创建请求已提交。导出记录ID: {new_export_info.export_id or new_export_info.report_id}, " # Use fallback for clarity
                        f"状态: {new_export_info.status.value if new_export_info.status else 'N/A'}")
        cli_logger.info("请使用 'exports get <export_record_id>' 命令检查状态和下载链接。") # Removed 'exports list'
    except ValueError as e:
        cli_logger.error(f"创建导出任务失败: 无效的来源类型 '{args.source_type}'. 错误: {e}")
        cli_logger.error(f"有效的来源类型包括: {[item.value for item in ReportSourceListType]}")
    except AcunetixError as e:
        cli_logger.error(f"创建导出任务失败: {e}")

def get_export(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """获取特定导出任务的详情和下载链接"""
    from acunetix_sdk.models.export import ExportStatusEnum
    from acunetix_sdk.errors import AcunetixError
    from examples.cli.cli_config import AWVS_API_URL # 直接从配置模块获取

    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info(f"正在获取导出记录 ID '{args.export_record_id}' 的详情...")

    if not AWVS_API_URL:
        cli_logger.error("错误: AWVS_API_URL 未配置。请先运行 login 命令。")
        return

    try:
        export_item = client.exports.get(args.export_record_id)
        cli_logger.info(f"导出详情 - 记录ID: {export_item.export_id}")
        cli_logger.info(f"  导出类型ID (模板): {export_item.export_type_id}")
        cli_logger.info(f"  模板名称: {export_item.template_name or 'N/A'}")
        cli_logger.info(f"  状态: {export_item.status.value if export_item.status else 'N/A'}")
        cli_logger.info(f"  生成日期: {export_item.generation_date or 'N/A'}")
        if export_item.source:
            cli_logger.info(f"  来源类型: {export_item.source.list_type.value}")
            cli_logger.info(f"  来源 ID(s): {', '.join(export_item.source.id_list) if export_item.source.id_list else 'N/A'}")
            if export_item.source.waf_id:
                 cli_logger.info(f"  WAF ID: {export_item.source.waf_id}")

        if export_item.status == ExportStatusEnum.COMPLETED and export_item.download:
            cli_logger.info("  下载链接:")
            for link in export_item.download:
                full_download_link = f"{AWVS_API_URL.rstrip('/')}{link}"
                cli_logger.info(f"    {full_download_link}")
        elif export_item.status == ExportStatusEnum.FAILED:
            cli_logger.warning("  导出失败。")
        elif export_item.status in [ExportStatusEnum.PENDING, ExportStatusEnum.PROCESSING]:
            cli_logger.info("  导出仍在处理中。请稍后再试。")
        else:
            cli_logger.info("  未找到下载链接或导出未完成/失败。")
            
    except AcunetixError as e:
        cli_logger.error(f"获取导出记录 ID '{args.export_record_id}' 详情失败: {e}")

def delete_export(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """删除导出任务记录"""
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info(f"正在删除导出记录 ID: {args.export_record_id}")
    try:
        client.exports.delete(args.export_record_id)
        cli_logger.info(f"导出记录 ID '{args.export_record_id}' 删除成功。")
    except AcunetixError as e:
        cli_logger.error(f"删除导出记录 ID '{args.export_record_id}' 失败: {e}")

def register_exports_parser(subparsers: argparse._SubParsersAction, parent_parser: argparse.ArgumentParser):
    """注册 exports 命令的解析器"""
    from acunetix_sdk.models.report import ReportSourceListType # Reused
    exports_parser = subparsers.add_parser("exports", help="管理导出任务", parents=[parent_parser])
    exports_subparsers = exports_parser.add_subparsers(title="操作", dest="action", required=True)

    list_export_types_parser = exports_subparsers.add_parser("list_types", help="列出可用的导出类型/模板", parents=[parent_parser])
    list_export_types_parser.set_defaults(func=list_export_types)

    # Removed list_exports subparser as the functionality is removed.

    create_export_parser = exports_subparsers.add_parser("create", help="创建新的导出任务", parents=[parent_parser])
    create_export_parser.add_argument("export_type_id", help="导出类型ID (从 'exports list_types' 获取)")
    create_export_parser.add_argument("source_type", choices=[item.value for item in ReportSourceListType], help="导出来源类型")
    create_export_parser.add_argument("source_ids", nargs='+', help="来源ID列表")
    create_export_parser.add_argument("--waf_id", help="如果导出到WAF，提供WAF ID")
    create_export_parser.set_defaults(func=create_export)

    get_export_parser = exports_subparsers.add_parser("get", help="获取特定导出任务的详情", parents=[parent_parser])
    get_export_parser.add_argument("export_record_id", help="要获取详情的导出记录ID")
    get_export_parser.set_defaults(func=get_export)
    
    delete_export_parser = exports_subparsers.add_parser("delete", help="删除导出任务记录", parents=[parent_parser])
    delete_export_parser.add_argument("export_record_id", help="要删除的导出记录ID")
    delete_export_parser.set_defaults(func=delete_export)
