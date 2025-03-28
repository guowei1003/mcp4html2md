from typing import Dict, Any, Callable, List, Optional
import importlib.util
import os
from pathlib import Path

class Plugin:
    def __init__(self, name: str, description: str):
        """
        插件基类
        :param name: 插件名称
        :param description: 插件描述
        """
        self.name = name
        self.description = description
        
    async def process_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理内容
        :param content: 内容数据
        :return: 处理后的内容数据
        """
        raise NotImplementedError()

class PluginManager:
    def __init__(self, plugin_dir: Optional[str] = None):
        """
        初始化插件管理器
        :param plugin_dir: 插件目录路径
        """
        self.plugin_dir = plugin_dir or os.path.join(os.path.dirname(__file__), 'plugins')
        self.plugins = {}
        
        # 注册内置插件
        from .plugins.image_processor import ImageProcessor
        from .plugins.image_downloader import ImageDownloader
        
        self.register_plugin(ImageProcessor('image_processor', '处理图片链接'))
        self.register_plugin(ImageDownloader('image_downloader', '下载图片到本地'))
        
        self._load_plugins()
        
    def _default_plugin_dir(self) -> str:
        """获取默认插件目录路径"""
        return os.path.join(str(Path.home()), '.mcp', 'plugins')
        
    def _load_plugins(self):
        """加载插件目录中的所有插件"""
        if not os.path.exists(self.plugin_dir):
            return
            
        for filename in os.listdir(self.plugin_dir):
            if filename.endswith('.py') and not filename.startswith('__'):
                self._load_plugin(os.path.join(self.plugin_dir, filename))
                
    def _load_plugin(self, filepath: str) -> None:
        """
        从文件加载插件
        :param filepath: 插件文件路径
        """
        try:
            spec = importlib.util.spec_from_file_location("plugin", filepath)
            if spec is None or spec.loader is None:
                return
                
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 查找并实例化插件类
            for item in dir(module):
                obj = getattr(module, item)
                if isinstance(obj, type) and issubclass(obj, Plugin) and obj != Plugin:
                    plugin = obj(item.lower(), '')
                    self.register_plugin(plugin)
                    
        except Exception as e:
            print(f"加载插件 {filepath} 失败: {e}")
            
    def get_plugin(self, name: str) -> Optional[Plugin]:
        """
        获取指定名称的插件
        :param name: 插件名称
        :return: 插件实例
        """
        return self.plugins.get(name)
        
    def list_plugins(self) -> List[Dict[str, str]]:
        """
        列出所有已加载的插件
        :return: 插件信息列表
        """
        return [
            {'name': name, 'description': plugin.description}
            for name, plugin in self.plugins.items()
        ]
        
    async def process_content(self, content: Dict[str, Any], plugin_name: str) -> Dict[str, Any]:
        """
        使用指定插件处理内容
        :param content: 内容数据
        :param plugin_name: 插件名称
        :return: 处理后的内容数据
        """
        plugin = self.get_plugin(plugin_name)
        if plugin is None:
            raise ValueError(f"插件 {plugin_name} 未找到")
            
        return await plugin.process_content(content)
        
    async def process_content_chain(self, content: Dict[str, Any], plugin_names: List[str]) -> Dict[str, Any]:
        """
        使用插件链处理内容
        :param content: 内容数据
        :param plugin_names: 插件名称列表
        :return: 处理后的内容数据
        """
        result = content
        for plugin_name in plugin_names:
            result = await self.process_content(result, plugin_name)
        return result

    def register_plugin(self, plugin: Plugin):
        """
        注册插件
        :param plugin: 插件实例
        """
        self.plugins[plugin.name] = plugin 