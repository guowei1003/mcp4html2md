import logging
import os
from pathlib import Path
from typing import Optional
from datetime import datetime

def setup_logger(name: str = 'convert', log_file: Optional[str] = None) -> logging.Logger:
    """
    设置日志记录器
    :param name: 日志记录器名称
    :param log_file: 日志文件路径，如果为None则使用默认路径
    :return: 配置好的日志记录器
    """
    # 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # 如果已经有处理器，先移除旧的处理器
    if logger.handlers:
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)
        
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器
    if log_file is None:
        log_dir = os.path.join(str(Path.home()), '.convert', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        date_str = datetime.now().strftime('%Y%m%d')
        log_file = os.path.join(log_dir, f'convert_{date_str}.log')
        
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

# 创建默认日志记录器
logger = setup_logger() 