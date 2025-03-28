import os
import asyncio
import tempfile
from typing import Optional, List
from mcp.server.fastmcp import FastMCP
from convert import PageFetcher, ContentParser, MarkdownConverter, PluginManager

mcp = FastMCP("html-convert-md")

async def _convert_html_to_markdown(input_content: str, is_url: bool = False, include_images: bool = True) -> str:
    """使用项目中的功能直接转换HTML/URL为Markdown
    
    Args:
        input_content: 输入内容（URL或HTML内容）
        is_url: 是否为URL
        include_images: 是否包含图片
    
    Returns:
        转换后的Markdown文本
    """
    try:
        content = None
        plugin_list = ["image_downloader"] if include_images else []
        plugin_manager = PluginManager()
        
        # 处理URL
        if is_url:
            if not PageFetcher.is_valid_url(input_content):
                return f"转换失败: 无效的URL: {input_content}"
                
            async with PageFetcher(headless=True) as fetcher:
                html, final_url = await fetcher.fetch(input_content)
                
            parser = ContentParser()
            content = parser.parse(html, final_url)
            
        # 处理HTML内容
        else:
            # 创建临时文件作为伪URL
            html = input_content
            pseudo_url = "https://html2md.local/content"
            
            parser = ContentParser()
            content = parser.parse(html, pseudo_url)
        
        # 应用插件处理
        if plugin_list:
            for plugin_name in plugin_list:
                plugin = plugin_manager.get_plugin(plugin_name)
                if plugin:
                    content = await plugin.process_content(content)
        
        # 转换为Markdown
        converter = MarkdownConverter()
        markdown = converter.convert(content)
        
        return markdown

    except Exception as e:
        return f"转换失败: {str(e)}"

@mcp.tool()
async def url_to_markdown(url: str, include_images: Optional[bool] = True) -> str:
    """将URL页面转换为Markdown格式
    
    Args:
        url: 要转换的网页URL
        include_images: 是否包含图片，默认为True
    
    Returns:
        转换后的Markdown文本
    """
    try:
        return await _convert_html_to_markdown(url, is_url=True, include_images=include_images)
    except Exception as e:
        return f"转换失败: {str(e)}"

@mcp.tool()
async def html_to_markdown(html_content: str, include_images: Optional[bool] = True) -> str:
    """将HTML内容转换为Markdown格式
    
    Args:
        html_content: HTML内容字符串
        include_images: 是否包含图片，默认为True
    
    Returns:
        转换后的Markdown文本
    """
    try:
        return await _convert_html_to_markdown(html_content, is_url=False, include_images=include_images)
    except Exception as e:
        return f"转换失败: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport='stdio')  # 使用标准输入输出传输