# -*- coding: utf-8 -*-

"""
CLI 辅助函数模块
"""

import json
import logging
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from acunetix_sdk.models.issue_tracker import IssueTrackerConfig
    from acunetix_sdk.models.waf import WAFConfig


def parse_issue_tracker_config_from_json_file(filepath: str) -> Optional['IssueTrackerConfig']:
    """从 JSON 文件解析 IssueTrackerConfig"""
    # 导入移到函数内部，以避免在模块加载时因 sys.path 问题而失败
    # 主 CLI 文件应确保 acunetix_sdk 在 sys.path 中
    from acunetix_sdk.models.issue_tracker import IssueTrackerConfig
    cli_logger = logging.getLogger("awvs_cli")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            config_dict = json.load(f)
        return IssueTrackerConfig(**config_dict)
    except FileNotFoundError:
        cli_logger.error(f"配置文件 '{filepath}' 未找到。")
        return None
    except json.JSONDecodeError:
        cli_logger.error(f"配置文件 '{filepath}' 格式无效。")
        return None
    except Exception as e: 
        cli_logger.error(f"解析配置文件 '{filepath}' 时出错: {e}")
        return None

def parse_waf_config_from_json_file(filepath: str) -> Optional['WAFConfig']:
    """从 JSON 文件解析 WAFConfig"""
    from acunetix_sdk.models.waf import WAFConfig
    cli_logger = logging.getLogger("awvs_cli")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            config_dict = json.load(f)
        return WAFConfig(**config_dict)
    except FileNotFoundError:
        cli_logger.error(f"配置文件 '{filepath}' 未找到。")
        return None
    except json.JSONDecodeError:
        cli_logger.error(f"配置文件 '{filepath}' 格式无效。")
        return None
    except Exception as e: 
        cli_logger.error(f"解析配置文件 '{filepath}' 时出错: {e}")
        return None

def parse_exclusion_matrix(matrix_str: str) -> Optional[List[bool]]:
    """解析排除矩阵 JSON 字符串"""
    cli_logger = logging.getLogger("awvs_cli")
    try:
        matrix = json.loads(matrix_str)
        if not isinstance(matrix, list) or len(matrix) != 168 or not all(isinstance(x, bool) for x in matrix):
            cli_logger.error("排除矩阵必须是一个包含168个布尔值的JSON数组。")
            return None
        return matrix
    except json.JSONDecodeError:
        cli_logger.error("排除矩阵JSON格式无效。")
        return None
    except Exception as e:
        cli_logger.error(f"解析排除矩阵时出错: {e}")
        return None
