# HTML Convert Markdown (HTML Convert Markdown MCP Tool)

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

### Option 1: Install from PyPI (Recommended)

```bash
# Install from PyPI
pip install htmlcmd

# Install Playwright browsers (required)
playwright install
```

### Option 2: Install from Source

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
htmlcmd https://example.com

# Specify output file
htmlcmd https://example.com -o output.md

# Use image processing plugin
htmlcmd https://example.com --plugins image_downloader

# List available plugins
mcp --list-plugins
```

## Configuration

MCP uses YAML configuration files. The default configuration is included in the package at `src/convert/default_config.yaml`. On first run, this configuration will be automatically copied to `~/.convert/config.yaml`.

### Default Configuration

```yaml
fetcher:
  headless: true
  timeout: 30
  user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

parser:
  rules_path: ~/.convert/rules
  default_format: markdown
  default_rules:
    title: 'h1'
    content: 'article'
    author: '.author'
    date: '.date'
    tags: '.tags'

converter:
  template_path: ~/.convert/templates
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
  log_dir: ~/.convert/logs
  max_file_size: 10MB
  backup_count: 5
```

### Customizing Configuration

You can customize the configuration in two ways:

1. **Global Configuration**:
   - Edit `~/.convert/config.yaml`
   - Changes will apply to all future conversions
   ```bash
   # Open config in your default editor
   nano ~/.convert/config.yaml
   ```

2. **Project-specific Configuration**:
   - Create a `convert_config.yaml` in your project directory
   - This will override the global configuration for this project
   ```bash
   # Copy default config to current directory
   cp ~/.convert/config.yaml ./convert_config.yaml
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
- Log files location: `~/.convert/logs/`

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run specific test file
pytest tests/test_logger.py
```

Output:
```bash
(base)  ✘ /workflow-script/mcp4html2md   main ±  pytest -v
========================================================================== test session starts ===========================================================================
platform darwin -- Python 3.11.11, pytest-8.3.5, pluggy-1.5.0 -- /Users/cgw/miniconda3/envs/media_env/bin/python3.11
cachedir: .pytest_cache
rootdir: /Users/cgw/workflow-script/mcp4html2md
configfile: pytest.ini
plugins: anyio-4.9.0, asyncio-0.26.0
asyncio: mode=Mode.STRICT, asyncio_default_fixture_loop_scope=function, asyncio_default_test_loop_scope=function
collected 51 items                                                                                                                                                       

