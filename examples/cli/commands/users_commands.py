# -*- coding: utf-8 -*-

"""
CLI 命令 - Users 模块
"""

import logging
import argparse # 用于类型提示
import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from acunetix_sdk.client_sync import AcunetixSyncClient
    from acunetix_sdk.models.user import UserCreate, UserUpdate, RoleMappingCreate
    from acunetix_sdk.errors import AcunetixError

def list_users(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """列出所有用户"""
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info("正在获取用户列表...")
    try:
        response = client.users.list(limit=args.limit or 100)
        if not response.items: # 更改 response.users 为 response.items
            cli_logger.info("未找到任何用户。")
            return
        
        cli_logger.info(f"找到 {len(response.items)} 个用户:") # 更改 response.users 为 response.items
        for user in response.items: # 更改 response.users 为 response.items
            cli_logger.info(f"  ID: {user.user_id}, 姓名: {user.first_name} {user.last_name}, "
                            f"邮箱: {user.email}, 启用: {'是' if user.enabled else '否'}")
    except AcunetixError as e:
        cli_logger.error(f"获取用户列表失败: {e}")

def get_user(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """获取特定用户的详情"""
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info(f"正在获取用户 ID '{args.user_id}' 的详情...")
    try:
        user = client.users.get(args.user_id)
        cli_logger.info(f"用户详情 - ID: {user.user_id}")
        cli_logger.info(f"  姓名: {user.first_name} {user.last_name}")
        cli_logger.info(f"  邮箱: {user.email}")
        cli_logger.info(f"  启用: {'是' if user.enabled else '否'}")
        cli_logger.info(f"  TOTP启用: {'是' if user.totp_enabled else '否'}")
        cli_logger.info(f"  锁定状态: {user.locked if user.locked is not None else 'N/A'}")
        cli_logger.info(f"  账户过期日期: {user.expiration_date or 'N/A'}")
        cli_logger.info(f"  SSO豁免: {'是' if user.sso_exemption else '否'}")

        if user.role_mappings:
            cli_logger.info("  角色映射:")
            for rm in user.role_mappings:
                cli_logger.info(f"    角色ID: {rm.role_id}")
                cli_logger.info(f"      访问所有目标: {'是' if rm.access_all_targets else '否'}")
                if rm.target_group_ids:
                    cli_logger.info(f"      目标组ID: {', '.join(rm.target_group_ids)}")
        else:
            cli_logger.info("  角色映射: 无")
        
        if user.user_groups:
            cli_logger.info(f"  用户组ID: {', '.join(user.user_groups)}")
        else:
            cli_logger.info("  用户组ID: 无")
    except AcunetixError as e:
        cli_logger.error(f"获取用户 ID '{args.user_id}' 详情失败: {e}")

def create_user(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """创建新用户"""
    import hashlib # 导入 hashlib 用于密码哈希
    from acunetix_sdk.models.user import UserCreate, RoleMappingCreate
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info(f"正在创建用户: 邮箱='{args.email}', 姓名='{args.first_name} {args.last_name}'")

    role_mappings_data = []
    if args.role_mappings_json:
        try:
            mappings_list = json.loads(args.role_mappings_json)
            if not isinstance(mappings_list, list):
                raise ValueError("角色映射JSON必须是一个列表。")
            for mapping_dict in mappings_list:
                role_mappings_data.append(RoleMappingCreate(**mapping_dict))
        except json.JSONDecodeError:
            cli_logger.error("创建用户失败: 提供的角色映射JSON格式无效。")
            return
        except ValueError as ve:
            cli_logger.error(f"创建用户失败: 角色映射数据错误 - {ve}")
            return
        except Exception as e:
            cli_logger.error(f"创建用户失败: 解析角色映射时出错 - {e}")
            return
    
    # 对密码进行 SHA256 哈希处理
    hashed_password = hashlib.sha256(args.password.encode('utf-8')).hexdigest()
            
    user_data = UserCreate(
        first_name=args.first_name,
        last_name=args.last_name,
        email=args.email,
        password=hashed_password, # 使用哈希后的密码
        role_mappings=role_mappings_data if role_mappings_data else None,
        enabled=args.enabled
    )
    
    try:
        new_user = client.users.create(user_data, send_email=args.send_invite_email)
        cli_logger.info(f"用户创建成功: ID='{new_user.user_id}', 邮箱='{new_user.email}'")
        if args.send_invite_email:
            cli_logger.info("邀请邮件已发送。")
    except AcunetixError as e:
        cli_logger.error(f"创建用户失败: {e}")
    except Exception as e:
        cli_logger.error(f"创建用户时发生意外错误: {e}")

def update_user(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """更新用户信息"""
    from acunetix_sdk.models.user import UserUpdate, RoleMappingCreate
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")

    if not any([args.first_name, args.last_name, args.email, args.role_mappings_json is not None, args.enabled is not None]):
        cli_logger.error("错误: 至少需要提供一个更新参数。")
        return

    cli_logger.info(f"正在更新用户 ID '{args.user_id}'...")
    
    role_mappings_data = None
    if args.role_mappings_json is not None:
        try:
            mappings_list = json.loads(args.role_mappings_json)
            if not isinstance(mappings_list, list):
                raise ValueError("角色映射JSON必须是一个列表。")
            role_mappings_data = [RoleMappingCreate(**mapping_dict) for mapping_dict in mappings_list]
        except json.JSONDecodeError:
            cli_logger.error("更新用户失败: 提供的角色映射JSON格式无效。")
            return
        except ValueError as ve:
            cli_logger.error(f"更新用户失败: 角色映射数据错误 - {ve}")
            return
        except Exception as e:
            cli_logger.error(f"更新用户失败: 解析角色映射时出错 - {e}")
            return

    update_data = UserUpdate(
        first_name=args.first_name,
        last_name=args.last_name,
        email=args.email,
        role_mappings=role_mappings_data,
        enabled=args.enabled
    )
    
    try:
        client.users.update(args.user_id, update_data)
        cli_logger.info(f"用户 ID '{args.user_id}' 的更新请求已发送。正在获取更新后的信息...")
        # 重新获取用户信息以显示更新
        updated_user_info = client.users.get(args.user_id)
        cli_logger.info(f"用户更新成功: ID='{updated_user_info.user_id}', 邮箱='{updated_user_info.email}', "
                        f"姓名: {updated_user_info.first_name} {updated_user_info.last_name}, "
                        f"启用: {'是' if updated_user_info.enabled else '否'}")
    except AcunetixError as e:
        cli_logger.error(f"更新用户 ID '{args.user_id}' 失败: {e}")
    except Exception as e:
        cli_logger.error(f"更新用户时发生意外错误: {e}")

def delete_user(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """删除用户"""
    from acunetix_sdk.errors import AcunetixError
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info(f"正在删除用户 ID: {args.user_id}")
    try:
        client.users.delete(args.user_id)
        cli_logger.info(f"用户 ID '{args.user_id}' 删除成功。")
    except AcunetixError as e:
        cli_logger.error(f"删除用户 ID '{args.user_id}' 失败: {e}")

def register_users_parser(subparsers: argparse._SubParsersAction, parent_parser: argparse.ArgumentParser):
    """注册 users 命令的解析器"""
    users_parser = subparsers.add_parser("users", help="管理用户", parents=[parent_parser])
    users_subparsers = users_parser.add_subparsers(title="操作", dest="action", required=True)

    list_users_parser = users_subparsers.add_parser("list", help="列出所有用户", parents=[parent_parser])
    list_users_parser.add_argument("--limit", type=int, help="限制返回的用户数量")
    list_users_parser.set_defaults(func=list_users)

    get_user_parser = users_subparsers.add_parser("get", help="获取特定用户的详情", parents=[parent_parser])
    get_user_parser.add_argument("user_id", help="要获取详情的用户ID")
    get_user_parser.set_defaults(func=get_user)

    create_user_parser = users_subparsers.add_parser("create", help="创建新用户", parents=[parent_parser])
    create_user_parser.add_argument("email", help="用户邮箱")
    create_user_parser.add_argument("first_name", help="用户名字")
    create_user_parser.add_argument("last_name", help="用户姓氏")
    create_user_parser.add_argument("password", help="用户密码")
    create_user_parser.add_argument("--role_mappings_json", help="角色映射的JSON字符串")
    create_user_parser.add_argument("--enabled", type=lambda x: (str(x).lower() == 'true'), default=True, help="用户是否启用 (true/false, 默认 true)")
    create_user_parser.add_argument("--send_invite_email", action='store_true', help="是否发送邀请邮件给新用户")
    create_user_parser.set_defaults(func=create_user)

    update_user_parser = users_subparsers.add_parser("update", help="更新用户信息", parents=[parent_parser])
    update_user_parser.add_argument("user_id", help="要更新的用户ID")
    update_user_parser.add_argument("--email", help="新的用户邮箱")
    update_user_parser.add_argument("--first_name", help="新的用户名字")
    update_user_parser.add_argument("--last_name", help="新的用户姓氏")
    update_user_parser.add_argument("--role_mappings_json", help="新的角色映射JSON字符串")
    update_user_parser.add_argument("--enabled", type=lambda x: (str(x).lower() == 'true'), help="用户是否启用 (true/false)")
    update_user_parser.set_defaults(func=update_user)

    delete_user_parser = users_subparsers.add_parser("delete", help="删除用户", parents=[parent_parser])
    delete_user_parser.add_argument("user_id", help="要删除的用户ID")
    delete_user_parser.set_defaults(func=delete_user)
