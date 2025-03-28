from src.convert.plugin import Plugin

class TestPlugin(Plugin):
    """测试插件"""
    async def process_content(self, content):
        content['processed_by'] = self.name
        return content 