tests/test_cli.py::test_cli_initialization PASSED                                                                                                                  [  1%]
tests/test_cli.py::test_create_parser PASSED                                                                                                                       [  3%]
tests/test_cli.py::test_process_url PASSED                                                                                                                         [  5%]
tests/test_cli.py::test_convert_to_markdown PASSED                                                                                                                 [  7%]
tests/test_cli.py::test_get_output_path PASSED                                                                                                                     [  9%]
tests/test_cli.py::test_run PASSED                                                                                                                                 [ 11%]
tests/test_cli.py::test_run_with_output_file PASSED                                                                                                                [ 13%]
tests/test_cli.py::test_run_with_plugins PASSED                                                                                                                    [ 15%]
tests/test_cli.py::test_run_list_plugins PASSED                                                                                                                    [ 17%]
tests/test_cli.py::test_save_markdown PASSED                                                                                                                       [ 19%]
tests/test_cli.py::test_list_available_plugins PASSED                                                                                                              [ 21%]
tests/test_cli.py::test_run_with_stdout PASSED                                                                                                                     [ 23%]
tests/test_config.py::test_config_initialization PASSED                                                                                                            [ 25%]
tests/test_config.py::test_config_get_value PASSED                                                                                                                 [ 27%]
tests/test_config.py::test_config_set_value PASSED                                                                                                                 [ 29%]
tests/test_config.py::test_config_save_and_load PASSED                                                                                                             [ 31%]
tests/test_config.py::test_default_config_creation PASSED                                                                                                          [ 33%]
tests/test_content_parser.py::test_content_parser_initialization PASSED                                                                                            [ 35%]
tests/test_content_parser.py::test_parse_github_content PASSED                                                                                                     [ 37%]
tests/test_content_parser.py::test_parse_zhihu_content PASSED                                                                                                      [ 39%]
tests/test_content_parser.py::test_xpath_to_css_conversion PASSED                                                                                                  [ 41%]
tests/test_image_downloader.py::test_image_downloader_initialization PASSED                                                                                        [ 43%]
tests/test_image_downloader.py::test_extract_image_urls PASSED                                                                                                     [ 45%]
tests/test_image_downloader.py::test_extract_markdown_image_urls PASSED                                                                                            [ 47%]
tests/test_image_downloader.py::test_normalize_urls PASSED                                                                                                         [ 49%]
tests/test_image_downloader.py::test_get_extension PASSED                                                                                                          [ 50%]
tests/test_image_downloader.py::test_replace_image_urls PASSED                                                                                                     [ 52%]
tests/test_image_downloader.py::test_replace_markdown_image_urls PASSED                                                                                            [ 54%]
tests/test_image_downloader.py::test_download_images PASSED                                                                                                        [ 56%]
tests/test_image_downloader.py::test_process_content PASSED                                                                                                        [ 58%]
tests/test_image_processor.py::test_image_processor_initialization PASSED                                                                                          [ 60%]
tests/test_image_processor.py::test_process_html_images PASSED                                                                                                     [ 62%]
tests/test_image_processor.py::test_process_markdown_images PASSED                                                                                                 [ 64%]
tests/test_image_processor.py::test_process_mixed_content PASSED                                                                                                   [ 66%]
tests/test_image_processor.py::test_handle_empty_content PASSED                                                                                                    [ 68%]
tests/test_image_processor.py::test_handle_invalid_content PASSED                                                                                                  [ 70%]
tests/test_logger.py::test_logger_initialization PASSED                                                                                                            [ 72%]
tests/test_logger.py::test_logger_with_custom_file PASSED                                                                                                          [ 74%]
tests/test_logger.py::test_logger_reuse PASSED                                                                                                                     [ 76%]
tests/test_logger.py::test_logger_formatting PASSED                                                                                                                [ 78%]
tests/test_markdown_converter.py::test_markdown_converter_initialization PASSED                                                                                    [ 80%]
tests/test_markdown_converter.py::test_convert_basic_data PASSED                                                                                                   [ 82%]
tests/test_markdown_converter.py::test_convert_with_metadata PASSED                                                                                                [ 84%]
tests/test_markdown_converter.py::test_format_content_blocks PASSED                                                                                                [ 86%]
tests/test_markdown_converter.py::test_extract_domain PASSED                                                                                                       [ 88%]
tests/test_plugin.py::test_plugin_manager_initialization PASSED                                                                                                    [ 90%]
tests/test_plugin.py::test_plugin_loading PASSED                                                                                                                   [ 92%]
tests/test_plugin.py::test_plugin_list PASSED                                                                                                                      [ 94%]
tests/test_plugin.py::test_plugin_processing PASSED                                                                                                                [ 96%]
tests/test_plugin.py::test_plugin_chain_processing PASSED                                                                                                          [ 98%]
tests/test_plugin.py::test_invalid_plugin PASSED                                                                                                                   [100%]

============================================================================ warnings summary ============================================================================
tests/test_plugins/test_plugin.py:3
  /Users/cgw/workflow-script/mcp4html2md/tests/test_plugins/test_plugin.py:3: PytestCollectionWarning: cannot collect test class 'TestPlugin' because it has a __init__ constructor (from: tests/test_plugins/test_plugin.py)
    class TestPlugin(Plugin):

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
===================================================================== 51 passed, 1 warning in 0.57s ======================================================================
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
