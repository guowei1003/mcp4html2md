import argparse
import asyncio
import sys
import os
from typing import List, Optional
from pathlib import Path
from datetime import datetime

from .page_fetcher import PageFetcher
from .content_parser import ContentParser
from .markdown_converter import MarkdownConverter
from .config import Config
from .plugin import PluginManager

__version__ = '1.0.0'

class CLI:
    def __init__(self):
        """初始化CLI"""
        self.config = Config()
        self.plugin_manager = PluginManager()
        
    def create_parser(self) -> argparse.ArgumentParser:
        """创建命令行参数解析器"""
        parser = argparse.ArgumentParser(
            prog='htmlcmd',
            description='HTML Convert Markdown - 将网页内容转换为Markdown格式',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog='''
示例:
  %(prog)s https://example.com                    # 转换网页到Markdown
  %(prog)s -o output.md https://example.com       # 指定输出文件
  %(prog)s --plugins image_downloader example.com # 使用图片下载插件
  %(prog)s --list-plugins                         # 列出所有可用插件
  %(prog)s -v                                     # 显示版本信息
'''
        )
        
        parser.add_argument(
            '-v', '--version',
            action='version',
            version=f'%(prog)s {__version__}',
            help='显示版本信息'
        )
        
        parser.add_argument(
            'url',
            nargs='?',
            help='要处理的网页URL'
        )
        
        parser.add_argument(
            '-o', '--output',
            help='输出文件路径，默认为配置中指定的目录'
        )
        
        parser.add_argument(
            '--no-headless',
            action='store_true',
            help='禁用无头模式（显示浏览器窗口）'
        )
        
        parser.add_argument(
            '--plugins',
            nargs='+',
            help='要使用的插件列表'
        )
        
        parser.add_argument(
            '--list-plugins',
            action='store_true',
            help='列出所有可用的插件'
        )
        
        parser.add_argument(
            '--template',
            help='使用自定义Markdown模板'
        )
        
        return parser
        
    def get_output_path(self, url: str, output: Optional[str] = None) -> str:
        """
        获取输出文件路径
        :param url: 网页URL
        :param output: 指定的输出路径
        :return: 完整的输出文件路径
        """
        if output:
            return os.path.abspath(output)
            
        # 使用配置中的输出目录和文件名模板
        output_dir = self.config.get('output.path')
        filename_template = self.config.get('output.filename_template')
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成文件名
        date_str = datetime.now().strftime('%Y%m%d-%H%M%S')
        filename = filename_template.format(
            title=url.split('/')[-1] or 'index',
            date=date_str
        )
        
        if not filename.endswith('.md'):
            filename += '.md'
            
        return os.path.join(output_dir, filename)
        
    async def process_url(self, url: str, plugins: Optional[List[str]] = None) -> dict:
        """
        处理URL并返回内容
        :param url: 网页URL
        :param plugins: 要使用的插件列表
        :return: 处理后的内容数据
        """
        async with PageFetcher(headless=self.config.get('fetcher.headless', True)) as fetcher:
            html, final_url = await fetcher.fetch(url)
            
        parser = ContentParser()
        content = parser.parse(html, final_url)
        
        # 应用插件
        if plugins:
            for plugin_name in plugins:
                plugin = self.plugin_manager.get_plugin(plugin_name)
                if plugin is None:
                    raise ValueError(f"插件 {plugin_name} 未找到")
                content = await plugin.process_content(content)
            
        return content
        
    def convert_to_markdown(self, content: dict, template: Optional[str] = None) -> str:
        """
        将内容转换为Markdown
        :param content: 内容数据
        :param template: 可选的自定义模板
        :return: Markdown文本
        """
        converter = MarkdownConverter(template)
        return converter.convert(content)
        
    def save_markdown(self, markdown: str, output_path: str) -> None:
        """
        保存Markdown到文件
        :param markdown: Markdown文本
        :param output_path: 输出文件路径
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown)
            
    def list_available_plugins(self) -> None:
        """列出所有可用的插件"""
        plugins = self.plugin_manager.list_plugins()
        if not plugins:
            print("没有找到可用的插件。")
            return
            
        print("\n可用的插件：")
        for plugin in plugins:
            print(f"\n名称: {plugin['name']}")
            print(f"描述: {plugin['description']}")
            
    async def run(self, args: argparse.Namespace) -> int:
        """
        运行CLI
        :param args: 命令行参数
        :return: 退出码
        """
        try:
            if args.list_plugins:
                self.list_available_plugins()
                return 0
                
            if not args.url:
                print("错误：请提供要处理的URL")
                return 1
                
            if not PageFetcher.is_valid_url(args.url):
                print(f"错误：无效的URL: {args.url}")
                return 1
                
            # 处理URL
            content = await self.process_url(args.url, args.plugins)
            
            # 转换为Markdown
            converter = MarkdownConverter(args.template)
            markdown = converter.convert(content)
            
            # 保存到文件
            output_path = self.get_output_path(args.url, args.output)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown)
                
            print(f"\n成功！Markdown文件已保存到：{output_path}")
            return 0
            
        except Exception as e:
            print(f"\n错误：{str(e)}")
            return 1
            
def main():
    """CLI入口点"""
    cli = CLI()
    parser = cli.create_parser()
    
    # 如果没有提供任何参数，显示帮助信息
    if len(sys.argv) == 1:
        parser.print_help()
        return 1
        
    args = parser.parse_args()
    
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    return loop.run_until_complete(cli.run(args))
    
if __name__ == '__main__':
    main() 