import pytest
import os
import tempfile
import aiohttp
from unittest.mock import Mock, patch, AsyncMock
from src.mcp.plugins.image_downloader import ImageDownloader

@pytest.fixture
def image_downloader(tmp_path):
    image_dir = tmp_path / 'images'
    os.makedirs(image_dir, exist_ok=True)
    return ImageDownloader('test_downloader', 'Test Image Downloader')

def test_image_downloader_initialization(image_downloader):
    assert image_downloader.name == 'test_downloader'
    assert image_downloader.description == 'Test Image Downloader'
    assert os.path.exists(image_downloader.image_dir)

def test_extract_image_urls(image_downloader):
    html = '''
    <img src="image1.jpg">
    <img src="http://example.com/image2.png"/>
    <img src='https://test.com/image3.gif'/>
    '''
    urls = image_downloader._extract_image_urls(html)
    assert len(urls) == 3
    assert 'image1.jpg' in urls
    assert 'http://example.com/image2.png' in urls
    assert 'https://test.com/image3.gif' in urls

def test_extract_markdown_image_urls(image_downloader):
    markdown = '''
    ![Alt 1](image1.jpg)
    ![](http://example.com/image2.png)
    ![Test](https://test.com/image3.gif "title")
    '''
    urls = image_downloader._extract_markdown_image_urls(markdown)
    assert len(urls) == 3
    assert ('Alt 1', 'image1.jpg') in urls
    assert ('', 'http://example.com/image2.png') in urls
    assert ('Test', 'https://test.com/image3.gif') in urls

def test_normalize_urls(image_downloader):
    base_url = 'https://example.com/article/'
    urls = [
        'image1.jpg',
        'http://example.com/image2.png',
        'data:image/png;base64,xyz',
        '/images/image3.gif'
    ]
    normalized = image_downloader._normalize_urls(urls, base_url)
    assert 'https://example.com/article/image1.jpg' in normalized
    assert 'http://example.com/image2.png' in normalized
    assert 'data:image/png;base64,xyz' not in normalized
    assert 'https://example.com/images/image3.gif' in normalized

def test_get_extension(image_downloader):
    # 从URL获取扩展名
    assert image_downloader._get_extension('image.jpg', '') == '.jpg'
    assert image_downloader._get_extension('image.PNG', '') == '.png'
    
    # 从content-type获取扩展名
    assert image_downloader._get_extension('image', 'image/jpeg') == '.jpg'
    assert image_downloader._get_extension('image', 'image/png') == '.png'
    assert image_downloader._get_extension('image', 'image/svg+xml') == '.svg'

def test_replace_image_urls(image_downloader):
    html = '''
    <img src="http://example.com/image1.jpg">
    <img src="image2.png"/>
    '''
    url_mapping = {
        'http://example.com/image1.jpg': 'images/local1.jpg',
        'image2.png': 'images/local2.png'
    }
    replaced = image_downloader._replace_image_urls(html, url_mapping)
    assert 'src="images/local1.jpg"' in replaced
    assert 'src="images/local2.png"' in replaced

def test_replace_markdown_image_urls(image_downloader):
    markdown = '''
    ![Alt 1](http://example.com/image1.jpg)
    ![](image2.png)
    '''
    url_mapping = {
        'http://example.com/image1.jpg': 'images/local1.jpg',
        'image2.png': 'images/local2.png'
    }
    replaced = image_downloader._replace_markdown_image_urls(markdown, url_mapping)
    assert '](images/local1.jpg)' in replaced
    assert '](images/local2.png)' in replaced

@pytest.mark.asyncio
async def test_download_images(image_downloader):
    # Mock aiohttp.ClientSession
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.headers = {'content-type': 'image/jpeg'}
    mock_response.read = AsyncMock(return_value=b'fake_image_data')

    mock_session = AsyncMock()
    mock_session.get = AsyncMock(return_value=mock_response)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock()

    with patch('aiohttp.ClientSession', return_value=mock_session):
        urls = ['http://example.com/image1.jpg']
        url_mapping = await image_downloader._download_images(urls)

        assert len(url_mapping) == 1
        assert urls[0] in url_mapping
        local_path = url_mapping[urls[0]]
        assert local_path.startswith('images/img_')
        assert local_path.endswith('.jpg')

@pytest.mark.asyncio
async def test_process_content(image_downloader):
    content = {
        'url': 'https://example.com/article',
        'content': [
            {
                'type': 'markdown',
                'html': '<img src="image1.jpg">',
                'content': '![](image1.jpg)'
            }
        ]
    }

    # Mock _download_images
    mock_mapping = {'https://example.com/article/image1.jpg': 'images/local1.jpg'}
    with patch.object(image_downloader, '_download_images', AsyncMock(return_value=mock_mapping)):
        processed = await image_downloader.process_content(content)

        assert 'images' in processed
        assert len(processed['images']) == 1
        assert processed['images'][0]['original_url'] == 'https://example.com/article/image1.jpg'
        assert processed['images'][0]['local_path'] == 'images/local1.jpg' 