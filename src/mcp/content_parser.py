from typing import Dict, List, Tuple, Any, Optional
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import yaml
import os

class ContentParser:
    def __init__(self, custom_rules: Optional[Dict] = None):
        """
        初始化内容解析器
        :param custom_rules: 自定义解析规则
        """
        self.rules = self._load_default_rules()
        if custom_rules:
            self.rules.update(custom_rules)
            
    def _load_default_rules(self) -> Dict:
        """加载默认解析规则"""
        return {
            'github.com': {
                'title': ('xpath', '//h1/strong/a'),
                'content': [
                    ('xpath', '//article', 'markdown'),
                ],
                'metadata': {
                    'stars': ('css', '.social-count'),
                    'language': ('css', '.repository-language-stats-graph'),
                    'updated': ('css', 'relative-time')
                }
            },
            'zhihu.com': {
                'title': ('css', 'h1.QuestionHeader-title'),
                'author': ('css', '.AuthorInfo-name'),
                'content': [
                    ('css', '.QuestionAnswer-content', 'text_blocks')
                ],
                'metadata': {
                    'upvotes': ('css', '.VoteButton--up'),
                    'comments': ('css', '.Comments-count')
                }
            }
        }
        
    def parse(self, html: str, url: str) -> Dict[str, Any]:
        """
        解析HTML内容
        :param html: HTML字符串
        :param url: 页面URL
        :return: 结构化数据字典
        """
        domain = urlparse(url).netloc
        rules = self.rules.get(domain, self._get_default_rules())
        
        soup = BeautifulSoup(html, 'lxml')
        result = {
            'title': '',
            'author': '',
            'content': [],
            'metadata': {},
            'url': url
        }
        
        # 解析标题
        if 'title' in rules:
            result['title'] = self._extract_element(soup, rules['title'])
            
        # 解析作者
        if 'author' in rules:
            result['author'] = self._extract_element(soup, rules['author'])
            
        # 解析内容
        if 'content' in rules:
            for content_rule in rules['content']:
                content = self._extract_content(soup, content_rule)
                if content:
                    result['content'].append(content)
                    
        # 解析元数据
        if 'metadata' in rules:
            for key, rule in rules['metadata'].items():
                result['metadata'][key] = self._extract_element(soup, rule)
                
        return result
        
    def _extract_element(self, soup: BeautifulSoup, rule: Tuple) -> str:
        """
        提取单个元素
        :param soup: BeautifulSoup对象
        :param rule: 提取规则元组 (selector_type, selector)
        :return: 提取的文本
        """
        selector_type, selector = rule[:2]
        if selector_type == 'xpath':
            elements = soup.select(self._xpath_to_css(selector))
        else:  # css
            elements = soup.select(selector)
            
        return elements[0].get_text(strip=True) if elements else ''
        
    def _extract_content(self, soup: BeautifulSoup, rule: Tuple) -> Dict[str, Any]:
        """
        提取内容块
        :param soup: BeautifulSoup对象
        :param rule: 提取规则元组 (selector_type, selector, format)
        :return: 内容字典
        """
        selector_type, selector, format_type = rule
        if selector_type == 'xpath':
            elements = soup.select(self._xpath_to_css(selector))
        else:  # css
            elements = soup.select(selector)
            
        if not elements:
            return None
            
        content = {
            'type': format_type,
            'content': elements[0].get_text(strip=True),
            'html': str(elements[0])
        }
        
        return content
        
    @staticmethod
    def _xpath_to_css(xpath: str) -> str:
        """
        简单的XPath转CSS选择器
        :param xpath: XPath字符串
        :return: CSS选择器
        """
        # 这是一个简化版本，只处理基本情况
        return xpath.replace('//','').replace('/','>')

    def _get_default_rules(self) -> Dict:
        """
        获取默认解析规则
        :return: 默认规则字典
        """
        return {
            'title': ('css', 'h1, .title, .post-title, header h1'),
            'author': ('css', '.author, .post-author, .entry-author'),
            'content': [
                ('css', 'article, .post-content, .entry-content, .content', 'text_blocks')
            ],
            'metadata': {
                'date': ('css', '.date, .post-date, .entry-date'),
                'tags': ('css', '.tags, .post-tags, .entry-tags')
            }
        } 