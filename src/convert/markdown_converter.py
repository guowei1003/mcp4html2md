from typing import Dict, Any, List
from markdownify import markdownify as md
from datetime import datetime
import re

class MarkdownConverter:
    def __init__(self, template: str = None):
        """
        初始化Markdown转换器
        :param template: 可选的自定义模板
        """
        self.template = template or self._default_template()
        
    def convert(self, data: Dict[str, Any]) -> str:
        """
        将结构化数据转换为Markdown
        :param data: ContentParser解析的数据
        :return: Markdown字符串
        """
        # 准备模板变量
        variables = {
            'title': data.get('title', '无标题'),
            'url': data.get('url', ''),
            'domain': self._extract_domain(data.get('url', '')),
            'author': data.get('author', ''),
            'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'metadata': self._format_metadata(data.get('metadata', {})),
            'content': self._format_content(data.get('content', [])),
        }
        
        # 渲染模板
        return self._render_template(variables)
        
    def _format_metadata(self, metadata: Dict) -> str:
        """格式化元数据为Markdown表格"""
        if not metadata:
            return ''
            
        rows = []
        for key, value in metadata.items():
            key = key.replace('_', ' ').title()
            rows.append(f'| {key} | {value} |')
            
        if rows:
            header = '| 属性 | 值 |\n|------|-------|'
            return header + '\n' + '\n'.join(rows)
        return ''
        
    def _format_content(self, content_blocks: List[Dict]) -> str:
        """
        格式化内容块为Markdown
        :param content_blocks: 内容块列表
        :return: Markdown字符串
        """
        formatted = []
        for block in content_blocks:
            if not block:
                continue
                
            content_type = block.get('type', '')
            html_content = block.get('html', '')
            
            if content_type == 'markdown':
                # 已经是Markdown格式，直接使用
                formatted.append(html_content)
            elif content_type == 'text_blocks':
                # 将HTML转换为Markdown
                markdown = md(html_content, heading_style='ATX')
                formatted.append(markdown)
            else:
                # 默认转换为Markdown
                markdown = md(html_content, heading_style='ATX')
                formatted.append(markdown)
                
        return '\n\n'.join(formatted)
        
    def _render_template(self, variables: Dict[str, str]) -> str:
        """渲染Markdown模板"""
        result = self.template
        for key, value in variables.items():
            placeholder = '{' + key + '}'
            result = result.replace(placeholder, str(value))
        return result
        
    @staticmethod
    def _extract_domain(url: str) -> str:
        """从URL中提取域名"""
        match = re.search(r'https?://(?:www\.)?([^/]+)', url)
        return match.group(1) if match else ''
        
    @staticmethod
    def _default_template() -> str:
        """默认Markdown模板"""
        return '''# {title}

> 来源: [{domain}]({url})  
> 抓取时间: {datetime}

{metadata}

---

{content}

---

> 由Convert工具自动生成，原文版权归作者所有''' 