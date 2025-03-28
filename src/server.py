import os
import tempfile
import subprocess
import asyncio
from typing import Optional
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("html-convert-md")

async def _convert_html_to_markdown(input_content: str, is_url: bool = False, include_images: bool = True) -> str:
    """使用 htmlcmd 命令行工具转换内容
    
    Args:
        input_content: 输入内容（URL或HTML内容）
        is_url: 是否为URL
        include_images: 是否包含图片
    
    Returns:
        转换后的Markdown文本
    """
    temp_files = []
    
    try:
        # 如果是HTML内容，先创建临时文件
        if not is_url:
            html_file = tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False)
            html_file.write(input_content)
            html_file.close()
            temp_files.append(html_file.name)
            input_content = html_file.name

        # 创建临时输出文件
        output_file = tempfile.NamedTemporaryFile(suffix='.md', delete=False)
        output_file.close()
        temp_files.append(output_file.name)

        # 构建命令
        cmd = ['htmlcmd']
        if not include_images:
            cmd.extend(['--no-images'])
        cmd.extend(['-o', output_file.name, input_content])

        # 运行命令
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            error_msg = stderr.decode() if stderr else "未知错误"
            return f"转换失败: {error_msg}"

        # 读取输出文件
        with open(output_file.name, 'r', encoding='utf-8') as f:
            result = f.read()

        return result

    except Exception as e:
        return f"转换失败: {str(e)}"
    finally:
        # 清理临时文件
        for file_path in temp_files:
            try:
                if os.path.exists(file_path):
                    os.unlink(file_path)
            except:
                pass

@mcp.tool()
async def url_to_markdown(url: str, include_images: Optional[bool] = True) -> str:
    """将URL页面转换为Markdown格式
    
    Args:
        url: 要转换的网页URL
        include_images: 是否包含图片，默认为True
    
    Returns:
        转换后的Markdown文本
    """
    try:
        return await _convert_html_to_markdown(url, is_url=True, include_images=include_images)
    except Exception as e:
        return f"转换失败: {str(e)}"

@mcp.tool()
async def html_to_markdown(html_content: str, include_images: Optional[bool] = True) -> str:
    """将HTML内容转换为Markdown格式
    
    Args:
        html_content: HTML内容字符串
        include_images: 是否包含图片，默认为True
    
    Returns:
        转换后的Markdown文本
    """
    try:
        return await _convert_html_to_markdown(html_content, is_url=False, include_images=include_images)
    except Exception as e:
        return f"转换失败: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport='stdio')  # 使用标准输入输出传输