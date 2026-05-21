import json
import requests


def call_ai_api(api_url, api_key, model_name, messages, temperature=0.7, max_tokens=1024):
    url = api_url.rstrip('/') + '/chat/completions'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}',
    }
    payload = {
        'model': model_name,
        'messages': messages,
        'temperature': temperature,
        'max_tokens': max_tokens,
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    return data['choices'][0]['message']['content']


def test_connection(api_url, api_key, model_name):
    try:
        result = call_ai_api(api_url, api_key, model_name, [
            {'role': 'user', 'content': '请回复"连接成功"四个字。'}
        ], max_tokens=20)
        return True, result.strip()
    except requests.exceptions.Timeout:
        return False, '连接超时，请检查 API 地址'
    except requests.exceptions.ConnectionError:
        return False, '无法连接到 API 地址，请检查 URL 是否正确'
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response is not None else 0
        if status == 401:
            return False, 'API 密钥无效（401 Unauthorized）'
        if status == 404:
            return False, 'API 地址不存在（404），请检查 URL'
        return False, f'HTTP 错误: {status}'
    except Exception as e:
        return False, f'连接失败: {str(e)}'


def analyze_interests(api_url, api_key, model_name, bookmarks):
    if not bookmarks:
        return []

    bookmark_list = '\n'.join(
        f'- {b["title"]}（{b["url"]}）{": " + b["description"] if b.get("description") else ""}'
        for b in bookmarks[:100]
    )

    messages = [
        {
            'role': 'system',
            'content': (
                '你是一个兴趣分析助手。根据用户收藏的网页列表，分析用户的兴趣爱好，'
                '返回 Top 5 的兴趣标签。每个标签包含名称和简短描述。'
                '请以 JSON 数组格式回复，格式为：'
                '[{"tag": "兴趣名称", "description": "简短描述", "count": 相关收藏数量}]'
                '只返回 JSON，不要其他文字。'
            ),
        },
        {
            'role': 'user',
            'content': f'以下是我收藏的网页列表，请分析我的 Top 5 兴趣：\n\n{bookmark_list}',
        },
    ]

    try:
        result = call_ai_api(api_url, api_key, model_name, messages, temperature=0.3)
        result = result.strip()
        if result.startswith('```'):
            result = result.split('\n', 1)[-1].rsplit('```', 1)[0].strip()
        interests = json.loads(result)
        if isinstance(interests, list):
            return interests[:5]
        return []
    except (json.JSONDecodeError, KeyError, IndexError):
        return []


def recommend_keywords(api_url, api_key, model_name, title, description='', url=''):
    messages = [
        {
            'role': 'system',
            'content': (
                '你是一个关键词推荐助手。根据给定的网页信息，推荐 5-8 个相关的关键词标签。'
                '请以 JSON 数组格式回复，格式为：["关键词1", "关键词2", ...]'
                '只返回 JSON 数组，不要其他文字。'
            ),
        },
        {
            'role': 'user',
            'content': f'网页标题：{title}\n网址：{url}\n描述：{description or "无"}\n\n请推荐相关关键词标签。',
        },
    ]

    try:
        result = call_ai_api(api_url, api_key, model_name, messages, temperature=0.3, max_tokens=256)
        result = result.strip()
        if result.startswith('```'):
            result = result.split('\n', 1)[-1].rsplit('```', 1)[0].strip()
        keywords = json.loads(result)
        if isinstance(keywords, list):
            return keywords[:8]
        return []
    except (json.JSONDecodeError, KeyError, IndexError):
        return []


def recommend_urls(api_url, api_key, model_name, interests, bookmarks):
    if not interests:
        return []

    interest_text = '\n'.join(
        f'- {i["tag"]}：{i.get("description", "")}'
        for i in interests
    )

    existing_urls = '\n'.join(
        f'- {b["title"]}（{b["url"]}）'
        for b in bookmarks[:50]
    )

    messages = [
        {
            'role': 'system',
            'content': (
                '你是一个网站推荐助手。根据用户的兴趣标签和已有收藏，推荐 5-8 个用户可能感兴趣的优质网站。'
                '推荐的网站不能与用户已有收藏重复。每个推荐包含网站名称、URL和推荐理由。'
                '请以 JSON 数组格式回复，格式为：'
                '[{"title": "网站名称", "url": "https://...", "description": "推荐理由"}]'
                '请确保推荐的都是真实存在的知名网站，URL 必须有效。只返回 JSON，不要其他文字。'
            ),
        },
        {
            'role': 'user',
            'content': (
                f'我的兴趣标签：\n{interest_text}\n\n'
                f'我已有的收藏：\n{existing_urls}\n\n'
                '请根据我的兴趣推荐新的优质网站。'
            ),
        },
    ]

    try:
        result = call_ai_api(api_url, api_key, model_name, messages, temperature=0.5, max_tokens=1024)
        result = result.strip()
        if result.startswith('```'):
            result = result.split('\n', 1)[-1].rsplit('```', 1)[0].strip()
        urls = json.loads(result)
        if isinstance(urls, list):
            return urls[:8]
        return []
    except (json.JSONDecodeError, KeyError, IndexError):
        return []


def evaluate_url_safety(api_url, api_key, model_name, url, title=''):
    messages = [
        {
            'role': 'system',
            'content': (
                '你是一个内容安全评估助手。请评估以下网页是否适合公开分享。'
                '评估维度：1）是否为有效的正常网站；2）内容是否健康安全（无色情、暴力、欺诈、钓鱼等）；'
                '3）是否为恶意软件或钓鱼网站。'
                '请以 JSON 格式回复，必须包含 safe（布尔值）和 reason（字符串）字段。'
                '示例：{"safe": true, "reason": "知名技术博客，内容健康"}'
                '或：{"safe": false, "reason": "包含钓鱼风险的虚假银行网站"}'
                '只返回 JSON，不要其他文字。'
            ),
        },
        {
            'role': 'user',
            'content': f'网页标题：{title or "无标题"}\n网址：{url}\n\n请评估该网页是否安全可公开。',
        },
    ]

    try:
        result = call_ai_api(api_url, api_key, model_name, messages, temperature=0.1, max_tokens=256)
        result = result.strip()
        if result.startswith('```'):
            result = result.split('\n', 1)[-1].rsplit('```', 1)[0].strip()
        evaluation = json.loads(result)
        if isinstance(evaluation, dict) and 'safe' in evaluation:
            return evaluation
        return {'safe': False, 'reason': '评估结果格式异常'}
    except (json.JSONDecodeError, KeyError, IndexError):
        return {'safe': False, 'reason': '评估请求失败，请稍后重试'}
