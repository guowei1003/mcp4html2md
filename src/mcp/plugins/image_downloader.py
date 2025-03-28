import os
import re
import time
import random
import aiohttp
import asyncio
from pathlib import Path
from typing import Dict, Any, Tuple, List
from urllib.parse import urljoin, urlparse
from mcp.plugin import Plugin
from mcp.logger import logger

class ImageDownloader(Plugin):
    """图片下载插件：下载文档中的图片到本地并更新链接"""
    
    def __init__(self, name: str, description: str):
        """
        初始化图片下载插件
        :param name: 插件名称
        :param description: 插件描述
        """
        super().__init__(name, description)
        self.image_dir = os.path.join(os.getcwd(), 'images')
        
    async def process_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理内容中的图片
        :param content: 内容数据
        :return: 处理后的内容数据
        """
        logger.info("开始处理文档中的图片")
        os.makedirs(self.image_dir, exist_ok=True)
        logger.info(f"图片下载目录: {self.image_dir}")
        base_url = content.get('url', '')
        logger.debug(f"文档基础URL: {base_url}")
        
        # 收集所有需要下载的图片URL
        image_urls = set()
        
        # 处理内容块中的图片
        for block in content.get('content', []):
            if isinstance(block, dict):
                html = block.get('html', '')
                if html:
                    # 从HTML中提取图片URL
                    urls = self._extract_image_urls(html)
                    logger.debug(f"从HTML中提取到的图片URL: {urls}")
                    image_urls.update(self._normalize_urls(urls, base_url))
                    
                    # 如果是Markdown内容，也处理Markdown中的图片
                    if block.get('type') == 'markdown':
                        markdown_content = block.get('content', '')
                        urls = self._extract_markdown_image_urls(markdown_content)
                        logger.debug(f"从Markdown中提取到的图片URL: {urls}")
                        image_urls.update(self._normalize_urls(urls, base_url))
        
        if not image_urls:
            logger.info("文档中没有找到需要下载的图片")
            return content
            
        logger.info(f"找到 {len(image_urls)} 个需要下载的图片")
        
        # 下载图片并获取新的本地路径
        url_mapping = await self._download_images(list(image_urls))
        
        # 更新内容中的图片链接
        logger.info("开始更新文档中的图片链接")
        for block in content.get('content', []):
            if isinstance(block, dict):
                html = block.get('html', '')
                if html:
                    block['html'] = self._replace_image_urls(html, url_mapping)
                    
                    if block.get('type') == 'markdown':
                        markdown_content = block.get('content', '')
                        block['content'] = self._replace_markdown_image_urls(
                            markdown_content, 
                            url_mapping
                        )
        
        # 添加图片信息到内容中
        if url_mapping:
            content['images'] = [
                {'original_url': url, 'local_path': path}
                for url, path in url_mapping.items()
            ]
            logger.info(f"成功处理 {len(url_mapping)} 个图片")
            
        return content
        
    def _extract_image_urls(self, html: str) -> List[str]:
        """从HTML中提取图片URL"""
        urls = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', html)
        logger.debug(f"从HTML中提取到 {len(urls)} 个图片URL")
        return urls
        
    def _extract_markdown_image_urls(self, markdown: str) -> List[Tuple[str, str]]:
        """
        从Markdown中提取图片URL
        :param markdown: Markdown文本
        :return: (alt_text, url) 元组列表
        """
        # 匹配 ![alt](url "title") 或 ![alt](url) 格式
        urls = re.findall(r'!\[([^\]]*)\]\(([^)"\']+)(?:\s+"[^"]*")?\)', markdown)
        logger.debug(f"从Markdown中提取到 {len(urls)} 个图片URL")
        return urls
        
    def _normalize_urls(self, urls: List[str], base_url: str) -> List[str]:
        """标准化URL列表"""
        normalized = []
        for url in urls:
            # 如果是Markdown格式的URL，取第二个元素（URL部分）
            if isinstance(url, tuple):
                url = url[1]
                
            if url.startswith(('http://', 'https://')):
                normalized.append(url)
            elif url.startswith('data:'):
                logger.debug(f"跳过data URL: {url[:50]}...")
                continue
            else:
                normalized_url = urljoin(base_url, url)
                logger.debug(f"标准化URL: {url} -> {normalized_url}")
                normalized.append(normalized_url)
        return normalized
        
    async def _download_images(self, urls: List[str]) -> Dict[str, str]:
        """
        异步下载图片
        :param urls: 图片URL列表
        :return: 原始URL到本地路径的映射
        """
        async def download_image(session: aiohttp.ClientSession, url: str) -> Tuple[str, str]:
            try:
                logger.debug(f"开始下载图片: {url}")
                response = await session.get(url)
                if response.status == 200:
                    # 生成本地文件名
                    timestamp = int(time.time() * 1000)
                    random_num = random.randint(1000, 9999)
                    ext = self._get_extension(url, response.headers.get('content-type', ''))
                    filename = f'img_{timestamp}_{random_num}{ext}'
                    filepath = os.path.join(self.image_dir, filename)
                    
                    # 保存文件
                    content = await response.read()
                    with open(filepath, 'wb') as f:
                        f.write(content)
                        
                    logger.info(f"成功下载图片: {url} -> {filename}")
                    # 返回相对路径
                    return url, os.path.join('images', filename)
                else:
                    logger.error(f"下载图片失败: {url}, 状态码: {response.status}")
            except Exception as e:
                logger.error(f"下载图片出错 {url}: {str(e)}")
            return url, url
            
        logger.info(f"开始下载 {len(urls)} 个图片")
        async with aiohttp.ClientSession() as session:
            tasks = [download_image(session, url) for url in urls]
            results = await asyncio.gather(*tasks)
            return dict(results)
            
    def _get_extension(self, url: str, content_type: str) -> str:
        """获取图片扩展名"""
        # 先从URL中尝试获取
        path = urlparse(url).path
        ext = os.path.splitext(path)[1].lower()
        if ext in ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg'):
            return ext
            
        # 从content-type中获取
        content_type = content_type.lower()
        if 'jpeg' in content_type or 'jpg' in content_type:
            ext = '.jpg'
        elif 'png' in content_type:
            ext = '.png'
        elif 'gif' in content_type:
            ext = '.gif'
        elif 'webp' in content_type:
            ext = '.webp'
        elif 'svg' in content_type:
            ext = '.svg'
        else:
            # 检查内容类型中是否包含图片格式信息
            if 'image/' in content_type:
                # 从 content-type 中提取格式
                format_match = re.search(r'image/([a-zA-Z0-9]+)', content_type)
                if format_match:
                    ext = f'.{format_match.group(1).lower()}'
                else:
                    ext = '.jpg'  # 默认使用.jpg
            else:
                ext = '.jpg'  # 默认使用.jpg
            
        logger.debug(f"确定图片扩展名: {url} -> {ext} (content-type: {content_type})")
        return ext
        
    def _replace_image_urls(self, html: str, url_mapping: Dict[str, str]) -> str:
        """替换HTML中的图片URL"""
        for old_url, new_path in url_mapping.items():
            html = re.sub(
                f'src=["\']({re.escape(old_url)})["\']',
                f'src="{new_path}"',
                html
            )
            logger.debug(f"替换HTML图片URL: {old_url} -> {new_path}")
        return html
        
    def _replace_markdown_image_urls(self, markdown: str, url_mapping: Dict[str, str]) -> str:
        """替换Markdown中的图片URL"""
        for old_url, new_path in url_mapping.items():
            markdown = re.sub(
                f'\\]\\({re.escape(old_url)}\\)',
                f']({new_path})',
                markdown
            )
            logger.debug(f"替换Markdown图片URL: {old_url} -> {new_path}")
        return markdown 