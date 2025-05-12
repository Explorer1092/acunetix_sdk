# -*- coding: utf-8 -*-

"""
CLI 命令 - Workers (扫描代理) 模块
"""

import logging
import argparse # 用于类型提示
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from acunetix_sdk.client_sync import AcunetixSyncClient
    from acunetix_sdk.models.worker import WorkerDescription
    from acunetix_sdk.errors import AcunetixError

def list_workers(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """列出所有扫描代理 (Workers)"""
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info("正在获取扫描代理列表...")
    try:
        response = client.workers.list()
        if not response.workers:
            cli_logger.info("未找到任何扫描代理。")
            return
        
        cli_logger.info(f"找到 {len(response.workers)} 个扫描代理:")
        for worker in response.workers:
            cli_logger.info(f"  ID: {worker.worker_id}, 描述: {worker.description or 'N/A'}")
            cli_logger.info(f"    扫描应用: {worker.scanning_app.value}, 端点: {worker.endpoint}")
            cli_logger.info(f"    状态: {worker.status.value if worker.status else 'N/A'}, "
                            f"授权状态: {worker.authorization.value if worker.authorization else 'N/A'}")
            cli_logger.info(f"    版本: {worker.app_version or 'N/A'}, 许可证状态: {worker.license_status or 'N/A'}")
            if worker.targets:
                 cli_logger.info(f"    关联目标数: {len(worker.targets)}")
            cli_logger.info("-" * 10)
    except AcunetixError as e:
        cli_logger.error(f"获取扫描代理列表失败: {e}")

def get_worker(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """获取特定扫描代理的详情"""
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info(f"正在获取扫描代理 ID '{args.worker_id}' 的详情...")
    try:
        worker = client.workers.get(args.worker_id)
        cli_logger.info(f"扫描代理详情 - ID: {worker.worker_id}")
        cli_logger.info(f"  描述: {worker.description or 'N/A'}")
        cli_logger.info(f"  扫描应用: {worker.scanning_app.value}")
        cli_logger.info(f"  端点: {worker.endpoint}")
        cli_logger.info(f"  状态: {worker.status.value if worker.status else 'N/A'}")
        cli_logger.info(f"  授权状态: {worker.authorization.value if worker.authorization else 'N/A'}")
        cli_logger.info(f"  应用版本: {worker.app_version or 'N/A'}")
        cli_logger.info(f"  许可证状态: {worker.license_status or 'N/A'}")
        cli_logger.info(f"  最大扫描数: {worker.max_scans if hasattr(worker, 'max_scans') else 'N/A'}")
        cli_logger.info(f"  当前扫描数: {worker.current_scans if hasattr(worker, 'current_scans') else 'N/A'}")
        cli_logger.info(f"  通知状态: {'启用' if worker.notification_status else '禁用' if hasattr(worker, 'notification_status') and worker.notification_status is not None else 'N/A'}")

        if worker.targets:
            cli_logger.info(f"  关联目标ID: {', '.join(worker.targets)}")
    except AcunetixError as e:
        if getattr(e, "status_code", None) == 404:
            cli_logger.info(f"扫描代理 ID '{args.worker_id}' 不存在。")
        else:
            cli_logger.error(f"获取扫描代理 ID '{args.worker_id}' 详情失败: {e}")

def update_worker_description(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """更新扫描代理的描述"""
    from acunetix_sdk.models.worker import WorkerDescription
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info(f"正在更新扫描代理 ID '{args.worker_id}' 的描述为: '{args.description}'")
    
    description_data = WorkerDescription(description=args.description)
    
    try:
        client.workers.rename(args.worker_id, description_data)
        cli_logger.info(f"扫描代理 ID '{args.worker_id}' 描述更新成功。")
    except AcunetixError as e:
        if getattr(e, "status_code", None) == 404:
            cli_logger.info(f"扫描代理 ID '{args.worker_id}' 不存在，无法更新描述。")
        else:
            cli_logger.error(f"更新扫描代理描述失败: {e}")
    except AttributeError:
        cli_logger.error("更新扫描代理描述失败: SDK 中可能尚未实现相关方法 (例如 'rename' 或 'update_description')。")

def authorize_worker(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """授权扫描代理"""
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info(f"正在授权扫描代理 ID: {args.worker_id}")
    try:
        client.workers.authorize(args.worker_id)
        cli_logger.info(f"扫描代理 ID '{args.worker_id}' 授权成功。")
    except AcunetixError as e:
        if getattr(e, "status_code", None) == 404:
            cli_logger.info(f"扫描代理 ID '{args.worker_id}' 不存在，无法授权。")
        else:
            cli_logger.error(f"授权扫描代理 ID '{args.worker_id}' 失败: {e}")

def deauthorize_worker(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """取消授权/分离扫描代理"""
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info(f"正在取消授权/分离扫描代理 ID: {args.worker_id}")
    try:
        client.workers.deauthorize(args.worker_id)
        cli_logger.info(f"扫描代理 ID '{args.worker_id}' 取消授权/分离成功。")
    except AcunetixError as e:
        if getattr(e, "status_code", None) == 404:
            cli_logger.info(f"扫描代理 ID '{args.worker_id}' 不存在，无法取消授权/分离。")
        else:
            cli_logger.error(f"取消授权/分离扫描代理 ID '{args.worker_id}' 失败: {e}")

def delete_worker(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """删除扫描代理"""
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info(f"正在删除扫描代理 ID: {args.worker_id}")
    try:
        client.workers.delete(args.worker_id)
        cli_logger.info(f"扫描代理 ID '{args.worker_id}' 删除成功。")
    except AcunetixError as e:
        if getattr(e, "status_code", None) == 404:
            cli_logger.info(f"扫描代理 ID '{args.worker_id}' 已不存在，无需删除。")
        else:
            cli_logger.error(f"删除扫描代理 ID '{args.worker_id}' 失败: {e}")

def register_workers_parser(subparsers: argparse._SubParsersAction, parent_parser: argparse.ArgumentParser):
    """注册 workers 命令的解析器"""
    workers_parser = subparsers.add_parser("workers", help="管理扫描代理 (Workers)", parents=[parent_parser])
    workers_subparsers = workers_parser.add_subparsers(title="操作", dest="action", required=True)

    list_workers_parser = workers_subparsers.add_parser("list", help="列出所有扫描代理", parents=[parent_parser])
    list_workers_parser.set_defaults(func=list_workers)

    get_worker_parser = workers_subparsers.add_parser("get", help="获取特定扫描代理的详情", parents=[parent_parser])
    get_worker_parser.add_argument("worker_id", help="要获取详情的扫描代理ID")
    get_worker_parser.set_defaults(func=get_worker)

    update_desc_parser = workers_subparsers.add_parser("update_description", help="更新扫描代理的描述", parents=[parent_parser])
    update_desc_parser.add_argument("worker_id", help="要更新描述的扫描代理ID")
    update_desc_parser.add_argument("description", help="新的描述内容")
    update_desc_parser.set_defaults(func=update_worker_description)

    authorize_parser = workers_subparsers.add_parser("authorize", help="授权扫描代理", parents=[parent_parser])
    authorize_parser.add_argument("worker_id", help="要授权的扫描代理ID")
    authorize_parser.set_defaults(func=authorize_worker)

    deauthorize_parser = workers_subparsers.add_parser("deauthorize", help="取消授权/分离扫描代理", parents=[parent_parser])
    deauthorize_parser.add_argument("worker_id", help="要取消授权的扫描代理ID")
    deauthorize_parser.set_defaults(func=deauthorize_worker)

    delete_parser = workers_subparsers.add_parser("delete", help="删除扫描代理", parents=[parent_parser])
    delete_parser.add_argument("worker_id", help="要删除的扫描代理ID")
    delete_parser.set_defaults(func=delete_worker)
