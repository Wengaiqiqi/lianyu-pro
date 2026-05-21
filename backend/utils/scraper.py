import requests
from bs4 import BeautifulSoup


def fetch_url_info(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
        resp = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        resp.raise_for_status()

        content_type = resp.headers.get('content-type', '')
        if 'text/html' not in content_type and 'application/xhtml' not in content_type:
            return {
                'title': '',
                'description': '',
                'favicon': '',
                'error': f'不支持的内容类型: {content_type}',
            }

        soup = BeautifulSoup(resp.content, 'html.parser')

        title = ''
        if soup.title and soup.title.string:
            title = soup.title.string.strip()
        elif soup.title:
            title = soup.title.text.strip()

        description = ''
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            description = meta_desc['content'].strip()
        if not description:
            meta_og = soup.find('meta', attrs={'property': 'og:description'})
            if meta_og and meta_og.get('content'):
                description = meta_og['content'].strip()

        favicon = ''
        icon_link = soup.find('link', rel=lambda x: x and 'icon' in x.lower())
        if icon_link and icon_link.get('href'):
            favicon = icon_link['href']
            if favicon.startswith('//'):
                favicon = 'https:' + favicon
            elif favicon.startswith('/'):
                from urllib.parse import urlparse
                parsed = urlparse(url)
                favicon = f"{parsed.scheme}://{parsed.netloc}{favicon}"
            elif not favicon.startswith('http'):
                favicon = url.rstrip('/') + '/' + favicon

        if not title and not description:
            return {
                'title': '',
                'description': '',
                'favicon': '',
                'error': '无法解析出标题和描述',
            }

        return {
            'title': title,
            'description': description,
            'favicon': favicon,
        }
    except requests.exceptions.Timeout:
        return {
            'title': '',
            'description': '',
            'favicon': '',
            'error': '请求超时',
        }
    except requests.exceptions.ConnectionError:
        return {
            'title': '',
            'description': '',
            'favicon': '',
            'error': '连接失败',
        }
    except requests.exceptions.HTTPError as e:
        return {
            'title': '',
            'description': '',
            'favicon': '',
            'error': f'HTTP错误: {e.response.status_code}',
        }
    except Exception as e:
        return {
            'title': '',
            'description': '',
            'favicon': '',
            'error': str(e),
        }
