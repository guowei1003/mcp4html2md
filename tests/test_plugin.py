import pytest
import os
import tempfile
from src.mcp.plugin import Plugin, PluginManager

@pytest.fixture
def temp_plugin_dir():
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建测试插件文件
        plugin_content = '''
from src.mcp.plugin import Plugin

class TestPlugin(Plugin):
    """测试插件"""
    async def process_content(self, content):
        content['processed_by'] = self.name
        return content
'''
        plugin_path = os.path.join(temp_dir, 'test_plugin.py')
        with open(plugin_path, 'w') as f:
            f.write(plugin_content)
        yield temp_dir

def test_plugin_manager_initialization(temp_plugin_dir):
    manager = PluginManager(temp_plugin_dir)
    assert isinstance(manager.plugins, dict)
    assert 'testplugin' in manager.plugins

@pytest.mark.asyncio
async def test_plugin_loading(temp_plugin_dir):
    manager = PluginManager(temp_plugin_dir)
    plugin = manager.get_plugin('testplugin')
    assert plugin is not None
    assert plugin.name == 'testplugin'
    assert isinstance(plugin, Plugin)

def test_plugin_list(temp_plugin_dir):
    manager = PluginManager(temp_plugin_dir)
    plugins = manager.list_plugins()
    assert len(plugins) == 3
    plugin_names = [p['name'] for p in plugins]
    assert 'testplugin' in plugin_names
    assert 'image_processor' in plugin_names
    assert 'image_downloader' in plugin_names

@pytest.mark.asyncio
async def test_plugin_processing(temp_plugin_dir):
    manager = PluginManager(temp_plugin_dir)
    content = {'test': 'data'}
    processed = await manager.process_content(content, 'testplugin')
    assert processed['processed_by'] == 'testplugin'
    assert processed['test'] == 'data'

@pytest.mark.asyncio
async def test_plugin_chain_processing(temp_plugin_dir):
    # 创建第二个测试插件
    plugin2_content = '''
from src.mcp.plugin import Plugin

class TestPlugin2(Plugin):
    """测试插件2"""
    async def process_content(self, content):
        content['processed_by_2'] = self.name
        return content
'''
    plugin2_path = os.path.join(temp_plugin_dir, 'test_plugin2.py')
    with open(plugin2_path, 'w') as f:
        f.write(plugin2_content)
        
    manager = PluginManager(temp_plugin_dir)
    content = {'test': 'data'}
    processed = await manager.process_content_chain(content, ['testplugin', 'testplugin2'])
    assert processed['processed_by'] == 'testplugin'
    assert processed['processed_by_2'] == 'testplugin2'
    assert processed['test'] == 'data'

@pytest.mark.asyncio
async def test_invalid_plugin(temp_plugin_dir):
    manager = PluginManager(temp_plugin_dir)
    content = {'test': 'data'}
    with pytest.raises(ValueError):
        await manager.process_content(content, 'nonexistent_plugin') 