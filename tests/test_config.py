import pytest
import os
import tempfile
import yaml
from src.mcp.config import Config

@pytest.fixture
def temp_config_file():
    with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as f:
        yield f.name
    os.unlink(f.name)

def test_config_initialization(temp_config_file):
    config = Config(temp_config_file)
    assert config.config_path == temp_config_file
    assert isinstance(config.config, dict)
    assert 'fetcher' in config.config
    assert 'parser' in config.config
    assert 'converter' in config.config
    assert 'output' in config.config

def test_config_get_value(temp_config_file):
    config = Config(temp_config_file)
    
    # 测试获取存在的值
    assert config.get('fetcher.headless') is True
    assert isinstance(config.get('fetcher.timeout'), int)
    
    # 测试获取不存在的值
    assert config.get('nonexistent.key') is None
    assert config.get('nonexistent.key', 'default') == 'default'

def test_config_set_value(temp_config_file):
    config = Config(temp_config_file)
    
    # 测试设置新值
    config.set('test.new.key', 'value')
    assert config.get('test.new.key') == 'value'
    
    # 测试更新现有值
    config.set('fetcher.headless', False)
    assert config.get('fetcher.headless') is False
    
    # 验证配置已保存到文件
    with open(temp_config_file, 'r') as f:
        saved_config = yaml.safe_load(f)
        assert saved_config['test']['new']['key'] == 'value'
        assert saved_config['fetcher']['headless'] is False

def test_config_save_and_load(temp_config_file):
    # 创建并保存配置
    config1 = Config(temp_config_file)
    config1.set('test.key', 'test_value')
    
    # 重新加载配置
    config2 = Config(temp_config_file)
    assert config2.get('test.key') == 'test_value'

def test_default_config_creation():
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = os.path.join(temp_dir, 'config.yaml')
        config = Config(config_path)
        
        # 验证默认配置是否已创建
        assert os.path.exists(config_path)
        
        # 验证默认配置内容
        with open(config_path, 'r') as f:
            saved_config = yaml.safe_load(f)
            assert isinstance(saved_config, dict)
            assert all(key in saved_config for key in ['fetcher', 'parser', 'converter', 'output']) 