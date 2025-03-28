import pytest
from src.convert.plugins.image_processor import ImageProcessor

def test_image_processor_initialization():
    processor = ImageProcessor('image_processor', '')
    assert processor.name == 'image_processor'

@pytest.mark.asyncio
async def test_process_html_images():
    processor = ImageProcessor('image_processor', '')
    content = {
        'url': 'https://example.com/article',
        'content': [
            {
                'type': 'text_blocks',
                'html': '<img src="images/test.jpg"> <img src="https://other.com/img.jpg">',
                'content': ''
            }
        ]
    }

    processed = await processor.process_content(content)
    html = processed['content'][0]['html']
    assert 'src="https://example.com/article/images/test.jpg"' in html
    assert 'src="https://other.com/img.jpg"' in html

@pytest.mark.asyncio
async def test_process_markdown_images():
    processor = ImageProcessor('image_processor', '')
    content = {
        'url': 'https://example.com/article',
        'content': [
            {
                'type': 'markdown',
                'html': '![Alt](/images/test.jpg) ![Other](https://other.com/img.jpg)',
                'content': '![Alt](/images/test.jpg) ![Other](https://other.com/img.jpg)'
            }
        ]
    }

    processed = await processor.process_content(content)
    markdown = processed['content'][0]['content']
    assert '![Alt](https://example.com/images/test.jpg)' in markdown
    assert '![Other](https://other.com/img.jpg)' in markdown

@pytest.mark.asyncio
async def test_process_mixed_content():
    processor = ImageProcessor('image_processor', '')
    content = {
        'url': 'https://example.com/article',
        'content': [
            {
                'type': 'markdown',
                'html': '<img src="img1.jpg"> ![Alt](img2.jpg)',
                'content': '![Alt](img2.jpg)'
            }
        ]
    }

    processed = await processor.process_content(content)
    block = processed['content'][0]
    assert 'src="https://example.com/article/img1.jpg"' in block['html']
    assert '![Alt](https://example.com/article/img2.jpg)' in block['content']

@pytest.mark.asyncio
async def test_handle_empty_content():
    processor = ImageProcessor('image_processor', '')
    content = {
        'url': 'https://example.com/article',
        'content': []
    }

    processed = await processor.process_content(content)
    assert processed == content

@pytest.mark.asyncio
async def test_handle_invalid_content():
    processor = ImageProcessor('image_processor', '')
    content = {
        'url': 'https://example.com/article',
        'content': [None, {'type': 'text', 'html': None}]
    }

    # 不应抛出异常
    processed = await processor.process_content(content)
    assert processed['content'] == content['content'] 