# -*- coding: utf-8 -*-

"""
CLI 命令 - Agents Config 模块
"""

import logging
import argparse # 用于类型提示
from typing import TYPE_CHECKING

# 仅在类型检查时导入，用于类型提示，避免循环依赖
if TYPE_CHECKING:
    from acunetix_sdk.client_sync import AcunetixSyncClient
    from acunetix_sdk.models.agent import AgentRegistrationToken, NewAgentRegistrationToken
    from acunetix_sdk.errors import AcunetixError

def get_agents_config(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """获取全局代理配置"""
    from acunetix_sdk.errors import AcunetixError # 运行时导入
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info("正在获取全局代理配置...")
    try:
        config = client.agents_config.get()
        cli_logger.info("全局代理配置:")
        cli_logger.info(f"  自动更新: {'是' if config.auto_update else '否'}")
        cli_logger.info(f"  类型: {config.type or 'N/A'}")
    except AcunetixError as e:
        cli_logger.error(f"获取全局代理配置失败: {e}")

# def update_agents_config(client: 'AcunetixSyncClient', args: argparse.Namespace):
#     """更新全局代理配置"""
#     from acunetix_sdk.models.agent import AgentsConfig # AgentsConfig 仅在此注释掉的函数中使用
#     from acunetix_sdk.errors import AcunetixError
#     cli_logger = logging.getLogger("awvs_cli")
#     cli_logger.info("正在更新全局代理配置...")
#     
#     update_data = {}
#     if args.auto_update is not None:
#         update_data['auto_update'] = args.auto_update
#     if args.type is not None:
#         update_data['type'] = args.type
#         
#     if not update_data:
#         cli_logger.error("错误: 未提供任何更新参数 (--auto_update, --type)。")
#         return
# 
#     config_payload = AgentsConfig(**update_data)
# 
#     try:
#         updated_config = client.agents_config.update(config_payload) # SDK 中不存在此方法
#         cli_logger.info("全局代理配置更新成功。")
#         cli_logger.info(f"  自动更新: {'是' if updated_config.auto_update else '否'}")
#         cli_logger.info(f"  类型: {updated_config.type or 'N/A'}")
#     except AcunetixError as e:
#         cli_logger.error(f"更新全局代理配置失败: {e}")
#     except AttributeError:
#         cli_logger.error("更新全局代理配置失败: SDK 中可能尚未实现 'client.agents_config.update()' 方法或API不支持此操作。")

def get_agent_registration_token(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """获取当前的代理注册令牌"""
    from acunetix_sdk.errors import AcunetixError # 运行时导入
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info("正在获取当前的代理注册令牌...")
    try:
        token_info = client.agents_config.get_registration_token() # SDK 方法返回 AgentRegistrationToken
        if not token_info or not token_info.token: # 检查 token_info 本身以及其 token 属性
            cli_logger.info("未找到当前的代理注册令牌或令牌无效。")
            return
    except AcunetixError as e:
        # 如果是 404，则视为不存在令牌，输出信息而非报错
        if getattr(e, "status_code", None) == 404:
            cli_logger.info("未找到当前的代理注册令牌。")
        else:
            cli_logger.error(f"获取代理注册令牌失败: {e}")
    else:
        cli_logger.info("当前的代理注册令牌:")
        cli_logger.info(f"  令牌: {token_info.token}")
        cli_logger.info(f"    描述: {token_info.description or 'N/A'}")
        cli_logger.info(f"    创建日期: {token_info.created or 'N/A'}")

def create_agent_registration_token(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """创建或生成新的代理注册令牌"""
    from acunetix_sdk.models.agent import NewAgentRegistrationToken # 运行时导入
    from acunetix_sdk.errors import AcunetixError # 运行时导入
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info(f"正在创建/生成代理注册令牌: 描述='{args.description}'")
    
    token_data = NewAgentRegistrationToken(description=args.description)
    
    try:
        new_token_info = client.agents_config.generate_registration_token(token_data) # SDK 方法返回 AgentRegistrationToken
        cli_logger.info("代理注册令牌创建/生成成功:")
        cli_logger.info(f"  令牌: {new_token_info.token}")
        cli_logger.info(f"  描述: {new_token_info.description or 'N/A'}")
        cli_logger.info(f"  创建日期: {new_token_info.created or 'N/A'}")
    except AcunetixError as e:
        cli_logger.error(f"创建/生成代理注册令牌失败: {e}")
    except AttributeError:
        cli_logger.error("创建/生成代理注册令牌失败: SDK 中 'client.agents_config.generate_registration_token()' 方法调用方式可能不正确。")

def delete_agent_registration_token(client: 'AcunetixSyncClient', args: argparse.Namespace):
    """删除当前的代理注册令牌"""
    from acunetix_sdk.errors import AcunetixError # 运行时导入
    cli_logger = logging.getLogger("awvs_cli")
    cli_logger.info("正在删除当前的代理注册令牌...")
    try:
        client.agents_config.delete_registration_token()
        cli_logger.info("当前的代理注册令牌删除成功。")
    except AcunetixError as e:
        # 404 表示令牌不存在，视为已删除
        if getattr(e, "status_code", None) == 404:
            cli_logger.info("无需删除，当前不存在代理注册令牌。")
        else:
            cli_logger.error(f"删除当前的代理注册令牌失败: {e}")

def register_agents_config_parser(subparsers: argparse._SubParsersAction, parent_parser: argparse.ArgumentParser):
    """注册 agents_config 命令的解析器"""
    agents_config_parser = subparsers.add_parser("agents_config", help="管理全局代理配置和注册令牌", parents=[parent_parser])
    agents_config_subparsers = agents_config_parser.add_subparsers(title="操作", dest="action", required=True)

    get_config_parser = agents_config_subparsers.add_parser("get", help="获取全局代理配置", parents=[parent_parser])
    get_config_parser.set_defaults(func=get_agents_config)

    # update_config_parser = agents_config_subparsers.add_parser("update", help="更新全局代理配置 (当前功能因SDK/API限制已禁用)", parents=[parent_parser])
    # update_config_parser.add_argument("--auto_update", type=lambda x: (str(x).lower() == 'true'), help="是否启用自动更新 (true/false)")
    # update_config_parser.add_argument("--type", help="代理配置类型 (具体可选值未知)")
    # update_config_parser.set_defaults(func=update_agents_config)

    get_token_parser = agents_config_subparsers.add_parser("get_token", help="获取当前的代理注册令牌", parents=[parent_parser]) # 重命名 list_tokens to get_token
    get_token_parser.set_defaults(func=get_agent_registration_token) # 更新函数引用

    create_token_parser = agents_config_subparsers.add_parser("create_token", help="创建或生成新的代理注册令牌", parents=[parent_parser]) # 更新帮助文本
    create_token_parser.add_argument("--description", help="令牌描述", default="")
    create_token_parser.set_defaults(func=create_agent_registration_token)

    delete_token_parser = agents_config_subparsers.add_parser("delete_token", help="删除当前的代理注册令牌", parents=[parent_parser]) # 更新帮助文本
    # delete_token_parser.add_argument("token", help="要删除的令牌字符串") # 移除 token 参数
    delete_token_parser.set_defaults(func=delete_agent_registration_token)
