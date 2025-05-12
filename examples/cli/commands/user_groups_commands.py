# -*- coding: utf-8 -*-

"""
CLI 命令 - User Groups 模块
"""

import logging
import argparse # 用于类型提示
import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from acunetix_sdk.client_sync import AcunetixSyncClient
    from acunetix_sdk.models.user import UserGroup, RoleMapping, UserToUserGroupDetails, RoleMappingIdList
    from acunetix_sdk.errors import AcunetixError

def list_user_groups(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """列出所有用户组"""
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info("正在获取用户组列表...")
    try:
        # 确保传递 extended 参数 (如果 args 中存在)
        response = client.user_groups.list(limit=args.limit or 100, extended=args.extended if hasattr(args, 'extended') else None)
        if not response.items: # 使用 response.items
            cli_logger.info("未找到任何用户组。")
            return
        
        cli_logger.info(f"找到 {len(response.items)} 个用户组:") # 使用 response.items
        for group in response.items: # 使用 response.items
            cli_logger.info(f"  ID: {group.user_group_id}, 名称: {group.name}, 描述: {group.description or 'N/A'}")
            user_count_display = 'N/A'
            if hasattr(group, 'stats') and group.stats and hasattr(group.stats, 'user_count'):
                 user_count_display = group.stats.user_count
            cli_logger.info(f"    用户数量: {user_count_display}")
            # 如果 extended 为 True 并且数据存在，则显示额外信息
            if hasattr(args, 'extended') and args.extended:
                if hasattr(group, 'user_ids') and group.user_ids:
                     cli_logger.info(f"    用户ID: {', '.join(group.user_ids)}")
                if hasattr(group, 'role_mappings') and group.role_mappings:
                    cli_logger.info("    角色映射:")
                    for rm in group.role_mappings:
                        rm_details = f"映射ID: {rm.role_mapping_id}, 角色ID: {rm.role_id}, 访问所有目标: {'是' if rm.access_all_targets else '否'}"
                        if rm.target_group_ids:
                            rm_details += f", 目标组ID: {', '.join(rm.target_group_ids)}"
                        cli_logger.info(f"      {rm_details}")
    except AcunetixError as e:
        cli_logger.error(f"获取用户组列表失败: {e}")

def get_user_group(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """获取特定用户组的详情"""
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info(f"正在获取用户组 ID '{args.group_id}' 的详情...")
    try:
        group = client.user_groups.get(args.group_id)
        cli_logger.info(f"用户组详情 - ID: {group.user_group_id}")
        cli_logger.info(f"  名称: {group.name}")
        cli_logger.info(f"  描述: {group.description or 'N/A'}")
        cli_logger.info(f"  创建时间: {group.created_at or 'N/A'}")
        cli_logger.info(f"  用户数量: {group.stats.user_count if group.stats else 'N/A'}")
        if group.user_ids:
            # 过滤掉 None 值，然后 join
            valid_user_ids = [uid for uid in group.user_ids if uid is not None]
            if valid_user_ids:
                cli_logger.info(f"  用户ID: {', '.join(valid_user_ids)}")
            else:
                cli_logger.info("  用户ID: 无 (或仅包含无效条目)")
        else:
            cli_logger.info("  用户ID: 无") # 如果 group.user_ids 本身是 None 或空列表
        if group.role_mappings:
            cli_logger.info("  角色映射:")
            for rm in group.role_mappings:
                cli_logger.info(f"    映射ID: {rm.role_mapping_id}, 角色ID: {rm.role_id}, "
                                f"访问所有目标: {'是' if rm.access_all_targets else '否'}")
                if rm.target_group_ids:
                    cli_logger.info(f"      目标组ID: {', '.join(rm.target_group_ids)}")
    except AcunetixError as e:
        cli_logger.error(f"获取用户组 ID '{args.group_id}' 详情失败: {e}")

def create_user_group(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """创建新用户组"""
    from acunetix_sdk.models.user import UserGroup, RoleMapping
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info(f"正在创建用户组: 名称='{args.name}', 描述='{args.description}'")

    role_mappings_data = []
    if args.role_mappings_json:
        try:
            mappings_list = json.loads(args.role_mappings_json)
            if not isinstance(mappings_list, list): raise ValueError("角色映射JSON必须是一个列表。")
            for mapping_dict in mappings_list:
                role_mappings_data.append(RoleMapping(**mapping_dict))
        except Exception as e:
            cli_logger.error(f"创建用户组失败: 解析角色映射时出错 - {e}")
            return
            
    user_ids_data = args.user_ids.split(',') if args.user_ids else []

    group_data = UserGroup(
        name=args.name,
        description=args.description or "",
        role_mappings=role_mappings_data if role_mappings_data else None,
        user_ids=user_ids_data if user_ids_data else None
    )
    
    try:
        new_group = client.user_groups.create(group_data)
        cli_logger.info(f"用户组创建成功: ID='{new_group.user_group_id}', 名称='{new_group.name}'")
    except AcunetixError as e:
        cli_logger.error(f"创建用户组失败: {e}")
    except Exception as e:
        cli_logger.error(f"创建用户组时发生意外错误: {e}")

def update_user_group(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """更新用户组信息"""
    from acunetix_sdk.models.user import UserGroupUpdate, RoleMapping # Changed UserGroup to UserGroupUpdate
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")

    if not any([args.name, args.description is not None, args.role_mappings_json is not None, args.user_ids is not None]):
        cli_logger.error("错误: 至少需要提供一个更新参数。")
        return

    cli_logger.info(f"正在更新用户组 ID '{args.group_id}'...")
    
    update_data_dict = {}
    if args.name:
        update_data_dict['name'] = args.name
    if args.description is not None:
        update_data_dict['description'] = args.description
    
    if args.role_mappings_json is not None:
        try:
            mappings_list = json.loads(args.role_mappings_json)
            if not isinstance(mappings_list, list): raise ValueError("角色映射JSON必须是一个列表。")
            update_data_dict['role_mappings'] = [RoleMapping(**mapping_dict) for mapping_dict in mappings_list]
        except Exception as e:
            cli_logger.error(f"更新用户组失败: 解析角色映射时出错 - {e}")
            return
            
    if args.user_ids is not None:
        # For UserGroupUpdate, user_ids should be List[Optional[str]] or None
        # If user_ids is an empty string from CLI, split(',') might give [''], filter that out.
        raw_user_ids = args.user_ids.split(',')
        update_data_dict['user_ids'] = [uid for uid in raw_user_ids if uid] if args.user_ids else None

    update_payload = UserGroupUpdate(**update_data_dict) # Use UserGroupUpdate model

    try:
        client.user_groups.update(args.group_id, update_payload)
        cli_logger.info(f"用户组 ID '{args.group_id}' 的更新请求已发送。正在获取更新后的信息...")
        # 重新获取用户组信息以显示更新
        updated_group_info = client.user_groups.get(args.group_id)
        cli_logger.info(f"用户组更新成功: ID='{updated_group_info.user_group_id}', "
                        f"名称='{updated_group_info.name}', "
                        f"描述='{updated_group_info.description or 'N/A'}'")
    except AcunetixError as e:
        cli_logger.error(f"更新用户组 ID '{args.group_id}' 失败: {e}")
    except Exception as e:
        cli_logger.error(f"更新用户组时发生意外错误: {e}")

def delete_user_group(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """删除用户组"""
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info(f"正在删除用户组 ID: {args.group_id}")
    try:
        client.user_groups.delete(args.group_id)
        cli_logger.info(f"用户组 ID '{args.group_id}' 删除成功。")
    except AcunetixError as e:
        cli_logger.error(f"删除用户组 ID '{args.group_id}' 失败: {e}")

def add_users_to_group(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """向用户组添加用户"""
    from acunetix_sdk.models.user import UserToUserGroupDetails
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    user_ids_list = args.user_ids.split(',')
    cli_logger.info(f"正在向用户组 ID '{args.group_id}' 添加用户: {', '.join(user_ids_list)}")
    # payload 应该是 ChildUserIdList 类型，根据 SDK 方法签名
    from acunetix_sdk.models.user import ChildUserIdList 
    payload = ChildUserIdList(user_id_list=user_ids_list)
    try:
        # 使用正确的方法名 add_users_to_group
        client.user_groups.add_users_to_group(args.group_id, payload)
        cli_logger.info(f"成功向用户组 ID '{args.group_id}' 添加用户。")
    except AcunetixError as e:
        cli_logger.error(f"向用户组添加用户失败: {e}")

def remove_users_from_group(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """从用户组移除用户"""
    from acunetix_sdk.models.user import UserToUserGroupDetails
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    user_ids_list = args.user_ids.split(',')
    cli_logger.info(f"正在从用户组 ID '{args.group_id}' 移除用户: {', '.join(user_ids_list)}")
    # payload 应该是 ChildUserIdList 类型，根据 SDK 方法签名
    from acunetix_sdk.models.user import ChildUserIdList
    payload = ChildUserIdList(user_id_list=user_ids_list)
    try:
        # 使用正确的方法名 remove_users_from_group
        client.user_groups.remove_users_from_group(args.group_id, payload)
        cli_logger.info(f"成功从用户组 ID '{args.group_id}' 移除用户。")
    except AcunetixError as e:
        cli_logger.error(f"从用户组移除用户失败: {e}")

def add_role_mappings_to_group(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """向用户组添加角色映射"""
    from acunetix_sdk.models.user import RoleMapping
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info(f"正在向用户组 ID '{args.group_id}' 添加角色映射...")
    try:
        mappings_list_dict = json.loads(args.role_mappings_json)
        if not isinstance(mappings_list_dict, list): raise ValueError("角色映射JSON必须是一个列表。")
        
        # payload 应该是 RoleMappingList 类型
        from acunetix_sdk.models.user import RoleMappingList
        role_mappings_payload = RoleMappingList(role_mappings=[RoleMapping(**mapping_dict) for mapping_dict in mappings_list_dict])
        
        # 使用正确的方法名 add_role_mappings_to_group
        response = client.user_groups.add_role_mappings_to_group(args.group_id, role_mappings_payload)
        cli_logger.info(f"成功向用户组 ID '{args.group_id}' 添加 {len(response.role_mappings or [])} 个角色映射。")
    except json.JSONDecodeError:
        cli_logger.error("添加角色映射失败: 提供的JSON格式无效。")
    except ValueError as ve:
        cli_logger.error(f"添加角色映射失败: 数据错误 - {ve}")
    except AcunetixError as e:
        cli_logger.error(f"向用户组添加角色映射失败: {e}")
    except Exception as e:
        cli_logger.error(f"添加角色映射时发生意外错误: {e}")

def remove_role_mappings_from_group(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """从用户组移除角色映射"""
    from acunetix_sdk.models.user import RoleMappingIdList
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    mapping_ids_list = args.mapping_ids.split(',')
    cli_logger.info(f"正在从用户组 ID '{args.group_id}' 移除角色映射ID: {', '.join(mapping_ids_list)}")
    payload = RoleMappingIdList(role_mapping_ids=mapping_ids_list)
    try:
        # 使用正确的方法名 remove_role_mappings_from_group
        client.user_groups.remove_role_mappings_from_group(args.group_id, payload)
        cli_logger.info(f"成功从用户组 ID '{args.group_id}' 移除角色映射。")
    except AcunetixError as e:
        cli_logger.error(f"从用户组移除角色映射失败: {e}")

def register_user_groups_parser(subparsers: argparse._SubParsersAction, parent_parser: argparse.ArgumentParser):
    """注册 user_groups 命令的解析器"""
    from acunetix_sdk.models.user import UserGroupUpdate # Import for type hint if needed, though not strictly for CLI parsing here
    user_groups_parser = subparsers.add_parser("user_groups", help="管理用户组", parents=[parent_parser])
    user_groups_subparsers = user_groups_parser.add_subparsers(title="操作", dest="action", required=True)

    list_user_groups_parser = user_groups_subparsers.add_parser("list", help="列出所有用户组", parents=[parent_parser])
    list_user_groups_parser.add_argument("--limit", type=int, help="限制返回的用户组数量")
    list_user_groups_parser.add_argument("--extended", action='store_true', help="显示扩展信息 (如用户和角色映射)")
    list_user_groups_parser.set_defaults(func=list_user_groups)

    get_user_group_parser = user_groups_subparsers.add_parser("get", help="获取特定用户组的详情", parents=[parent_parser])
    get_user_group_parser.add_argument("group_id", help="要获取详情的用户组ID")
    get_user_group_parser.set_defaults(func=get_user_group)

    create_user_group_parser = user_groups_subparsers.add_parser("create", help="创建新用户组", parents=[parent_parser])
    create_user_group_parser.add_argument("name", help="用户组名称")
    create_user_group_parser.add_argument("--description", help="用户组描述", default="")
    create_user_group_parser.add_argument("--user_ids", help="逗号分隔的用户ID列表")
    create_user_group_parser.add_argument("--role_mappings_json", help="角色映射的JSON字符串")
    create_user_group_parser.set_defaults(func=create_user_group)

    update_user_group_parser = user_groups_subparsers.add_parser("update", help="更新用户组信息", parents=[parent_parser])
    update_user_group_parser.add_argument("group_id", help="要更新的用户组ID")
    update_user_group_parser.add_argument("--name", help="新的用户组名称")
    update_user_group_parser.add_argument("--description", help="新的用户组描述")
    update_user_group_parser.add_argument("--user_ids", help="新的逗号分隔的用户ID列表")
    update_user_group_parser.add_argument("--role_mappings_json", help="新的角色映射JSON字符串")
    update_user_group_parser.set_defaults(func=update_user_group)

    delete_user_group_parser = user_groups_subparsers.add_parser("delete", help="删除用户组", parents=[parent_parser])
    delete_user_group_parser.add_argument("group_id", help="要删除的用户组ID")
    delete_user_group_parser.set_defaults(func=delete_user_group)

    add_users_to_group_parser = user_groups_subparsers.add_parser("add_users", help="向用户组添加用户", parents=[parent_parser])
    add_users_to_group_parser.add_argument("group_id", help="用户组ID")
    add_users_to_group_parser.add_argument("user_ids", help="逗号分隔的要添加的用户ID列表")
    add_users_to_group_parser.set_defaults(func=add_users_to_group)

    remove_users_from_group_parser = user_groups_subparsers.add_parser("remove_users", help="从用户组移除用户", parents=[parent_parser])
    remove_users_from_group_parser.add_argument("group_id", help="用户组ID")
    remove_users_from_group_parser.add_argument("user_ids", help="逗号分隔的要移除的用户ID列表")
    remove_users_from_group_parser.set_defaults(func=remove_users_from_group)

    add_rm_to_group_parser = user_groups_subparsers.add_parser("add_role_mappings", help="向用户组添加角色映射", parents=[parent_parser])
    add_rm_to_group_parser.add_argument("group_id", help="用户组ID")
    add_rm_to_group_parser.add_argument("role_mappings_json", help="角色映射的JSON字符串")
    add_rm_to_group_parser.set_defaults(func=add_role_mappings_to_group)

    remove_rm_from_group_parser = user_groups_subparsers.add_parser("remove_role_mappings", help="从用户组移除角色映射", parents=[parent_parser])
    remove_rm_from_group_parser.add_argument("group_id", help="用户组ID")
    remove_rm_from_group_parser.add_argument("mapping_ids", help="逗号分隔的要移除的角色映射ID列表")
    remove_rm_from_group_parser.set_defaults(func=remove_role_mappings_from_group)
