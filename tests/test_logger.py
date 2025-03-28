import pytest
import logging
import os
import tempfile
from src.convert.logger import setup_logger

def test_logger_initialization():
    logger = setup_logger('test_logger')
    assert isinstance(logger, logging.Logger)
    assert logger.name == 'test_logger'
    assert logger.level == logging.DEBUG
    
    # 验证处理器
    assert len(logger.handlers) == 2
    handlers = logger.handlers
    assert any(isinstance(h, logging.StreamHandler) for h in handlers)
    assert any(isinstance(h, logging.FileHandler) for h in handlers)
    
    # 验证日志级别
    stream_handler = next(h for h in handlers if isinstance(h, logging.StreamHandler))
    file_handler = next(h for h in handlers if isinstance(h, logging.FileHandler))
    assert stream_handler.level == logging.INFO
    assert file_handler.level == logging.DEBUG

def test_logger_with_custom_file():
    with tempfile.NamedTemporaryFile(suffix='.log', delete=False) as temp_file:
        log_path = temp_file.name
        
    try:
        logger = setup_logger('test_logger', log_path)
        
        # 写入测试日志
        test_message = "Test log message"
        logger.info(test_message)
        
        # 确保日志被写入文件
        for handler in logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.flush()
        
        # 验证日志文件内容
        with open(log_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert test_message in content
            
    finally:
        # 关闭所有处理器
        logger.handlers.clear()
        os.unlink(log_path)

def test_logger_reuse():
    """测试重复调用setup_logger不会创建重复的处理器"""
    logger1 = setup_logger('test_logger')
    handlers_count = len(logger1.handlers)
    
    # 再次获取同名logger
    logger2 = setup_logger('test_logger')
    assert logger2 is logger1  # 应该是同一个logger实例
    assert len(logger2.handlers) == handlers_count  # 处理器数量应该保持不变

def test_logger_formatting():
    with tempfile.NamedTemporaryFile(suffix='.log', delete=False) as temp_file:
        log_path = temp_file.name
        
    try:
        logger = setup_logger('test_logger', log_path)
        
        # 测试不同级别的日志
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        
        # 验证日志格式
        with open(log_path, 'r', encoding='utf-8') as f:
            content = f.readlines()
            
            for line in content:
                # 验证时间戳格式
                assert ' - test_logger - ' in line
                # 验证日志级别
                assert any(level in line for level in ['DEBUG', 'INFO', 'WARNING', 'ERROR'])
                # 验证消息
                assert any(msg in line for msg in [
                    "Debug message",
                    "Info message",
                    "Warning message",
                    "Error message"
                ])
                
    finally:
        os.unlink(log_path) 