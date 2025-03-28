from typing import Dict, Any, Optional
import yaml
import os
from pathlib import Path

class Config:
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置管理器
        :param config_path: 配置文件路径
        """
        self.config_path = config_path or self._default_config_path()
        self.config = self._load_config()
        
    def _default_config_path(self) -> str:
        """获取默认配置文件路径"""
        return os.path.join(str(Path.home()), '.mcp', 'config.yaml')
        
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        config = {}
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f) or {}
                
        # 如果配置为空或不存在，使用默认配置
        if not config:
            config = self._create_default_config()
            
        return config
            
    def _create_default_config(self) -> Dict[str, Any]:
        """创建默认配置"""
        config = {
            'fetcher': {
                'headless': True,
                'timeout': 30,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            },
            'parser': {
                'rules_path': os.path.join(str(Path.home()), '.mcp', 'rules'),
                'default_format': 'markdown'
            },
            'converter': {
                'template_path': os.path.join(str(Path.home()), '.mcp', 'templates'),
                'default_template': 'default.md'
            },
            'output': {
                'path': os.path.join(str(Path.home()), 'Documents', 'mcp-output'),
                'filename_template': '{title}-{date}'
            }
        }
        
        # 确保配置目录存在
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        
        # 保存默认配置
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(config, f, allow_unicode=True)
            
        return config
        
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        :param key: 配置键，支持点号分隔的路径
        :param default: 默认值
        :return: 配置值
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
                
        return value if value is not None else default
        
    def set(self, key: str, value: Any) -> None:
        """
        设置配置值
        :param key: 配置键，支持点号分隔的路径
        :param value: 配置值
        """
        keys = key.split('.')
        config = self.config
        
        # 遍历到最后一个键之前
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
            
        # 设置最后一个键的值
        config[keys[-1]] = value
        
        # 保存配置
        self.save()
        
    def save(self) -> None:
        """保存配置到文件"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(self.config, f, allow_unicode=True) 