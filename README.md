# MCP (Markdown Content Processor)

A powerful web content scraping and processing tool that converts web pages to well-formatted Markdown documents.

## Features

- **Smart Web Scraping**: Uses Playwright for reliable content extraction, even from JavaScript-heavy websites
- **Intelligent Content Parsing**: Automatically identifies and extracts main content from web pages
- **Markdown Conversion**: Converts HTML content to clean, well-formatted Markdown
- **Plugin System**: Extensible architecture supporting custom content processing plugins
- **Image Processing**: Automatically downloads and manages images with local references
- **Configurable**: Supports custom templates and configuration options
- **Command Line Interface**: Easy to use CLI for quick content processing

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/mcp4html2md.git
cd mcp4html2md

# Install the package
pip install -e .

# Install Playwright browsers (required)
playwright install
```

## Quick Start

Basic usage:
```bash
# Convert a webpage to Markdown
mcp https://example.com

# Specify output file
mcp https://example.com -o output.md

# Use image processing plugin
mcp https://example.com --plugins image_downloader

# List available plugins
mcp --list-plugins
```

## Configuration

MCP uses YAML configuration files. The default configuration is included in the package at `src/mcp/default_config.yaml`. On first run, this configuration will be automatically copied to `~/.mcp/config.yaml`.

### Default Configuration

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
  file_exists_action: increment  # increment, overwrite, or skip

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

### Customizing Configuration

You can customize the configuration in two ways:

1. **Global Configuration**:
   - Edit `~/.mcp/config.yaml`
   - Changes will apply to all future conversions
   ```bash
   # Open config in your default editor
   nano ~/.mcp/config.yaml
   ```

2. **Project-specific Configuration**:
   - Create a `mcp_config.yaml` in your project directory
   - This will override the global configuration for this project
   ```bash
   # Copy default config to current directory
   cp ~/.mcp/config.yaml ./mcp_config.yaml
   ```

### Configuration Options

- **fetcher**: Controls web page fetching
  - `headless`: Run browser in headless mode
  - `timeout`: Page load timeout in seconds
  - `user_agent`: Browser user agent string

- **parser**: Content parsing settings
  - `rules_path`: Directory for custom parsing rules
  - `default_format`: Output format (markdown/html)
  - `default_rules`: CSS selectors for content extraction

- **converter**: Markdown conversion settings
  - `template_path`: Directory for custom templates
  - `default_template`: Default template file
  - `image_path`: Local path for downloaded images
  - `link_style`: URL style in output (relative/absolute)

- **output**: Output file settings
  - `path`: Default output directory
  - `filename_template`: Template for output filenames
  - `create_date_dirs`: Create date-based directories
  - `file_exists_action`: Action when file exists

- **plugins**: Plugin settings
  - `enabled`: List of enabled plugins
  - Plugin-specific configurations

- **logging**: Logging settings
  - `console_level`: Console output level
  - `file_level`: File logging level
  - `log_dir`: Log file directory
  - `max_file_size`: Maximum log file size
  - `backup_count`: Number of backup log files

## Plugin System

MCP supports a plugin system for custom content processing. Available plugins:

- **Image Downloader**: Downloads images to local storage and updates references
  ```bash
  mcp https://example.com --plugins image_downloader
  ```

### Creating Custom Plugins

1. Create a new Python file in the plugins directory
2. Inherit from the `Plugin` base class
3. Implement the `process_content` method

Example:
```python
from mcp.plugin import Plugin

class CustomPlugin(Plugin):
    def __init__(self, name: str, description: str):
        super().__init__(name, description)
    
    def process_content(self, content: dict) -> dict:
        # Process content here
        return content
```

## Logging

MCP includes a comprehensive logging system:
- Console output: INFO level and above
- File logging: DEBUG level and above
- Log files location: `~/.mcp/logs/`

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run specific test file
pytest tests/test_logger.py
```

## Cursor 集成

MCP 可以轻松集成到 Cursor IDE 中，提供便捷的网页内容转换功能。以下是集成步骤：

### 1. 安装 MCP 扩展

1. 打开 Cursor 的命令面板（按 `Cmd+Shift+P` 或 `Ctrl+Shift+P`）
2. 输入 `Extensions: Install Extension`
3. 搜索 `MCP HTML to Markdown`
4. 点击安装

### 2. 配置快捷键（可选）

1. 打开 Cursor 设置（按 `Cmd+,` 或 `Ctrl+,`）
2. 点击 `Keyboard Shortcuts`
3. 搜索 `mcp`
4. 为以下命令设置快捷键：
   - `MCP: Convert URL to Markdown`
   - `MCP: Convert Selection to Markdown`
   - `MCP: Convert Clipboard to Markdown`

### 3. 使用方法

#### 方法一：命令面板

1. 选中网页 URL 或 HTML 内容
2. 打开命令面板
3. 输入 `MCP: Convert` 选择相应的转换命令

#### 方法二：右键菜单

1. 选中网页 URL 或 HTML 内容
2. 右键点击，选择 `MCP Convert to Markdown`

#### 方法三：快捷键

- 使用之前配置的快捷键直接触发转换

### 4. 自定义配置

1. 打开命令面板
2. 输入 `MCP: Open Settings`
3. 修改配置选项：
   ```json
   {
     "mcp.output.path": "~/Documents/mcp-output",
     "mcp.plugins.enabled": ["image_downloader"],
     "mcp.converter.template": "default.md",
     "mcp.fetcher.timeout": 30
   }
   ```

### 5. 常见用例

1. **转换网页文章**
   ```
   1. 复制文章 URL
   2. 在 Cursor 中使用 Cmd+V 或 Ctrl+V 粘贴
   3. 选中 URL
   4. 使用命令面板或快捷键转换
   ```

2. **转换选中的 HTML**
   ```
   1. 选中 HTML 内容
   2. 右键选择 "MCP Convert to Markdown"
   3. 转换后的 Markdown 将替换选中内容
   ```

3. **使用图片下载插件**
   ```
   1. 在设置中启用 image_downloader 插件
   2. 转换时会自动下载图片并更新引用
   ```

### 6. 故障排除

如果遇到问题，请检查：

1. MCP 扩展是否正确安装
2. 配置文件是否正确（`~/.mcp/config.yaml`）
3. 查看输出面板中的错误信息
4. 确保有正确的网络连接

如需更多帮助，请访问：
- [MCP GitHub Issues](https://github.com/yourusername/mcp4html2md/issues)
- [Cursor 扩展文档](https://cursor.sh/docs/extensions)

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
