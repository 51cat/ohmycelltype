import re
import json
import pandas as pd

import logging
from functools import wraps
import time
from datetime import timedelta
import sys


def execute_task(func, params_dict):
    """
    执行传入的函数并返回执行状态。
    
    Args:
        func: 要执行的目标函数
        params_dict: 字典格式的参数
        
    Returns:
        tuple: (bool, any) 
               第一个元素是是否成功 (True/False)，
               第二个元素是函数的返回值或捕获到的异常对象。
    """
    try:
        # 使用 ** 将字典解包为关键字参数
        result = func(**params_dict)
        return True, result
    except Exception as e:
        # 捕获执行过程中的任何异常
        return False, e

def extract_and_validate_json(text, required_keys=None):
    """
    从文本中提取 JSON 并校验。
    :param text: AI 返回的原始文本
    :param required_keys: 列表类型，可选。如果提供，将校验这些字段是否存在。
    :return: 成功返回字典，失败或字段不全返回 None。
    """
    # 1. 嗅探：找最外层的 { ... }
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if not match:
        return None
    
    try:
        # 2. 解析
        data = json.loads(match.group())
        
        # 3. 校验：只有在给了 required_keys 时才执行字段检查
        if required_keys:
            # 确保 data 是字典且包含所有必要字段
            if isinstance(data, dict) and all(key in data for key in required_keys):
                return data
            else:
                return None  # 字段不全，继续潜伏
        
        # 如果没给 required_keys，只要是合法 JSON 就放行
        return data
            
    except (json.JSONDecodeError, TypeError):
        return None


def parse_response(response):
    if isinstance(response, dict):
        return response
    # --------------------------

    if not response or not isinstance(response, str):
        return None

    code_block_pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
    code_match = re.search(code_block_pattern, response)
    
    if code_match:
        content = code_match.group(1).strip()
    else:
        json_pattern = r"(\{[\s\S]*\})"
        json_match = re.search(json_pattern, response)
        content = json_match.group(1).strip() if json_match else None

    if not content:
        return None

    try:
        return json.loads(content)
    except (json.JSONDecodeError, TypeError):
        return None

def get_table_context(file_path):
    try:
        df = pd.read_csv(file_path)
        
        table_head_str = df.head(10).to_csv(index=False)
        
        column_info = df.dtypes.apply(lambda x: x.name).to_dict()
        
        context = {
            "Table_Head": table_head_str,
            "Column_Info": column_info
        }
        
        return json.dumps(context, indent=4, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)



def add_log(func):
    logFormatter = logging.Formatter(
        '[%(levelname)s][%(asctime)s] %(name)s %(message)s'
    )

    # 创建一个日志器
    logger = logging.getLogger(
        f'{func.__module__}.{func.__name__}'
    )
    
    # 设置日志级别
    logger.setLevel(logging.INFO)

    # 创建一个控制台处理器
    consoleHandler = logging.StreamHandler(sys.stderr)
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)

    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info('start...')
        start = time.time()

        result = func(*args, **kwargs)
    
        end = time.time()
        used = timedelta(seconds=end - start)
        logger.info('done. time used: %s', used)
        
        return result

    wrapper.logger = logger
    return wrapper