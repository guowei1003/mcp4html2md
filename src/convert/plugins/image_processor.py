from typing import Dict, Any
from convert.plugin import Plugin
import re
from urllib.parse import urljoin

class ImageProcessor(Plugin):
    """图片处理插件：处理内容中的图片链接，支持相对路径转绝对路径等功能"""
    
    async def process_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理内容中的图片
        :param content: 内容数据
        :return: 处理后的内容数据
        """
        base_url = content.get('url', '')
        
        # 处理内容块中的图片
        for block in content.get('content', []):
            if isinstance(block, dict):
                html = block.get('html', '')
                if html:
                    # 处理图片链接
                    block['html'] = self._process_image_links(html, base_url)
                    
                    # 如果是Markdown内容，也处理Markdown中的图片
                    if block.get('type') == 'markdown':
                        block['content'] = self._process_markdown_images(
                            block.get('content', ''), 
                            base_url
                        )
                        
        return content
        
    def _process_image_links(self, html: str, base_url: str) -> str:
        """处理HTML中的图片链接"""
        def replace_src(match):
            src = match.group(1)
            if not src.startswith(('http://', 'https://', 'data:')):
                # 如果以斜杠开头，直接拼接到域名
                if src.startswith('/'):
                    base = re.match(r'https?://[^/]+', base_url)
                    if base:
                        src = base.group(0) + src
                else:
                    # 相对路径，拼接到当前路径
                    src = urljoin(base_url.rstrip('/') + '/', src)
            return f'src="{src}"'
            
        return re.sub(r'src="([^"]+)"', replace_src, html)
        
    def _process_markdown_images(self, markdown: str, base_url: str) -> str:
        """处理Markdown中的图片链接"""
        def replace_link(match):
            alt = match.group(1)
            src = match.group(2)
            if not src.startswith(('http://', 'https://', 'data:')):
                # 如果以斜杠开头，直接拼接到域名
                if src.startswith('/'):
                    base = re.match(r'https?://[^/]+', base_url)
                    if base:
                        src = base.group(0) + src
                else:
                    # 相对路径，拼接到当前路径
                    src = urljoin(base_url.rstrip('/') + '/', src)
            return f'![{alt}]({src})'
            
        return re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', replace_link, markdown) 