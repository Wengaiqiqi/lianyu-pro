"""全局注入常用网站书签"""
import requests
from urllib.parse import urlparse
from app import create_app
from models import db
from models.bookmark import Bookmark
from models.category import Category


DEFAULT_BOOKMARKS = {
    '技术': [
        ('GitHub', 'https://github.com', '全球最大的代码托管平台'),
        ('Stack Overflow', 'https://stackoverflow.com', '程序员问答社区'),
        ('掘金', 'https://juejin.cn', '面向全球中文开发者的技术社区'),
        ('CSDN', 'https://csdn.net', '中国专业开发者社区'),
        ('V2EX', 'https://v2ex.com', '程序员主题社区'),
        ('SegmentFault', 'https://segmentfault.com', '思否开发者社区'),
    ],
    '工具': [
        ('Google', 'https://google.com', '全球最大的搜索引擎'),
        ('百度', 'https://baidu.com', '中文搜索引擎'),
        ('Notion', 'https://notion.so', '协作workspace'),
        ('Figma', 'https://figma.com', '在线协作设计工具'),
        ('JSON格式化', 'https://json.cn', 'JSON在线解析工具'),
        ('Regex101', 'https://regex101.com', '正则表达式测试工具'),
    ],
    '学习': [
        ('Bilibili', 'https://bilibili.com', '国内知名的视频弹幕网站'),
        ('网易云课堂', 'https://study.163.com', '在线学习平台'),
        ('中国大学MOOC', 'https://icourse163.org', '优质在线课程平台'),
        ('腾讯课堂', 'https://ke.qq.com', '在线职业教育平台'),
        ('知乎', 'https://zhihu.com', '中文互联网高质量问答社区'),
    ],
    '娱乐': [
        ('哔哩哔哩', 'https://bilibili.com', '国内知名的视频弹幕网站'),
        ('抖音', 'https://www.douyin.com', '短视频分享平台'),
        ('小红书', 'https://www.xiaohongshu.com', '生活方式分享社区'),
        ('优酷', 'https://youku.com', '视频播放平台'),
        ('网易云音乐', 'https://music.163.com', '在线音乐平台'),
    ],
    '新闻': [
        ('今日头条', 'https://www.toutiao.com', '个性化资讯推荐平台'),
        ('腾讯新闻', 'https://news.qq.com', '综合新闻资讯'),
        ('36氪', 'https://36kr.com', '创业投资资讯平台'),
        ('少数派', 'https://sspai.com', '高品质数字生活指南'),
    ],
    '社交': [
        ('微博', 'https://weibo.com', '中国最大的社交媒体平台'),
        ('微信', 'https://weixin.qq.com', '即时通讯与社交平台'),
        ('Twitter', 'https://twitter.com', '全球社交新闻平台'),
        ('Reddit', 'https://reddit.com', '国外社交新闻论坛'),
    ],
    '购物': [
        ('淘宝', 'https://taobao.com', '国内领先的网络零售平台'),
        ('京东', 'https://jd.com', '综合网购平台'),
        ('拼多多', 'https://pinduoduo.com', '新电商开创者'),
        ('唯品会', 'https://vip.com', '品牌特卖网站'),
    ],
}


def _abs_url(base, href):
    if not href:
        return None
    if href.startswith('//'):
        return 'https:' + href
    if href.startswith('/'):
        parsed = urlparse(base)
        return f"{parsed.scheme}://{parsed.netloc}{href}"
    if not href.startswith('http'):
        return base.rstrip('/') + '/' + href
    return href


def _is_valid_favicon(url):
    """验证 favicon 是否为有效的图标：
    - ICO/SVG：验证 Content-Type 即可
    - PNG/JPEG：需有 Content-Length 且 500B~20KB 之间
    - 返回空字符串的（size=0）：失败
    """
    if not url:
        return False
    try:
        r = requests.head(url, timeout=4,
                          headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'},
                          allow_redirects=True)
        if r.status_code != 200:
            return False
        ct = r.headers.get('content-type', '')
        if 'image/svg' in ct or 'image/x-icon' in ct or 'vnd.microsoft.icon' in ct:
            size = int(r.headers.get('content-length', 0))
            return size > 100  # ICO/SVG 也需要最小大小，空文件不行
        if 'image/png' in ct or 'image/jpeg' in ct:
            size = int(r.headers.get('content-length', 0))
            return 500 < size <= 20 * 1024
        return False
    except Exception:
        return False


