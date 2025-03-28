import pytest
from src.mcp.content_parser import ContentParser

def test_content_parser_initialization():
    parser = ContentParser()
    assert parser.rules is not None
    assert 'github.com' in parser.rules
    assert 'zhihu.com' in parser.rules
    
    custom_rules = {
        'custom.com': {
            'title': ('css', '.title'),
            'content': [('css', '.content', 'text')]
        }
    }
    parser = ContentParser(custom_rules)
    assert 'custom.com' in parser.rules

def test_parse_github_content():
    html = """
    <html>
        <h1><strong><a>Test Repo</a></strong></h1>
        <article>Test Content</article>
        <span class="social-count">100</span>
        <span class="repository-language-stats-graph">Python</span>
        <relative-time>2024-03-20</relative-time>
    </html>
    """
    parser = ContentParser()
    result = parser.parse(html, "https://github.com/test/repo")
    
    assert result['title'] == 'Test Repo'
    assert len(result['content']) == 1
    assert result['content'][0]['content'] == 'Test Content'
    assert result['metadata']['stars'] == '100'
    assert result['metadata']['language'] == 'Python'
    assert result['metadata']['updated'] == '2024-03-20'

def test_parse_zhihu_content():
    html = """
    <html>
        <h1 class="QuestionHeader-title">Test Question</h1>
        <div class="AuthorInfo-name">Test Author</div>
        <div class="QuestionAnswer-content">Test Answer</div>
        <button class="VoteButton--up">1000</button>
        <div class="Comments-count">50</div>
    </html>
    """
    parser = ContentParser()
    result = parser.parse(html, "https://zhihu.com/question/12345")
    
    assert result['title'] == 'Test Question'
    assert result['author'] == 'Test Author'
    assert len(result['content']) == 1
    assert result['content'][0]['content'] == 'Test Answer'
    assert result['metadata']['upvotes'] == '1000'
    assert result['metadata']['comments'] == '50'

def test_xpath_to_css_conversion():
    parser = ContentParser()
    assert parser._xpath_to_css('//div/span') == 'div>span'
    assert parser._xpath_to_css('//article') == 'article' 