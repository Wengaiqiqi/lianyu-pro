from datetime import datetime, timedelta

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from models import db
from models.bookmark import Bookmark
from models.bookmark_visit import BookmarkVisit
from models.category import Category
from utils.auth import active_required, log_operation
from utils.scraper import fetch_url_info


bookmark_bp = Blueprint('bookmark', __name__)


def get_ranking_period_range(ranking_type, period='current'):
    now = datetime.utcnow()

    if period == 'previous_month':
        first_day_current_month = datetime(now.year, now.month, 1)
        end_at = first_day_current_month
        previous_month_last_day = first_day_current_month - timedelta(days=1)
        start_at = datetime(previous_month_last_day.year, previous_month_last_day.month, 1)
        return start_at, end_at

    if ranking_type == 'day':
        start_at = now - timedelta(days=1)
    elif ranking_type == 'week':
        start_at = now - timedelta(days=7)
    elif ranking_type == 'month':
        start_at = now - timedelta(days=30)
    else:
        start_at = now - timedelta(days=1)

    return start_at, now


def get_ranked_bookmarks(base_query, ranking_type='day', limit=10, period='current'):
    start_at, end_at = get_ranking_period_range(ranking_type, period)

    ranked_rows = (
        db.session.query(
            Bookmark.id.label('bookmark_id'),
            db.func.count(BookmarkVisit.id).label('period_visits'),
        )
        .select_from(Bookmark)
        .join(BookmarkVisit, BookmarkVisit.bookmark_id == Bookmark.id)
        .filter(
            base_query,
            BookmarkVisit.created_at >= start_at,
            BookmarkVisit.created_at < end_at,
        )
        .group_by(Bookmark.id)
        .order_by(
            db.func.count(BookmarkVisit.id).desc(),
            Bookmark.created_at.desc(),
        )
        .limit(limit)
        .all()
    )

    bookmark_ids = [row.bookmark_id for row in ranked_rows]
    if not bookmark_ids:
        return []

    bookmarks = Bookmark.query.filter(Bookmark.id.in_(bookmark_ids)).all()
    bookmark_map = {bookmark.id: bookmark for bookmark in bookmarks}

    ranked_bookmarks = []
    for row in ranked_rows:
        bookmark = bookmark_map.get(row.bookmark_id)
        if not bookmark:
            continue

        data = bookmark.to_dict()
        data['period_visits'] = int(row.period_visits or 0)
        data['ranking_type'] = ranking_type
        data['period'] = period
        data['period_start'] = start_at.isoformat()
        data['period_end'] = end_at.isoformat()
        ranked_bookmarks.append(data)

    return ranked_bookmarks


def get_ranked_bookmarks_by_url(base_query, ranking_type='day', limit=10, period='current'):
    """按 URL 合并统计热度，同一 URL 的所有访问记录累加"""
    start_at, end_at = get_ranking_period_range(ranking_type, period)

    ranked_rows = (
        db.session.query(
            Bookmark.url.label('url'),
            db.func.max(Bookmark.id).label('bookmark_id'),
            db.func.count(BookmarkVisit.id).label('period_visits'),
        )
        .select_from(Bookmark)
        .join(BookmarkVisit, BookmarkVisit.bookmark_id == Bookmark.id)
        .filter(
            base_query,
            BookmarkVisit.created_at >= start_at,
            BookmarkVisit.created_at < end_at,
        )
        .group_by(Bookmark.url)
        .order_by(
            db.func.count(BookmarkVisit.id).desc(),
        )
        .limit(limit)
        .all()
    )

    if not ranked_rows:
        return []

    bookmark_ids = [row.bookmark_id for row in ranked_rows]
    bookmarks = Bookmark.query.filter(Bookmark.id.in_(bookmark_ids)).all()
    bookmark_map = {bookmark.id: bookmark for bookmark in bookmarks}

    ranked_bookmarks = []
    for row in ranked_rows:
        bookmark = bookmark_map.get(row.bookmark_id)
        if not bookmark:
            continue

        data = bookmark.to_dict()
        data['period_visits'] = int(row.period_visits or 0)
        data['ranking_type'] = ranking_type
        data['period'] = period
        data['period_start'] = start_at.isoformat()
        data['period_end'] = end_at.isoformat()
        ranked_bookmarks.append(data)

    return ranked_bookmarks


