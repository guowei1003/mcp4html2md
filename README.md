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
html2md https://example.com

# Specify output file
html2md https://example.com -o output.md

# Use image processing plugin
html2md https://example.com --plugins image_downloader

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

Output:
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

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