def get_favicon(url):
    """多重保底获取网站 favicon：
    1. 根目录 /favicon.ico（最可靠）
    2. 网页 HTML 中解析
    3. DuckDuckGo API
    4. 验证有效性，失败则返回空字符串
    """
    candidates = []
    parsed = urlparse(url)
    domain = parsed.netloc

    # 1. 根目录 favicon.ico（最可靠）
    candidates.append(f"{parsed.scheme}://{domain}/favicon.ico")

    # 2. 网页 HTML 解析
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
        resp = requests.get(url, headers=headers, timeout=5, allow_redirects=True)
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(resp.content, 'html.parser')

        for rel in ['apple-touch-icon', 'apple-touch-icon-precomposed', 'shortcut icon', 'icon']:
            icon_link = soup.find('link', rel=lambda x: x and rel in x.lower())
            if icon_link and icon_link.get('href'):
                fav = _abs_url(url, icon_link['href'])
                if fav:
                    candidates.append(fav)
    except Exception:
        pass

    # 3. DuckDuckGo API（跳过大小验证，用 stream 读取 1 字节判断是否有内容）
    candidates.append(f'https://icons.duckduckgo.com/ip3/{domain}.ico')

    # 4. 验证每个候选（ICO/SVG 直接通过，PNG/JPEG 限制 500B~20KB）
    for fav in candidates:
        is_duckduckgo = 'duckduckgo' in fav
        if is_duckduckgo:
            try:
                r = requests.get(fav, timeout=4, stream=True,
                                 headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'},
                                 allow_redirects=True)
                if r.status_code != 200:
                    continue
                ct = r.headers.get('content-type', '')
                cl = int(r.headers.get('content-length', 0))
                if 'image' not in ct:
                    continue
                if cl == 0:
                    # Content-Length=0 但可能有 chunked 内容，读取 1 字节验证
                    chunk = next(r.iter_content(1), None)
                    if chunk is None:
                        continue
                return fav
            except Exception:
                pass
        elif _is_valid_favicon(fav):
            return fav

    return ''
    for fav in candidates:
        if _is_valid_favicon(fav):
            return fav

    return ''


def seed_global_bookmarks():
    """为系统注入全局常用书签"""
    app = create_app()
    with app.app_context():
        global_cats = {c.name: c for c in Category.query.filter_by(user_id=None).all()}
        added_count = 0
        skipped_count = 0

        for cat_name, bookmarks in DEFAULT_BOOKMARKS.items():
            if cat_name not in global_cats:
                print(f'跳过分类 "{cat_name}"，未找到对应的全局分类')
                continue
            category = global_cats[cat_name]

            for title, url, description in bookmarks:
                existing = Bookmark.query.filter_by(url=url, user_id=None).first()
                if existing:
                    skipped_count += 1
                    continue
                bookmark = Bookmark(
                    title=title, url=url, description=description,
                    favicon=get_favicon(url), user_id=None,
                    category_id=category.id, is_public=True,
                )
                db.session.add(bookmark)
                added_count += 1

        db.session.commit()
        print(f'完成！新增 {added_count} 个全局书签，跳过 {skipped_count} 个已存在的书签')


def update_favicons():
    """批量更新全局书签的 favicon"""
    app = create_app()
    with app.app_context():
        bookmarks = Bookmark.query.filter_by(user_id=None).all()
        updated = 0
        empty = 0
        for b in bookmarks:
            new = get_favicon(b.url)
            b.favicon = new
            if new:
                updated += 1
            else:
                empty += 1
        db.session.commit()
        print(f'完成！{updated} 个已更新为有效 favicon，{empty} 个无法获取已清空（前端将显示默认图标）')


def fix_all_favicons():
    """修复所有书签（包含用户书签）"""
    app = create_app()
    with app.app_context():
        bookmarks = Bookmark.query.all()
        updated = 0
        empty = 0
        for b in bookmarks:
            new = get_favicon(b.url)
            b.favicon = new
            if new:
                updated += 1
            else:
                empty += 1
        db.session.commit()
        print(f'完成！共处理 {len(bookmarks)} 个书签，{updated} 个已更新，{empty} 个已清空')


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--update':
        update_favicons()
    elif len(sys.argv) > 1 and sys.argv[1] == '--fix-all':
        fix_all_favicons()
    else:
        seed_global_bookmarks()
