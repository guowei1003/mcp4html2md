# HTML Convert Markdown (HTML 转 Markdown MCP 工具)

一个强大的网页内容抓取和处理工具，可以将网页转换为格式良好的 Markdown 文档。

## 特性

- **智能网页抓取**：使用 Playwright 进行可靠的内容提取，即使是重度依赖 JavaScript 的网站
- **智能内容解析**：自动识别和提取网页的主要内容
- **Markdown 转换**：将 HTML 内容转换为清晰、格式良好的 Markdown
- **插件系统**：可扩展的架构，支持自定义内容处理插件
- **图片处理**：自动下载图片并管理本地引用
- **可配置**：支持自定义模板和配置选项
- **命令行界面**：易于使用的 CLI，快速处理内容

## 安装

### 方式一：从 PyPI 安装（推荐）

```bash
# 从 PyPI 安装
pip install mcp4html2md

# 安装 Playwright 浏览器（必需）
playwright install
```

### 方式二：从源码安装

```bash
# 克隆仓库
git clone https://github.com/guowei1003/mcp4html2md.git
cd mcp4html2md

# 安装包
pip install -e .

# 安装 Playwright 浏览器（必需）
playwright install
```

## 快速开始

基本用法：
```bash
# 将网页转换为 Markdown
htmlcmd https://example.com

# 指定输出文件
htmlcmd https://example.com -o output.md

# 使用图片处理插件
htmlcmd https://example.com --plugins image_downloader

# 列出可用插件
htmlcmd --list-plugins
```

## 配置

MCP 使用 YAML 格式的配置文件。默认配置文件包含在包中的 `src/mcp/default_config.yaml`。首次运行时，该配置将自动复制到 `~/.mcp/config.yaml`。

### 默认配置

```yaml
fetcher:
  headless: true
  timeout: 30
  user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

parser:
  rules_path: ~/.mcp/rules
  default_format: markdown
  default_rules:
    title: 'h1'
    content: 'article'
    author: '.author'
    date: '.date'
    tags: '.tags'

converter:
  template_path: ~/.mcp/templates
  default_template: default.md
  image_path: images
  link_style: relative

output:
  path: ~/Documents/mcp-output
  filename_template: '{title}-{date}'
  create_date_dirs: true
  file_exists_action: increment  # increment（递增）, overwrite（覆盖）, 或 skip（跳过）

plugins:
  enabled: []
  image_downloader:
    download_path: images
    skip_data_urls: true
    timeout: 30
    max_retries: 3

logging:
  console_level: INFO
  file_level: DEBUG
  log_dir: ~/.mcp/logs
  max_file_size: 10MB
  backup_count: 5
```

### 自定义配置

您可以通过两种方式自定义配置：

1. **全局配置**：
   - 编辑 `~/.mcp/config.yaml`
   - 更改将应用于所有后续的转换
   ```bash
   # 用默认编辑器打开配置文件
   nano ~/.mcp/config.yaml
   ```

2. **项目特定配置**：
   - 在项目目录中创建 `mcp_config.yaml`
   - 这将覆盖此项目的全局配置
   ```bash
   # 将默认配置复制到当前目录
   cp ~/.mcp/config.yaml ./mcp_config.yaml
   ```

### 配置选项说明

- **fetcher**: 控制网页获取
  - `headless`: 是否使用无头浏览器模式
  - `timeout`: 页面加载超时时间（秒）
  - `user_agent`: 浏览器用户代理字符串

- **parser**: 内容解析设置
  - `rules_path`: 自定义解析规则目录
  - `default_format`: 输出格式（markdown/html）
  - `default_rules`: 内容提取的 CSS 选择器

- **converter**: Markdown 转换设置
  - `template_path`: 自定义模板目录
  - `default_template`: 默认模板文件
  - `image_path`: 下载图片的本地路径
  - `link_style`: 输出中的 URL 样式（相对/绝对）

- **output**: 输出文件设置
  - `path`: 默认输出目录
  - `filename_template`: 输出文件名模板
  - `create_date_dirs`: 是否创建日期目录
  - `file_exists_action`: 文件已存在时的处理方式

- **plugins**: 插件设置
  - `enabled`: 启用的插件列表
  - 各插件的具体配置

- **logging**: 日志设置
  - `console_level`: 控制台输出级别
  - `file_level`: 文件日志级别
  - `log_dir`: 日志文件目录
  - `max_file_size`: 最大日志文件大小
  - `backup_count`: 备份日志文件数量

## 插件系统

MCP 支持自定义内容处理的插件系统。可用插件：

- **图片下载器**：将图片下载到本地存储并更新引用
  ```bash
  mcp https://example.com --plugins image_downloader
  ```

### 创建自定义插件

1. 在插件目录中创建新的 Python 文件
2. 继承 `Plugin` 基类
3. 实现 `process_content` 方法

示例：
```python
from mcp.plugin import Plugin

class CustomPlugin(Plugin):
    def __init__(self, name: str, description: str):
        super().__init__(name, description)
    
    def process_content(self, content: dict) -> dict:
        # 在这里处理内容
        return content
```

## 日志系统

MCP 包含一个完整的日志系统：
- 控制台输出：INFO 级别及以上
- 文件日志：DEBUG 级别及以上
- 日志文件位置：`~/.mcp/logs/`

