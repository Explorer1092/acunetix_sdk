# -*- coding: utf-8 -*-

"""
CLI 命令 - Notifications 模块
"""

import logging
import argparse # 用于类型提示
import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from acunetix_sdk.client_sync import AcunetixSyncClient
    from acunetix_sdk.models.notification import (
        NotificationCreateRequest, NotificationUpdateRequest, NotificationEvent, NotificationScope
    )
    from acunetix_sdk.errors import AcunetixError

def list_notifications(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """列出所有通知配置"""
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info("正在获取通知配置列表...")
    try:
        response = client.notifications.list(limit=args.limit or 100) # Assuming 'unread' param is not used by CLI for configs
        if not response.items: # Changed from response.notifications
            cli_logger.info("未找到任何通知配置。")
            return
        
        cli_logger.info(f"找到 {len(response.items)} 个通知配置:") # Changed from response.notifications
        for notif_config in response.items: # Changed from response.notifications
            cli_logger.info(f"  ID: {notif_config.notification_id}, 名称: {notif_config.name or 'N/A'}")
            # notif_config.event is now Optional[str]
            cli_logger.info(f"    事件: {notif_config.event or 'N/A'}, "
                            f"禁用: {'是' if notif_config.disabled else '否'}")
            if notif_config.scope:
                # notif_config.scope.type is now str
                scope_desc = f"类型: {notif_config.scope.type or 'N/A'}"
                if notif_config.scope.target_id: scope_desc += f", 目标ID: {notif_config.scope.target_id}"
                if notif_config.scope.group_id: scope_desc += f", 组ID: {notif_config.scope.group_id}"
                cli_logger.info(f"    范围: {scope_desc}")
            if notif_config.email_address:
                cli_logger.info(f"    邮件地址: {', '.join(notif_config.email_address)}")
            if notif_config.webhook_url:
                cli_logger.info(f"    Webhook URL: {notif_config.webhook_url}")
            cli_logger.info("-" * 10)
    except AcunetixError as e:
        cli_logger.error(f"获取通知配置列表失败: {e}")

def get_notification(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """获取特定通知配置的详情"""
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info(f"正在获取通知配置 ID '{args.notification_id}' 的详情...")
    try:
        notif_config = client.notifications.get(args.notification_id)
        cli_logger.info(f"通知配置详情 - ID: {notif_config.notification_id}")
        cli_logger.info(f"  名称: {notif_config.name or 'N/A'}")
        # notif_config.event is now Optional[str]
        cli_logger.info(f"  事件: {notif_config.event or 'N/A'}")
        cli_logger.info(f"  禁用: {'是' if notif_config.disabled else '否'}")
        if notif_config.scope:
            # notif_config.scope.type is now str
            scope_desc = f"类型: {notif_config.scope.type or 'N/A'}"
            if notif_config.scope.target_id: scope_desc += f", 目标ID: {notif_config.scope.target_id}"
            if notif_config.scope.group_id: scope_desc += f", 组ID: {notif_config.scope.group_id}"
            cli_logger.info(f"  范围: {scope_desc}")
        if notif_config.email_address:
            cli_logger.info(f"  邮件地址: {', '.join(notif_config.email_address)}")
        if notif_config.webhook_url:
            cli_logger.info(f"  Webhook URL: {notif_config.webhook_url}")
    except AcunetixError as e:
        cli_logger.error(f"获取通知配置 ID '{args.notification_id}' 详情失败: {e}")

def create_notification(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """创建新的通知配置"""
    from acunetix_sdk.models.notification import (
        NotificationCreateRequest, NotificationEvent, NotificationScope
    )
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info(f"正在创建通知配置: 名称='{args.name}', 事件='{args.event}'")

    try:
        event_type = NotificationEvent(args.event)
    except ValueError:
        cli_logger.error(f"错误: 无效的事件类型 '{args.event}'. "
                         f"有效类型为: {[item.value for item in NotificationEvent]}")
        return

    scope_data = None
    if args.scope_json:
        try:
            scope_dict = json.loads(args.scope_json)
            scope_data = NotificationScope(**scope_dict)
        except json.JSONDecodeError:
            cli_logger.error("创建通知配置失败: 范围JSON格式无效。")
            return
        except Exception as e:
            cli_logger.error(f"创建通知配置失败: 解析范围数据时出错 - {e}")
            return
    elif args.scope_type:
        scope_data = NotificationScope(type=args.scope_type, target_id=args.scope_target_id, group_id=args.scope_group_id)
    else:
        cli_logger.error("创建通知配置失败: 必须提供范围信息 (--scope_json 或 --scope_type)。")
        return

    if not args.email_addresses and not args.webhook_url:
        cli_logger.error("创建通知配置失败: 必须提供电子邮件地址或Webhook URL。")
        return

    email_list = args.email_addresses.split(',') if args.email_addresses else None

    notif_data = NotificationCreateRequest(
        name=args.name,
        event=event_type,
        scope=scope_data,
        disabled=args.disabled,
        email_address=email_list,
        webhook_url=args.webhook_url
    )
    
    try:
        new_notif = client.notifications.create(notif_data)
        cli_logger.info(f"通知配置创建成功: ID='{new_notif.notification_id}', 名称='{new_notif.name}'")
    except AcunetixError as e:
        cli_logger.error(f"创建通知配置失败: {e}")
    except Exception as e:
        cli_logger.error(f"创建通知配置时发生意外错误: {e}")

def update_notification(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """更新通知配置"""
    from acunetix_sdk.models.notification import (
        NotificationUpdateRequest, NotificationEvent, NotificationScope
    )
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    
    if not any([args.name, args.event, args.scope_json, args.scope_type, 
                args.disabled is not None, args.email_addresses is not None, args.webhook_url is not None]):
        cli_logger.error("错误: 至少需要提供一个更新参数。")
        return

    cli_logger.info(f"正在更新通知配置 ID '{args.notification_id}'...")
    
    update_payload = {}
    if args.name: update_payload['name'] = args.name
    if args.event:
        try:
            update_payload['event'] = NotificationEvent(args.event)
        except ValueError:
            cli_logger.error(f"错误: 无效的事件类型 '{args.event}'.")
            return
    if args.disabled is not None: update_payload['disabled'] = args.disabled
    if args.email_addresses is not None:
        update_payload['email_address'] = args.email_addresses.split(',') if args.email_addresses else []
    if args.webhook_url is not None:
        update_payload['webhook_url'] = args.webhook_url

    if args.scope_json:
        try:
            scope_dict = json.loads(args.scope_json)
            update_payload['scope'] = NotificationScope(**scope_dict)
        except Exception as e:
            cli_logger.error(f"更新通知配置失败: 解析范围JSON时出错 - {e}")
            return
    elif args.scope_type:
        current_notif = client.notifications.get(args.notification_id)
        current_scope = current_notif.scope if current_notif and current_notif.scope else NotificationScope(type=args.scope_type)
        
        new_scope_dict = {'type': args.scope_type}
        if args.scope_target_id is not None: new_scope_dict['target_id'] = args.scope_target_id 
        elif hasattr(current_scope, 'target_id'): new_scope_dict['target_id'] = current_scope.target_id
        
        if args.scope_group_id is not None: new_scope_dict['group_id'] = args.scope_group_id
        elif hasattr(current_scope, 'group_id'): new_scope_dict['group_id'] = current_scope.group_id
        
        update_payload['scope'] = NotificationScope(**new_scope_dict)

    update_data_model = NotificationUpdateRequest(**update_payload)

    try:
        updated_notif = client.notifications.update(args.notification_id, update_data_model)
        cli_logger.info(f"通知配置更新成功: ID='{updated_notif.notification_id}', 名称='{updated_notif.name or 'N/A'}'")
    except AcunetixError as e:
        cli_logger.error(f"更新通知配置 ID '{args.notification_id}' 失败: {e}")
    except Exception as e:
        cli_logger.error(f"更新通知配置时发生意外错误: {e}")

def delete_notification(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """删除通知配置"""
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info(f"正在删除通知配置 ID: {args.notification_id}")
    try:
        client.notifications.delete_configuration(args.notification_id) # Changed to delete_configuration
        cli_logger.info(f"通知配置 ID '{args.notification_id}' 删除成功。")
    except AcunetixError as e:
        cli_logger.error(f"删除通知配置 ID '{args.notification_id}' 失败: {e}")

def register_notifications_parser(subparsers: argparse._SubParsersAction, parent_parser: argparse.ArgumentParser):
    """注册 notifications 命令的解析器"""
    from acunetix_sdk.models.notification import NotificationEvent # 需要在注册时访问
    notifications_parser = subparsers.add_parser("notifications", help="管理通知配置", parents=[parent_parser])
    notifications_subparsers = notifications_parser.add_subparsers(title="操作", dest="action", required=True)

    list_notifications_parser = notifications_subparsers.add_parser("list", help="列出所有通知配置", parents=[parent_parser])
    list_notifications_parser.add_argument("--limit", type=int, help="限制返回的通知配置数量")
    list_notifications_parser.set_defaults(func=list_notifications)

    get_notification_parser = notifications_subparsers.add_parser("get", help="获取特定通知配置的详情", parents=[parent_parser])
    get_notification_parser.add_argument("notification_id", help="要获取详情的通知配置ID")
    get_notification_parser.set_defaults(func=get_notification)

    create_notification_parser = notifications_subparsers.add_parser("create", help="创建新的通知配置", parents=[parent_parser])
    create_notification_parser.add_argument("name", help="通知配置名称")
    create_notification_parser.add_argument("event", choices=[e.value for e in NotificationEvent], help="触发通知的事件类型")
    create_notification_parser.add_argument("--scope_json", help="范围的JSON字符串")
    create_notification_parser.add_argument("--scope_type", help="范围类型 (如果不用 --scope_json)")
    create_notification_parser.add_argument("--scope_target_id", help="特定目标ID (如果 scope_type 为 'target')")
    create_notification_parser.add_argument("--scope_group_id", help="特定目标组ID (如果 scope_type 为 'group')")
    create_notification_parser.add_argument("--disabled", action='store_true', help="创建时禁用此通知")
    create_notification_parser.add_argument("--email_addresses", help="逗号分隔的电子邮件地址列表")
    create_notification_parser.add_argument("--webhook_url", help="Webhook URL")
    create_notification_parser.set_defaults(func=create_notification)
    
    update_notification_parser = notifications_subparsers.add_parser("update", help="更新通知配置", parents=[parent_parser])
    update_notification_parser.add_argument("notification_id", help="要更新的通知配置ID")
    update_notification_parser.add_argument("--name", help="新的通知配置名称")
    update_notification_parser.add_argument("--event", choices=[e.value for e in NotificationEvent], help="新的事件类型")
    update_notification_parser.add_argument("--scope_json", help="新的范围JSON字符串")
    update_notification_parser.add_argument("--scope_type", help="新的范围类型")
    update_notification_parser.add_argument("--scope_target_id", help="新的特定目标ID")
    update_notification_parser.add_argument("--scope_group_id", help="新的特定目标组ID")
    update_notification_parser.add_argument("--disabled", type=lambda x: (str(x).lower() == 'true'), help="是否禁用 (true/false)")
    update_notification_parser.add_argument("--email_addresses", help="新的电子邮件地址列表 (空字符串清空)")
    update_notification_parser.add_argument("--webhook_url", help="新的Webhook URL (空字符串清空)")
    update_notification_parser.set_defaults(func=update_notification)

    delete_notification_parser = notifications_subparsers.add_parser("delete", help="删除通知配置", parents=[parent_parser])
    delete_notification_parser.add_argument("notification_id", help="要删除的通知配置ID")
    delete_notification_parser.set_defaults(func=delete_notification)
