# -*- coding: utf-8 -*-

"""
CLI 命令 - Roles 模块
"""

import logging
import argparse # 用于类型提示
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from acunetix_sdk.client_sync import AcunetixSyncClient
    from acunetix_sdk.models.user import Role # Role model is in user.py
    from acunetix_sdk.errors import AcunetixError

def list_roles(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """列出所有角色"""
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info("正在获取角色列表...")
    try:
        response = client.roles.list(limit=args.limit or 100)
        if not response.items: # 更改 response.roles 为 response.items
            cli_logger.info("未找到任何角色。")
            return
        
        cli_logger.info(f"找到 {len(response.items)} 个角色:") # 更改 response.roles 为 response.items
        for role in response.items: # 更改 response.roles 为 response.items
            cli_logger.info(f"  ID: {role.role_id}, 名称: {role.name}, 描述: {role.description or 'N/A'}")
            if role.stats:
                cli_logger.info(f"    用户数: {role.stats.user_count or 0}, "
                                f"组数: {role.stats.group_count or 0}, "
                                f"总用户数: {role.stats.all_user_count or 0}")
    except AcunetixError as e:
        cli_logger.error(f"获取角色列表失败: {e}")

def get_role(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """获取特定角色的详情"""
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info(f"正在获取角色 ID '{args.role_id}' 的详情...")
    try:
        role = client.roles.get(args.role_id)
        cli_logger.info(f"角色详情 - ID: {role.role_id}")
        cli_logger.info(f"  名称: {role.name}")
        cli_logger.info(f"  描述: {role.description or 'N/A'}")
        cli_logger.info(f"  创建时间: {role.created_at or 'N/A'}")
        if role.permissions:
            cli_logger.info(f"  权限: {', '.join(role.permissions)}")
        if role.stats:
            cli_logger.info(f"  统计 - 用户数: {role.stats.user_count or 0}, "
                            f"组数: {role.stats.group_count or 0}, "
                            f"总用户数: {role.stats.all_user_count or 0}")
    except AcunetixError as e:
        cli_logger.error(f"获取角色 ID '{args.role_id}' 详情失败: {e}")

def create_role(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """创建新角色"""
    from acunetix_sdk.models.user import Role
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    permissions_list = args.permissions.split(',') if args.permissions else []
    cli_logger.info(f"正在创建角色: 名称='{args.name}', 描述='{args.description}', 权限='{permissions_list}'")
    
    role_data = Role(
        name=args.name,
        description=args.description or "",
        permissions=permissions_list
    )
    
    try:
        new_role = client.roles.create(role_data)
        cli_logger.info(f"角色创建成功: ID='{new_role.role_id}', 名称='{new_role.name}'")
    except AcunetixError as e:
        cli_logger.error(f"创建角色失败: {e}")
    except Exception as e:
        cli_logger.error(f"创建角色时发生意外错误: {e}")

def update_role(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """更新角色信息"""
    from acunetix_sdk.models.user import RoleUpdate # Changed Role to RoleUpdate
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")

    if not any([args.name, args.description is not None, args.permissions is not None]):
        cli_logger.error("错误: 至少需要提供一个更新参数 (--name, --description, --permissions)。")
        return

    cli_logger.info(f"正在更新角色 ID '{args.role_id}'...")
    
    update_data_dict = {}
    if args.name:
        update_data_dict['name'] = args.name
    if args.description is not None:
        update_data_dict['description'] = args.description
    if args.permissions is not None:
        update_data_dict['permissions'] = args.permissions.split(',') if args.permissions else [] # Keep as list of strings
    
    update_payload = RoleUpdate(**update_data_dict) # Use RoleUpdate model
    
    try:
        client.roles.update(args.role_id, update_payload)
        cli_logger.info(f"角色 ID '{args.role_id}' 的更新请求已发送。正在获取更新后的信息...")
        # 重新获取角色信息以显示更新
        updated_role_info = client.roles.get(args.role_id)
        cli_logger.info(f"角色更新成功: ID='{updated_role_info.role_id}', "
                        f"名称='{updated_role_info.name}', "
                        f"描述='{updated_role_info.description or 'N/A'}'")
        if updated_role_info.permissions:
            cli_logger.info(f"  更新后权限: {', '.join(updated_role_info.permissions)}")
    except AcunetixError as e:
        cli_logger.error(f"更新角色 ID '{args.role_id}' 失败: {e}")
    except Exception as e:
        cli_logger.error(f"更新角色时发生意外错误: {e}")

def delete_role(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """删除角色"""
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info(f"正在删除角色 ID: {args.role_id}")
    try:
        client.roles.delete(args.role_id)
        cli_logger.info(f"角色 ID '{args.role_id}' 删除成功。")
    except AcunetixError as e:
        cli_logger.error(f"删除角色 ID '{args.role_id}' 失败: {e}")

def list_permissions(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """列出所有可用权限"""
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info("正在获取可用权限列表...")
    try:
        permissions_response = client.roles.get_permissions() # 使用正确的方法名 get_permissions
        if not permissions_response.permissions:
            cli_logger.info("未找到任何权限信息。")
            return
        
        cli_logger.info("可用权限:")
        for perm in permissions_response.permissions:
            cli_logger.info(f"  名称: {perm.name or 'N/A'}")
            cli_logger.info(f"    类别: {perm.category or 'N/A'}")
            cli_logger.info(f"    描述: {perm.description or 'N/A'}")
            cli_logger.info("-" * 10)
    except AcunetixError as e:
        cli_logger.error(f"获取权限列表失败: {e}")
    except AttributeError:
        cli_logger.error("获取权限列表失败: SDK 中可能尚未实现 'client.roles.list_permissions()' 方法。")

def register_roles_parser(subparsers: argparse._SubParsersAction, parent_parser: argparse.ArgumentParser):
    """注册 roles 命令的解析器"""
    roles_parser = subparsers.add_parser("roles", help="管理角色和权限", parents=[parent_parser])
    roles_subparsers = roles_parser.add_subparsers(title="操作", dest="action", required=True)

    list_roles_parser = roles_subparsers.add_parser("list", help="列出所有角色", parents=[parent_parser])
    list_roles_parser.add_argument("--limit", type=int, help="限制返回的角色数量")
    list_roles_parser.set_defaults(func=list_roles)

    get_role_parser = roles_subparsers.add_parser("get", help="获取特定角色的详情", parents=[parent_parser])
    get_role_parser.add_argument("role_id", help="要获取详情的角色ID")
    get_role_parser.set_defaults(func=get_role)

    create_role_parser = roles_subparsers.add_parser("create", help="创建新角色", parents=[parent_parser])
    create_role_parser.add_argument("name", help="角色名称")
    create_role_parser.add_argument("--description", help="角色描述", default="")
    create_role_parser.add_argument("--permissions", help="逗号分隔的权限名称列表", required=True)
    create_role_parser.set_defaults(func=create_role)

    update_role_parser = roles_subparsers.add_parser("update", help="更新角色信息", parents=[parent_parser])
    update_role_parser.add_argument("role_id", help="要更新的角色ID")
    update_role_parser.add_argument("--name", help="新的角色名称")
    update_role_parser.add_argument("--description", help="新的角色描述")
    update_role_parser.add_argument("--permissions", help="新的逗号分隔的权限名称列表")
    update_role_parser.set_defaults(func=update_role)

    delete_role_parser = roles_subparsers.add_parser("delete", help="删除角色", parents=[parent_parser])
    delete_role_parser.add_argument("role_id", help="要删除的角色ID")
    delete_role_parser.set_defaults(func=delete_role)

    list_permissions_parser = roles_subparsers.add_parser("list_permissions", help="列出所有可用权限", parents=[parent_parser])
    list_permissions_parser.set_defaults(func=list_permissions)
