import pytest
from src.mcp.markdown_converter import MarkdownConverter
from datetime import datetime

def test_markdown_converter_initialization():
    converter = MarkdownConverter()
    assert converter.template is not None
    
    custom_template = "# {title}\n{content}"
    converter = MarkdownConverter(template=custom_template)
    assert converter.template == custom_template

def test_convert_basic_data():
    data = {
        'title': 'Test Title',
        'url': 'https://example.com/test',
        'content': [
            {
                'type': 'markdown',
                'html': '## Test Content\n\nThis is a test.'
            }
        ]
    }
    
    converter = MarkdownConverter()
    result = converter.convert(data)
    
    assert 'Test Title' in result
    assert 'example.com' in result
    assert 'Test Content' in result
    assert 'This is a test.' in result

def test_convert_with_metadata():
    data = {
        'title': 'Test Title',
        'url': 'https://example.com/test',
        'metadata': {
            'author': 'Test Author',
            'date': '2024-03-20'
        },
        'content': []
    }
    
    converter = MarkdownConverter()
    result = converter.convert(data)
    
    assert '| Author | Test Author |' in result
    assert '| Date | 2024-03-20 |' in result

def test_format_content_blocks():
    data = {
        'title': 'Test',
        'url': 'https://test.com',
        'content': [
            {
                'type': 'text_blocks',
                'html': '<h1>Header</h1><p>Paragraph</p>'
            },
            {
                'type': 'markdown',
                'html': '## Second Header\n\nAnother paragraph'
            }
        ]
    }
    
    converter = MarkdownConverter()
    result = converter.convert(data)
    
    assert '# Header' in result
    assert 'Paragraph' in result
    assert '## Second Header' in result
    assert 'Another paragraph' in result

def test_extract_domain():
    converter = MarkdownConverter()
    assert converter._extract_domain('https://www.example.com/path') == 'example.com'
    assert converter._extract_domain('http://test.com') == 'test.com'
    assert converter._extract_domain('https://sub.domain.com/test') == 'sub.domain.com'
    assert converter._extract_domain('invalid-url') == '' 