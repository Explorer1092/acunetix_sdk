# -*- coding: utf-8 -*-

"""
CLI 命令 - Report Templates 模块
"""

import logging
import argparse # 用于类型提示
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from acunetix_sdk.client_sync import AcunetixSyncClient
    # Removed ReportTemplateCreateRequest, ReportTemplateUpdateRequest as they are no longer used
    from acunetix_sdk.models.report_template import ReportTemplateType 
    from acunetix_sdk.errors import AcunetixError

def list_report_templates(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """列出所有报告模板"""
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info("正在获取报告模板列表...")
    try:
        templates_list = client.report_templates.list() # 移除 limit 参数
        if not templates_list: # 直接检查列表是否为空
            cli_logger.info("未找到任何报告模板。")
            return
        
        cli_logger.info(f"找到 {len(templates_list)} 个报告模板:")
        for template in templates_list: # 直接遍历列表
            cli_logger.info(f"  ID: {template.template_id}, 名称: {template.name or 'N/A'}, "
                            f"组: {template.group or 'N/A'}")
            cli_logger.info(f"    可接受来源: {', '.join([src.value for src in template.accepted_sources]) if template.accepted_sources else 'N/A'}")
    except AcunetixError as e:
        cli_logger.error(f"获取报告模板列表失败: {e}")

def get_report_template(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """获取特定报告模板的详情"""
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info(f"正在获取报告模板 ID '{args.template_id}' 的详情...")
    try:
        template = client.report_templates.get(args.template_id)
        cli_logger.info(f"报告模板详情 - ID: {template.template_id}")
        cli_logger.info(f"  名称: {template.name or 'N/A'}")
        cli_logger.info(f"  组: {template.group or 'N/A'}")
        cli_logger.info(f"  可接受来源: {', '.join([src.value for src in template.accepted_sources]) if template.accepted_sources else 'N/A'}")
    except AcunetixError as e:
        cli_logger.error(f"获取报告模板 ID '{args.template_id}' 详情失败: {e}")

# create_report_template, update_report_template, delete_report_template 函数已被移除
# 因为底层 API 不支持这些操作。

def register_report_templates_parser(subparsers: argparse._SubParsersAction, parent_parser: argparse.ArgumentParser):
    """注册 report_templates 命令的解析器"""
    # from acunetix_sdk.models.report_template import ReportTemplateType # 不再需要，因为 create/update 已移除
    report_templates_parser = subparsers.add_parser("report_templates", help="管理报告模板 (仅支持 list 和 get 操作)", parents=[parent_parser])
    report_templates_subparsers = report_templates_parser.add_subparsers(title="操作", dest="action", required=True)

    list_report_templates_parser = report_templates_subparsers.add_parser("list", help="列出所有报告模板", parents=[parent_parser])
    list_report_templates_parser.set_defaults(func=list_report_templates)

    get_report_template_parser = report_templates_subparsers.add_parser("get", help="获取特定报告模板的详情", parents=[parent_parser])
    get_report_template_parser.add_argument("template_id", help="要获取详情的报告模板ID")
    get_report_template_parser.set_defaults(func=get_report_template)

    # create, update, delete 子解析器已被移除
