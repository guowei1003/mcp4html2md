import pytest
import os
import tempfile
from unittest.mock import Mock, patch, AsyncMock
from src.convert.cli import CLI

@pytest.fixture
def cli():
    return CLI()

@pytest.fixture
def temp_output_dir(tmp_path):
    return str(tmp_path)

def test_cli_initialization():
    cli = CLI()
    assert cli.config is not None
    assert cli.plugin_manager is not None

def test_create_parser():
    cli = CLI()
    parser = cli.create_parser()
    
    # URL参数虽然是位置参数，但设置了nargs='?'，所以是可选的
    # 不再测试必需参数，因为我们现在允许无参数调用（会显示帮助信息）
    # with pytest.raises(SystemExit):
    #     parser.parse_args([])
        
    # 测试URL参数
    args = parser.parse_args(['https://example.com'])
    assert args.url == 'https://example.com'
    
    # 测试可选参数
    args = parser.parse_args([
        'https://example.com',
        '-o', 'output.md',
        '--no-headless',
        '--plugins', 'plugin1', 'plugin2',
        '--template', 'template.md'
    ])
    assert args.output == 'output.md'
    assert args.no_headless is True
    assert args.plugins == ['plugin1', 'plugin2']
    assert args.template == 'template.md'

@pytest.mark.asyncio
async def test_process_url(cli):
    mock_content = {'title': 'Test', 'content': []}
    
    # Mock PageFetcher
    with patch('src.convert.cli.PageFetcher') as MockFetcher:
        mock_fetcher = AsyncMock()
        mock_fetcher.__aenter__.return_value = mock_fetcher
        mock_fetcher.__aexit__.return_value = None
        mock_fetcher.fetch.return_value = ('html content', 'https://example.com')
        MockFetcher.return_value = mock_fetcher
        
        # Mock ContentParser
        with patch('src.convert.cli.ContentParser') as MockParser:
            mock_parser = Mock()
            mock_parser.parse.return_value = mock_content
            MockParser.return_value = mock_parser
            
            result = await cli.process_url('https://example.com')
            assert result == mock_content

@pytest.mark.asyncio
async def test_convert_to_markdown(cli):
    content = {
        'title': 'Test',
        'content': [
            {'type': 'markdown', 'content': '# Test'}
        ]
    }
    
    result = cli.convert_to_markdown(content)
    assert '# Test' in result

@pytest.mark.asyncio
async def test_get_output_path(cli, temp_output_dir):
    # 测试默认输出路径（现在返回None）
    path = cli.get_output_path('https://example.com')
    assert path is None
    
    # 测试指定输出路径
    output_path = os.path.join(temp_output_dir, 'test.md')
    path = cli.get_output_path('https://example.com', output_path)
    assert path == os.path.abspath(output_path)

@pytest.mark.asyncio
async def test_run(cli, temp_output_dir):
    # 创建参数对象
    args = Mock()
    args.url = 'https://example.com'
    args.plugins = None
    args.template = None
    args.output = None
    args.list_plugins = False
    
    # Mock process_url
    with patch.object(cli, 'process_url') as mock_process:
        mock_process.return_value = {'title': 'Test', 'content': []}
        
        # Mock convert_to_markdown
        with patch.object(cli, 'convert_to_markdown') as mock_convert:
            mock_convert.return_value = '# Test'
            
            # Mock get_output_path
            with patch.object(cli, 'get_output_path') as mock_get_path:
                output_path = os.path.join(temp_output_dir, 'test.md')
                mock_get_path.return_value = output_path
                
                # Mock PageFetcher.is_valid_url
                with patch('src.convert.page_fetcher.PageFetcher.is_valid_url') as mock_valid:
                    mock_valid.return_value = True
                    
                    # 测试成功情况
                    exit_code = await cli.run(args)
                    assert exit_code == 0
                    
                    # 验证文件是否被创建
                    assert os.path.exists(output_path)