## 开发

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 运行特定测试文件
pytest tests/test_logger.py
```

结果输出：
```bash
(base)  ✘ /workflow-script/mcp4html2md   main ±  pytest -v
========================================================= test session starts ==========================================================
platform darwin -- Python 3.11.11, pytest-8.3.5, pluggy-1.5.0 -- /miniconda3/envs/media_env/bin/python3.11
cachedir: .pytest_cache
rootdir: /workflow-script/mcp4html2md
configfile: pytest.ini
plugins: asyncio-0.26.0
asyncio: mode=Mode.STRICT, asyncio_default_fixture_loop_scope=function, asyncio_default_test_loop_scope=function
collected 50 items                                                                                                                     

tests/test_cli.py::test_cli_initialization PASSED                                                                                [  2%]
tests/test_cli.py::test_create_parser PASSED                                                                                     [  4%]
tests/test_cli.py::test_process_url PASSED                                                                                       [  6%]
tests/test_cli.py::test_convert_to_markdown PASSED                                                                               [  8%]
tests/test_cli.py::test_get_output_path PASSED                                                                                   [ 10%]
tests/test_cli.py::test_run PASSED                                                                                               [ 12%]
tests/test_cli.py::test_run_with_output_file PASSED                                                                              [ 14%]
tests/test_cli.py::test_run_with_plugins PASSED                                                                                  [ 16%]
tests/test_cli.py::test_run_list_plugins PASSED                                                                                  [ 18%]
tests/test_cli.py::test_save_markdown PASSED                                                                                     [ 20%]
tests/test_cli.py::test_list_available_plugins PASSED                                                                            [ 22%]
tests/test_config.py::test_config_initialization PASSED                                                                          [ 24%]
tests/test_config.py::test_config_get_value PASSED                                                                               [ 26%]
tests/test_config.py::test_config_set_value PASSED                                                                               [ 28%]
tests/test_config.py::test_config_save_and_load PASSED                                                                           [ 30%]
tests/test_config.py::test_default_config_creation PASSED                                                                        [ 32%]
tests/test_content_parser.py::test_content_parser_initialization PASSED                                                          [ 34%]
tests/test_content_parser.py::test_parse_github_content PASSED                                                                   [ 36%]
tests/test_content_parser.py::test_parse_zhihu_content PASSED                                                                    [ 38%]
tests/test_content_parser.py::test_xpath_to_css_conversion PASSED                                                                [ 40%]
tests/test_image_downloader.py::test_image_downloader_initialization PASSED                                                      [ 42%]
tests/test_image_downloader.py::test_extract_image_urls PASSED                                                                   [ 44%]
tests/test_image_downloader.py::test_extract_markdown_image_urls PASSED                                                          [ 46%]
tests/test_image_downloader.py::test_normalize_urls PASSED                                                                       [ 48%]
tests/test_image_downloader.py::test_get_extension PASSED                                                                        [ 50%]
tests/test_image_downloader.py::test_replace_image_urls PASSED                                                                   [ 52%]
tests/test_image_downloader.py::test_replace_markdown_image_urls PASSED                                                          [ 54%]
tests/test_image_downloader.py::test_download_images PASSED                                                                      [ 56%]
tests/test_image_downloader.py::test_process_content PASSED                                                                      [ 58%]
tests/test_image_processor.py::test_image_processor_initialization PASSED                                                        [ 60%]
tests/test_image_processor.py::test_process_html_images PASSED                                                                   [ 62%]
tests/test_image_processor.py::test_process_markdown_images PASSED                                                               [ 64%]
tests/test_image_processor.py::test_process_mixed_content PASSED                                                                 [ 66%]
tests/test_image_processor.py::test_handle_empty_content PASSED                                                                  [ 68%]
tests/test_image_processor.py::test_handle_invalid_content PASSED                                                                [ 70%]
tests/test_logger.py::test_logger_initialization PASSED                                                                          [ 72%]
tests/test_logger.py::test_logger_with_custom_file PASSED                                                                        [ 74%]
tests/test_logger.py::test_logger_reuse PASSED                                                                                   [ 76%]
tests/test_logger.py::test_logger_formatting PASSED                                                                              [ 78%]
tests/test_markdown_converter.py::test_markdown_converter_initialization PASSED                                                  [ 80%]
tests/test_markdown_converter.py::test_convert_basic_data PASSED                                                                 [ 82%]
tests/test_markdown_converter.py::test_convert_with_metadata PASSED                                                              [ 84%]
tests/test_markdown_converter.py::test_format_content_blocks PASSED                                                              [ 86%]
tests/test_markdown_converter.py::test_extract_domain PASSED                                                                     [ 88%]
tests/test_plugin.py::test_plugin_manager_initialization PASSED                                                                  [ 90%]
tests/test_plugin.py::test_plugin_loading PASSED                                                                                 [ 92%]
tests/test_plugin.py::test_plugin_list PASSED                                                                                    [ 94%]
tests/test_plugin.py::test_plugin_processing PASSED                                                                              [ 96%]
tests/test_plugin.py::test_plugin_chain_processing PASSED                                                                        [ 98%]
tests/test_plugin.py::test_invalid_plugin PASSED                                                                                 [100%]

==================================================== 50 passed, 1 warning in 0.58s =====================================================
```

## 贡献

1. Fork 仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m '添加一些很棒的特性'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启一个 Pull Request

## 许可证

本项目基于 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情 