@bookmark_bp.route('', methods=['GET'])
@jwt_required()
@active_required
def get_bookmarks():
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    category_id = request.args.get('category_id', type=int)

    query = Bookmark.query.filter_by(user_id=user_id, is_blocked=False)
    if category_id:
        cat_ids = [category_id]

        def collect_children(parent_id):
            children = Category.query.filter_by(parent_id=parent_id).all()
            for child in children:
                cat_ids.append(child.id)
                collect_children(child.id)

        collect_children(category_id)
        query = query.filter(Bookmark.category_id.in_(cat_ids))

    query = query.order_by(Bookmark.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify(code=200, data={
        'items': [bookmark.to_dict() for bookmark in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages,
    })


@bookmark_bp.route('', methods=['POST'])
@jwt_required()
@active_required
def add_bookmark():
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    title = data.get('title', '').strip()
    url = data.get('url', '').strip()

    if not title or not url:
        return jsonify(code=400, msg='标题或 URL 不能为空')

    # 批查是否已存在相同 URL 的书签
    existing = Bookmark.query.filter_by(user_id=user_id, url=url).first()
    if existing:
        return jsonify(code=400, msg='该链接已在我的链域中，无需重复添加')

    bookmark = Bookmark(
        title=title,
        url=url,
        description=data.get('description', ''),
        favicon=data.get('favicon', ''),
        user_id=user_id,
        category_id=data.get('category_id'),
        is_public=data.get('is_public', False),
    )
    db.session.add(bookmark)
    db.session.commit()

    log_operation(user_id, '创建书签', 'bookmark', bookmark.id, f'创建书签: {title}')
    return jsonify(code=200, msg='created', data=bookmark.to_dict())


@bookmark_bp.route('/<int:bookmark_id>', methods=['PUT'])
@jwt_required()
@active_required
def update_bookmark(bookmark_id):
    user_id = get_jwt_identity()
    bookmark = Bookmark.query.filter_by(id=bookmark_id, user_id=user_id).first()
    if not bookmark:
        return jsonify(code=404, msg='bookmark not found')

    data = request.get_json() or {}
    if 'title' in data:
        bookmark.title = data['title'].strip()
    if 'url' in data:
        bookmark.url = data['url'].strip()
    if 'description' in data:
        bookmark.description = data['description']
    if 'favicon' in data:
        bookmark.favicon = data['favicon']
    if 'category_id' in data:
        bookmark.category_id = data['category_id']
    if 'is_public' in data:
        bookmark.is_public = data['is_public']

    db.session.commit()
    log_operation(user_id, '更新书签', 'bookmark', bookmark.id, f'更新书签: {bookmark.title}')
    return jsonify(code=200, msg='updated', data=bookmark.to_dict())


@bookmark_bp.route('/<int:bookmark_id>', methods=['DELETE'])
@jwt_required()
@active_required
def delete_bookmark(bookmark_id):
    user_id = get_jwt_identity()
    bookmark = Bookmark.query.filter_by(id=bookmark_id, user_id=user_id).first()
    if not bookmark:
        return jsonify(code=404, msg='bookmark not found')

    title = bookmark.title
    # 先删除关联的访问记录
    BookmarkVisit.query.filter_by(bookmark_id=bookmark_id).delete()
    db.session.delete(bookmark)
    db.session.commit()

    try:
        log_operation(user_id, '删除', 'bookmark', bookmark_id, f'删除: {title}')
    except Exception:
        pass

    return jsonify(code=200, msg='删除成功')


@bookmark_bp.route('/fetch-info', methods=['POST'])
@jwt_required()
@active_required
def fetch_info():
    data = request.get_json() or {}
    url = data.get('url', '').strip()
    if not url:
        return jsonify(code=400, msg='URL is required')

    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    info = fetch_url_info(url)
    return jsonify(code=200, data=info)


@bookmark_bp.route('/search', methods=['GET'])
@jwt_required()
@active_required
def search_bookmarks():
    user_id = get_jwt_identity()
    q = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    if not q:
        return jsonify(code=400, msg='search keyword is required')

    keyword = f'%{q}%'
    query = Bookmark.query.filter_by(user_id=user_id, is_blocked=False).filter(
        db.or_(
            Bookmark.title.like(keyword),
            Bookmark.description.like(keyword),
            Bookmark.url.like(keyword),
        )
    ).order_by(Bookmark.created_at.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify(code=200, data={
        'items': [bookmark.to_dict() for bookmark in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
    })


@bookmark_bp.route('/public', methods=['GET'])
def public_bookmarks():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 30, type=int)
    category_id = request.args.get('category_id', type=int)
    keyword = request.args.get('keyword', '').strip()

    query = Bookmark.query.filter_by(user_id=None, is_blocked=False)

    if category_id:
        req_cat = Category.query.get(category_id)
        if req_cat:
            query = query.join(Category, Bookmark.category_id == Category.id).filter(Category.name == req_cat.name)

    if keyword:
        kw = f'%{keyword}%'
        query = query.filter(
            db.or_(
                Bookmark.title.like(kw),
                Bookmark.description.like(kw),
                Bookmark.url.like(kw),
            )
        )

    query = query.order_by(Bookmark.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    categories = Category.query.filter_by(user_id=None, parent_id=None).order_by(Category.sort_order).all()

    return jsonify(code=200, data={
        'items': [bookmark.to_dict() for bookmark in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'categories': [category.to_dict(include_children=True) for category in categories],
    })


@bookmark_bp.route('/public/<int:bookmark_id>', methods=['GET'])
def get_public_bookmark_detail(bookmark_id):
    bookmark = Bookmark.query.filter(
        Bookmark.id == bookmark_id,
        Bookmark.is_blocked.is_(False),
        db.or_(
            Bookmark.user_id.is_(None),
            Bookmark.is_public.is_(True),
        ),
    ).first()

    if not bookmark:
        return jsonify(code=404, msg='public bookmark not found')

    return jsonify(code=200, data=bookmark.to_dict())


@bookmark_bp.route('/public/<int:bookmark_id>/visit-trend', methods=['GET'])
def get_public_bookmark_visit_trend(bookmark_id):
    bookmark = Bookmark.query.filter(
        Bookmark.id == bookmark_id,
        Bookmark.is_blocked.is_(False),
        db.or_(
            Bookmark.user_id.is_(None),
            Bookmark.is_public.is_(True),
        ),
    ).first()

    if not bookmark:
        return jsonify(code=404, msg='public bookmark not found')

    days = request.args.get('days', 7, type=int)
    days = max(3, min(days, 30))

    today = datetime.utcnow().date()
    start_date = today - timedelta(days=days - 1)
    start_at = datetime.combine(start_date, datetime.min.time())

    rows = (
        db.session.query(
            db.func.date(BookmarkVisit.created_at).label('visit_date'),
            db.func.count(BookmarkVisit.id).label('visit_count'),
        )
        .filter(
            BookmarkVisit.bookmark_id == bookmark.id,
            BookmarkVisit.created_at >= start_at,
        )
        .group_by(db.func.date(BookmarkVisit.created_at))
        .order_by(db.func.date(BookmarkVisit.created_at).asc())
        .all()
    )

    count_map = {
        str(row.visit_date): int(row.visit_count or 0)
        for row in rows
    }

    items = []
    for offset in range(days):
        current_date = start_date + timedelta(days=offset)
        key = current_date.isoformat()
        items.append({
            'date': key,
            'visits': count_map.get(key, 0),
        })

    return jsonify(code=200, data={
        'days': days,
        'items': items,
    })


@bookmark_bp.route('/rankings', methods=['GET'])
def get_rankings():
    ranking_type = request.args.get('type', 'day')
    limit = request.args.get('limit', 10, type=int)
    period = request.args.get('period', 'current').strip() or 'current'

    data = get_ranked_bookmarks(
        db.and_(
            Bookmark.user_id.is_(None),
            Bookmark.is_blocked.is_(False),
        ),
        ranking_type=ranking_type,
        limit=limit,
        period=period,
    )
    return jsonify(code=200, data=data)


@bookmark_bp.route('/users/public', methods=['GET'])
def public_user_bookmarks():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 30, type=int)
    category_id = request.args.get('category_id', type=int)
    keyword = request.args.get('keyword', '').strip()
    user_id_filter = request.args.get('user_id', type=int)

    query = Bookmark.query.filter(
        Bookmark.user_id.isnot(None),
        Bookmark.is_public.is_(True),
        Bookmark.is_blocked.is_(False),
    )

    if user_id_filter:
        query = query.filter(Bookmark.user_id == user_id_filter)

    if category_id:
        req_cat = Category.query.get(category_id)
        if req_cat:
            query = query.join(Category, Bookmark.category_id == Category.id).filter(Category.name == req_cat.name)

    if keyword:
        kw = f'%{keyword}%'
        query = query.filter(
            db.or_(
                Bookmark.title.like(kw),
                Bookmark.description.like(kw),
                Bookmark.url.like(kw),
            )
        )

    query = query.order_by(Bookmark.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    user_categories = Category.query.filter(Category.user_id.isnot(None), Category.parent_id == None).order_by(Category.sort_order).all()

    return jsonify(code=200, data={
        'items': [bookmark.to_dict() for bookmark in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'categories': [category.to_dict(include_children=True) for category in user_categories],
    })


@bookmark_bp.route('/users/public/rankings', methods=['GET'])
def get_public_user_bookmark_rankings():
    ranking_type = request.args.get('type', 'day')
    limit = request.args.get('limit', 8, type=int)
    period = request.args.get('period', 'current').strip() or 'current'

    bookmarks = get_ranked_bookmarks_by_url(
        db.and_(
            Bookmark.user_id.isnot(None),
            Bookmark.is_public.is_(True),
            Bookmark.is_blocked.is_(False),
        ),
        ranking_type=ranking_type,
        limit=limit,
        period=period,
    )
    return jsonify(code=200, data={
        'type': ranking_type,
        'period': period,
        'items': bookmarks,
    })


@bookmark_bp.route('/<int:bookmark_id>/visit', methods=['POST'])
def increment_visit(bookmark_id):
    bookmark = Bookmark.query.get(bookmark_id)
    if not bookmark or bookmark.is_blocked:
        return jsonify(code=404, msg='public bookmark not found')

    bookmark.visits = (bookmark.visits or 0) + 1
    db.session.add(BookmarkVisit(bookmark_id=bookmark.id))
    db.session.commit()
    return jsonify(code=200, msg='recorded', data={'visits': bookmark.visits})


@bookmark_bp.route('/pending-review', methods=['GET'])
@jwt_required()
@active_required
def get_pending_review():
    pending = Bookmark.query.filter_by(is_pending_review=True).order_by(Bookmark.created_at.desc()).all()
    return jsonify(code=200, data=[bookmark.to_dict() for bookmark in pending])


@bookmark_bp.route('/<int:bookmark_id>/approve', methods=['POST'])
@jwt_required()
@active_required
def approve_bookmark(bookmark_id):
    bookmark = Bookmark.query.get(bookmark_id)
    if not bookmark:
        return jsonify(code=404, msg='bookmark not found')

    data = request.get_json() or {}
    pending_type = bookmark.pending_type or 'public'

    if pending_type == 'homepage':
        category_id = data.get('category_id')
        if not category_id:
            return jsonify(code=400, msg='category is required')

        category = Category.query.get(category_id)
        if not category:
            return jsonify(code=404, msg='category not found')

        new_bookmark = Bookmark(
            title=bookmark.title,
            url=bookmark.url,
            description=bookmark.description,
            favicon=bookmark.favicon,
            user_id=None,
            category_id=category_id,
            is_public=True,
            is_blocked=False,
            visits=0,
        )
        db.session.add(new_bookmark)
        bookmark.is_pending_review = False
        bookmark.pending_category = ''
        bookmark.pending_type = ''
        db.session.commit()

        log_operation(get_jwt_identity(), '通过审核', 'bookmark', bookmark.id, f'通过审核并发布到分类: {bookmark.title} -> {category.name}')
        return jsonify(code=200, msg='approved and published', data=new_bookmark.to_dict())

    bookmark.is_public = True
    bookmark.is_blocked = False
    bookmark.is_pending_review = False
    bookmark.pending_category = ''
    bookmark.pending_type = ''
    db.session.commit()

    log_operation(get_jwt_identity(), '通过审核', 'bookmark', bookmark.id, f'通过审核: {bookmark.title}')
    return jsonify(code=200, msg='approved and public', data=bookmark.to_dict())


@bookmark_bp.route('/<int:bookmark_id>/set-pending', methods=['POST'])
@jwt_required()
@active_required
def set_pending_review(bookmark_id):
    bookmark = Bookmark.query.filter_by(id=bookmark_id, user_id=get_jwt_identity()).first()
    if not bookmark:
        return jsonify(code=404, msg='bookmark not found')

    data = request.get_json() or {}
    pending_type = data.get('type', 'public')
    if pending_type not in ('public', 'homepage'):
        pending_type = 'public'

    bookmark.is_pending_review = True
    bookmark.pending_category = bookmark.category.name if bookmark.category else ''
    bookmark.pending_type = pending_type
    db.session.commit()
    return jsonify(code=200, msg='submitted for review', data=bookmark.to_dict())


@bookmark_bp.route('/<int:bookmark_id>/reject', methods=['POST'])
@jwt_required()
@active_required
def reject_bookmark(bookmark_id):
    bookmark = Bookmark.query.get(bookmark_id)
    if not bookmark:
        return jsonify(code=404, msg='bookmark not found')

    bookmark.is_pending_review = False
    bookmark.pending_category = ''
    bookmark.pending_type = ''
    db.session.commit()

    log_operation(get_jwt_identity(), '拒绝审核', 'bookmark', bookmark.id, f'拒绝审核: {bookmark.title}')
    return jsonify(code=200, msg='rejected', data=bookmark.to_dict())