@pytest.mark.asyncio
async def test_run_with_output_file(cli, temp_output_dir):
    output_path = os.path.join(temp_output_dir, 'custom.md')
    
    # 创建参数对象
    args = Mock()
    args.url = 'https://example.com'
    args.plugins = None
    args.template = None
    args.output = output_path
    args.list_plugins = False
    
    with patch.object(cli, 'process_url') as mock_process:
        mock_process.return_value = {'title': 'Test', 'content': []}
        with patch.object(cli, 'convert_to_markdown') as mock_convert:
            mock_convert.return_value = '# Test'
            with patch('src.convert.page_fetcher.PageFetcher.is_valid_url') as mock_valid:
                mock_valid.return_value = True
                
                exit_code = await cli.run(args)
                assert exit_code == 0
                assert os.path.exists(output_path)

@pytest.mark.asyncio
async def test_run_with_plugins(cli, temp_output_dir):
    # 创建参数对象
    args = Mock()
    args.url = 'https://example.com'
    args.plugins = ['plugin1']
    args.template = None
    args.output = None
    args.list_plugins = False
    
    with patch.object(cli, 'process_url') as mock_process:
        mock_process.return_value = {'title': 'Test', 'content': []}
        with patch.object(cli, 'convert_to_markdown') as mock_convert:
            mock_convert.return_value = '# Test'
            with patch('src.convert.page_fetcher.PageFetcher.is_valid_url') as mock_valid:
                mock_valid.return_value = True
                
                exit_code = await cli.run(args)
                assert exit_code == 0

@pytest.mark.asyncio
async def test_run_list_plugins(cli):
    # 创建参数对象
    args = Mock()
    args.list_plugins = True
    
    # Mock list_available_plugins
    with patch.object(cli, 'list_available_plugins') as mock_list:
        exit_code = await cli.run(args)
        assert exit_code == 0
        mock_list.assert_called_once()

def test_save_markdown(cli, temp_output_dir):
    markdown = '# Test\nContent'
    
    # 测试保存到文件
    output_path = os.path.join(temp_output_dir, 'test.md')
    cli.save_markdown(markdown, output_path)
    
    assert os.path.exists(output_path)
    with open(output_path, 'r', encoding='utf-8') as f:
        assert f.read() == markdown
        
    # 测试输出到标准输出
    with patch('builtins.print') as mock_print:
        cli.save_markdown(markdown, None)
        mock_print.assert_called_once_with(markdown)

def test_list_available_plugins(cli, capsys):
    # 测试没有插件的情况
    with patch.object(cli.plugin_manager, 'list_plugins', return_value=[]):
        cli.list_available_plugins()
        captured = capsys.readouterr()
        assert "没有找到可用的插件" in captured.out
        
    # 测试有插件的情况
    plugins = [
        {'name': 'plugin1', 'description': 'Plugin 1'},
        {'name': 'plugin2', 'description': 'Plugin 2'}
    ]
    with patch.object(cli.plugin_manager, 'list_plugins', return_value=plugins):
        cli.list_available_plugins()
        captured = capsys.readouterr()
        assert "plugin1" in captured.out
        assert "Plugin 1" in captured.out
        assert "plugin2" in captured.out
        assert "Plugin 2" in captured.out 

@pytest.mark.asyncio
async def test_run_with_stdout(cli):
    """测试使用标准输出的情况"""
    # 创建参数对象
    args = Mock()
    args.url = 'https://example.com'
    args.plugins = None
    args.template = None
    args.output = None  # 空输出路径表示使用标准输出
    args.list_plugins = False
    
    # Mock process_url
    with patch.object(cli, 'process_url') as mock_process:
        mock_process.return_value = {'title': 'Test', 'content': []}
        
        # Mock convert_to_markdown
        with patch.object(cli, 'convert_to_markdown') as mock_convert:
            mock_convert.return_value = '# Test'
            
            # Mock get_output_path - 返回None表示输出到标准输出
            with patch.object(cli, 'get_output_path') as mock_get_path:
                mock_get_path.return_value = None
                
                # Mock save_markdown
                with patch.object(cli, 'save_markdown') as mock_save:
                    # Mock PageFetcher.is_valid_url
                    with patch('src.convert.page_fetcher.PageFetcher.is_valid_url') as mock_valid:
                        mock_valid.return_value = True
                        
                        # 测试成功情况
                        exit_code = await cli.run(args)
                        assert exit_code == 0
                        
                        # 验证save_markdown被正确调用，输出路径为None
                        mock_save.assert_called_once()
                        assert mock_save.call_args[0][1] is None  # 第二个参数应为None 