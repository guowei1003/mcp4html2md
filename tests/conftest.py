import pytest
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 配置pytest异步测试
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "asyncio: mark test as requiring asyncio"
    ) 