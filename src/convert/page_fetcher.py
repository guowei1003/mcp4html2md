from typing import Tuple
from playwright.async_api import async_playwright
import asyncio
from urllib.parse import urlparse

class PageFetcher:
    def __init__(self, headless: bool = True):
        """
        初始化浏览器实例
        :param headless: 是否启用无头模式
        """
        self.headless = headless
        self._browser = None
        self._context = None
        
    async def __aenter__(self):
        """异步上下文管理器入口"""
        playwright = await async_playwright().start()
        self._browser = await playwright.chromium.launch(headless=self.headless)
        self._context = await self._browser.new_context()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器退出"""
        if self._context:
            await self._context.close()
        if self._browser:
            await self._browser.close()
            
    async def fetch(self, url: str, wait_for: str = "load") -> Tuple[str, str]:
        """
        获取网页完整内容
        :param url: 目标URL
        :param wait_for: 等待事件类型 ("load", "domcontentloaded", "networkidle")
        :return: (HTML内容, 最终URL)
        """
        if not self._context:
            raise RuntimeError("PageFetcher must be used as an async context manager")
            
        page = await self._context.new_page()
        try:
            # 设置用户代理
            await page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            
            # 访问页面并等待加载
            response = await page.goto(url, wait_until=wait_for, timeout=60000)
            if not response:
                raise Exception(f"Failed to load {url}")
            if response.status >= 400:
                raise Exception(f"HTTP {response.status} error for {url}")
                
            # 等待页面稳定
            await page.wait_for_load_state("networkidle", timeout=60000)
            
            # 获取内容
            html = await page.content()
            final_url = page.url
            
            return html, final_url
            
        finally:
            await page.close()
            
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """
        验证URL是否有效
        :param url: 待验证的URL
        :return: 布尔值
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False 