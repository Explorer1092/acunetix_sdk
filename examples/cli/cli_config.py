# -*- coding: utf-8 -*-

"""
CLI 配置管理模块
"""

import json
import logging
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

# 配置文件路径
CONFIG_DIR = Path.home() / ".config" / "awvs_cli"
CONFIG_FILE = CONFIG_DIR / "config.json"

# 全局变量，将由 load_config 或 login 命令填充
AWVS_API_URL = None
AWVS_API_KEY = None

def ensure_config_dir_exists():
    """确保配置目录存在"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

def save_config(api_url: str, api_key: str):
    """保存配置到文件"""
    ensure_config_dir_exists()
    config_data = {"AWVS_API_URL": api_url, "AWVS_API_KEY": api_key}
    cli_logger = logging.getLogger("awvs_cli") # 主 CLI logger
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config_data, f, indent=4)
        cli_logger.info(f"配置已保存到: {CONFIG_FILE}")
        # 授予文件适当的权限 (用户读写)
        os.chmod(CONFIG_FILE, 0o600)
    except IOError as e:
        cli_logger.error(f"保存配置文件失败: {e}")
        sys.exit(1)

def load_config():
    """从文件加载配置，如果失败则尝试环境变量"""
    global AWVS_API_URL, AWVS_API_KEY
    cli_logger = logging.getLogger("awvs_cli") # 主 CLI logger
    
    # 尝试从配置文件加载
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                config_data = json.load(f)
            AWVS_API_URL = config_data.get("AWVS_API_URL")
            AWVS_API_KEY = config_data.get("AWVS_API_KEY")
            if AWVS_API_URL and AWVS_API_KEY:
                cli_logger.debug(f"从配置文件加载配置: {CONFIG_FILE}")
                return True
        except (IOError, json.JSONDecodeError) as e:
            cli_logger.warning(f"读取或解析配置文件 {CONFIG_FILE} 失败: {e}. 将尝试环境变量。")

    # 尝试从环境变量加载
    env_api_url = os.environ.get('AWVS_API_URL')
    env_api_key = os.environ.get('AWVS_API_KEY')

    if env_api_url and env_api_key:
        AWVS_API_URL = env_api_url
        AWVS_API_KEY = env_api_key
        cli_logger.debug("从环境变量加载配置。")
        return True
        
    return False

def cli_login(args):
    """处理 login 命令，保存 API URL 和 Key"""
    cli_logger = logging.getLogger("awvs_cli") # 主 CLI logger
    api_url = args.api_url
    api_key = args.api_key

    if not api_url:
        api_url = input("请输入 Acunetix API URL (例如 https://acunetix.example.com): ").strip()
    
    if not api_key:
        # 为了安全，API Key 的输入通常使用 getpass 隐藏
        # import getpass
        # api_key = getpass.getpass("请输入 Acunetix API Key: ").strip()
        # 但为了简单起见，这里暂时使用 input()
        api_key = input("请输入 Acunetix API Key: ").strip()

    if not api_url or not api_key:
        cli_logger.error("错误：API URL 和 API Key 不能为空。")
        return
    
    # 简单验证一下 URL
    parsed_url = urlparse(api_url)
    if not parsed_url.scheme or not parsed_url.netloc:
        cli_logger.error(f"错误：提供的 AWVS_API_URL '{api_url}' 格式无效。应为例如 'https://acunetix.example.com'")
        return

    save_config(api_url, api_key) # save_config 内部会使用 cli_logger
    cli_logger.info("登录信息已保存。后续命令将使用这些凭据。")

def register_login_parser(subparsers, parent_parser):
    """注册 login 命令的解析器"""
    login_parser = subparsers.add_parser(
        "login", 
        help="保存 API URL 和 API Key 以供后续使用。如果未提供参数，将提示输入。", 
        parents=[parent_parser]
    )
    login_parser.add_argument("--api_url", default=None, help="Acunetix API URL (例如 https://acunetix.example.com)")
    login_parser.add_argument("--api_key", default=None, help="Acunetix API Key")
    login_parser.set_defaults(func=lambda args_ns: cli_login(args_ns)) # 包装以匹配 (client, args) 签名，尽管 login 不需要 client
