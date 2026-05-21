from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import db
from models.user import User
from models.bookmark import Bookmark
from models.category import Category
from models.feedback import Feedback
from models.feedback_message import FeedbackMessage
from models.log import OperationLog
from models.user_interest import UserInterest
from models.ai_config import AIConfig
from utils.auth import admin_required, log_operation
from utils.ai_service import test_connection
from utils.scraper import fetch_url_info
from flask_jwt_extended import get_jwt_identity

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required
def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    keyword = request.args.get('keyword', '').strip()

    query = User.query
    if keyword:
        query = query.filter(User.username.like(f'%{keyword}%'))
    query = query.order_by(User.created_at.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    users = []
    for u in pagination.items:
        d = u.to_dict()
        d['bookmark_count'] = Bookmark.query.filter_by(user_id=u.id).count()
        users.append(d)

    return jsonify(code=200, data={
        'items': users,
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
    })


@admin_bp.route('/users/<int:user_id>/status', methods=['PUT'])
@jwt_required()
@admin_required
def toggle_user_status(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify(code=404, msg='用户不存在')
    if user.role == 'admin':
        return jsonify(code=400, msg='不能禁用管理员账户')

    user.is_active = not user.is_active
    db.session.commit()

    admin_id = int(get_jwt_identity())
    status = '启用' if user.is_active else '禁用'
    log_operation(admin_id, f'{status}用户', 'user', user.id, f'{status}用户: {user.username}')
    return jsonify(code=200, msg=f'已{status}用户', data=user.to_dict())


@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify(code=404, msg='用户不存在')
    if user.role == 'admin':
        return jsonify(code=400, msg='不能删除管理员账户')

    admin_id = int(get_jwt_identity())
    username = user.username

    # Cascading delete manually
    Bookmark.query.filter_by(user_id=user.id).delete()
    Category.query.filter_by(user_id=user.id).delete()
    UserInterest.query.filter_by(user_id=user.id).delete()
    Feedback.query.filter_by(user_id=user.id).delete()
    OperationLog.query.filter_by(user_id=user.id).delete()

    db.session.delete(user)
    db.session.commit()

    log_operation(admin_id, '删除用户', 'user', user_id, f'管理员删除了用户: {username}')
    return jsonify(code=200, msg='用户删除成功')


@admin_bp.route('/feedbacks', methods=['GET'])
@jwt_required()
@admin_required
def get_feedbacks():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    keyword = request.args.get('keyword', '').strip()
    status = request.args.get('status', '').strip()

    query = Feedback.query.join(User, Feedback.user_id == User.id).filter(
        Feedback.is_deleted_by_admin == False,
        Feedback.is_deleted_by_user == False,
    )
    if keyword:
        kw = f'%{keyword}%'
        query = query.filter(db.or_(
            Feedback.subject.like(kw),
            Feedback.content.like(kw),
            Feedback.contact.like(kw),
            User.username.like(kw),
            User.nickname.like(kw),
        ))
    if status == 'pending':
        query = query.filter(Feedback.status == 'pending')
    elif status == 'replied':
        query = query.filter(Feedback.status == 'replied')

    query = query.order_by(Feedback.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify(code=200, data={
        'items': [item.to_dict() for item in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
    })


@admin_bp.route('/feedbacks/<int:feedback_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_feedback(feedback_id):
    feedback = Feedback.query.get(feedback_id)
    if not feedback:
        return jsonify(code=404, msg='反馈不存在')

    admin_id = int(get_jwt_identity())
    subject = feedback.subject
    target_name = (
        (feedback.user.nickname or feedback.user.username)
        if feedback.user else str(feedback.user_id)
    )

    feedback.is_deleted_by_admin = True
    db.session.commit()

    log_operation(admin_id, '删除反馈', 'feedback', feedback_id, f'删除用户 {target_name} 的反馈: {subject}')
    return jsonify(code=200, msg='反馈已删除')


@admin_bp.route('/feedbacks/unread-count', methods=['GET'])
@jwt_required()
@admin_required
def get_unread_feedback_count():
    unread_count = Feedback.query.filter(
        Feedback.status == 'pending',
        Feedback.is_deleted_by_admin == False,
        Feedback.is_deleted_by_user == False,
    ).count()
    return jsonify(code=200, data={'unread_count': unread_count})


@admin_bp.route('/feedbacks/<int:feedback_id>/reply', methods=['PUT'])
@jwt_required()
@admin_required
def reply_feedback(feedback_id):
    feedback = Feedback.query.get(feedback_id)
    if not feedback:
        return jsonify(code=404, msg='反馈不存在')

    data = request.get_json() or {}
    reply = (data.get('reply') or '').strip()
    if not reply:
        return jsonify(code=400, msg='回复内容不能为空')
    if len(reply) > 5000:
        return jsonify(code=400, msg='回复内容不能超过 5000 个字符')

    admin_id = int(get_jwt_identity())
    feedback.admin_reply = reply
    feedback.status = 'replied'
    feedback.replied_by = admin_id
    feedback.replied_at = datetime.utcnow()
    feedback.is_read_by_user = False
    db.session.add(FeedbackMessage(
        feedback_id=feedback.id,
        sender_type='admin',
        sender_id=admin_id,
        content=reply,
        created_at=feedback.replied_at,
    ))
    db.session.commit()

    target_name = (
        (feedback.user.nickname or feedback.user.username)
        if feedback.user else str(feedback.user_id)
    )
    log_operation(
        admin_id,
        '回复反馈',
        'feedback',
        feedback.id,
        f'回复用户 {target_name} 的反馈: {feedback.subject}'
    )
    return jsonify(code=200, msg='回复已发送', data=feedback.to_dict())


@admin_bp.route('/bookmarks', methods=['GET'])
@jwt_required()
@admin_required
def get_all_bookmarks():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    keyword = request.args.get('keyword', '').strip()
    status = request.args.get('status', '')

    query = Bookmark.query
    if keyword:
        kw = f'%{keyword}%'
        query = query.filter(db.or_(
            Bookmark.title.like(kw),
            Bookmark.url.like(kw),
        ))
    if status == 'blocked':
        query = query.filter_by(is_blocked=True)
    elif status == 'normal':
        query = query.filter_by(is_blocked=False)

    query = query.order_by(Bookmark.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify(code=200, data={
        'items': [b.to_dict() for b in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
    })


@admin_bp.route('/bookmarks/<int:bookmark_id>/block', methods=['PUT'])
@jwt_required()
@admin_required
def toggle_block_bookmark(bookmark_id):
    bookmark = Bookmark.query.get(bookmark_id)
    if not bookmark:
        return jsonify(code=404, msg='网址不存在')

    bookmark.is_blocked = not bookmark.is_blocked
    db.session.commit()

    admin_id = get_jwt_identity()
    action = '屏蔽' if bookmark.is_blocked else '取消屏蔽'
    log_operation(admin_id, f'{action}网址', 'bookmark', bookmark.id, f'{action}: {bookmark.title}')
    return jsonify(code=200, msg=f'已{action}', data=bookmark.to_dict())


@admin_bp.route('/bookmarks/<int:bookmark_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_bookmark(bookmark_id):
    bookmark = Bookmark.query.get(bookmark_id)
    if not bookmark:
        return jsonify(code=404, msg='网址不存在')

    admin_id = get_jwt_identity()
    title = bookmark.title
    db.session.delete(bookmark)
    db.session.commit()

    log_operation(admin_id, '删除链接', 'bookmark', bookmark_id, f'管理员删除链接: {title}')
    return jsonify(code=200, msg='删除成功')


@admin_bp.route('/categories', methods=['GET'])
@jwt_required()
@admin_required
def get_global_categories():
    categories = Category.query.filter_by(user_id=None, parent_id=None).order_by(Category.sort_order).all()
    return jsonify(code=200, data=[c.to_dict(include_children=True) for c in categories])


@admin_bp.route('/categories', methods=['POST'])
@jwt_required()
@admin_required
def create_global_category():
    data = request.get_json()
    name = data.get('name', '').strip()
    if not name:
        return jsonify(code=400, msg='分类名称不能为空')

    category = Category(
        name=name,
        description=data.get('description', ''),
        parent_id=data.get('parent_id'),
        user_id=None,
        sort_order=data.get('sort_order', 0),
    )
    db.session.add(category)
    db.session.commit()

    admin_id = get_jwt_identity()
    log_operation(admin_id, '创建全局分类', 'category', category.id, f'创建全局分类: {name}')
    return jsonify(code=200, msg='创建成功', data=category.to_dict())


@admin_bp.route('/categories/<int:category_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_global_category(category_id):
    category = Category.query.filter_by(id=category_id, user_id=None).first()
    if not category:
        return jsonify(code=404, msg='全局分类不存在')

    data = request.get_json()
    if 'name' in data:
        category.name = data['name'].strip()
    if 'description' in data:
        category.description = data['description']
    if 'parent_id' in data:
        category.parent_id = data['parent_id']
    if 'sort_order' in data:
        category.sort_order = data['sort_order']

    db.session.commit()

    admin_id = get_jwt_identity()
    log_operation(admin_id, '编辑全局分类', 'category', category.id, f'编辑全局分类: {category.name}')
    return jsonify(code=200, msg='更新成功', data=category.to_dict())


@admin_bp.route('/categories/<int:category_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_global_category(category_id):
    category = Category.query.filter_by(id=category_id, user_id=None).first()
    if not category:
        return jsonify(code=404, msg='全局分类不存在')
    if category.children:
        return jsonify(code=400, msg='该分类下有子分类，请先删除子分类')

    name = category.name
    db.session.delete(category)
    db.session.commit()

    admin_id = get_jwt_identity()
    log_operation(admin_id, '删除全局分类', 'category', category_id, f'删除全局分类: {name}')
    return jsonify(code=200, msg='删除成功')


@admin_bp.route('/statistics', methods=['GET'])
@jwt_required()
@admin_required
def get_statistics():
    total_users = User.query.count()
    total_bookmarks = Bookmark.query.count()
    global_root_categories = Category.query.filter_by(user_id=None, parent_id=None).order_by(Category.sort_order).all()
    total_categories = len(global_root_categories)
    blocked_bookmarks = Bookmark.query.filter_by(is_blocked=True).count()
    active_users = User.query.filter_by(is_active=True, role='user').count()

    # 计算总访问量
    total_visits = db.session.query(db.func.sum(Bookmark.visits)).scalar() or 0

    today = datetime.utcnow().date()
    user_growth = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        next_day = day + timedelta(days=1)
        count = User.query.filter(
            User.created_at >= datetime.combine(day, datetime.min.time()),
            User.created_at < datetime.combine(next_day, datetime.min.time()),
        ).count()
        user_growth.append({'date': day.isoformat(), 'count': count})

    category_distribution = []
    for cat in global_root_categories:
        category_ids = cat.get_descendant_ids()
        count = Bookmark.query.filter(Bookmark.category_id.in_(category_ids)).count()
        category_distribution.append((cat.name, count))

    top_users = db.session.query(
        User.username, db.func.count(Bookmark.id).label('count')
    ).join(Bookmark, Bookmark.user_id == User.id).group_by(
        User.id
    ).order_by(db.text('count DESC')).limit(10).all()

    # 热门网址排行
    top_bookmarks = Bookmark.query.filter_by(is_blocked=False).order_by(
        Bookmark.visits.desc()
    ).limit(10).all()

    return jsonify(code=200, data={
        'total_users': total_users,
        'total_bookmarks': total_bookmarks,
        'total_categories': total_categories,
        'blocked_bookmarks': blocked_bookmarks,
        'active_users': active_users,
        'total_visits': total_visits,
        'user_growth': user_growth,
        'category_distribution': [{'name': name, 'count': count} for name, count in category_distribution],
        'top_users': [{'username': name, 'count': count} for name, count in top_users],
        'top_bookmarks': [{'id': b.id, 'title': b.title, 'visits': b.visits} for b in top_bookmarks],
    })


@admin_bp.route('/logs', methods=['GET'])
@jwt_required()
@admin_required
def get_logs():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    action = request.args.get('action', '').strip()
    username = request.args.get('username', '').strip()

    query = OperationLog.query
    if action:
        query = query.filter(OperationLog.action.like(f'%{action}%'))
    if username:
        query = query.join(User).filter(User.username.like(f'%{username}%'))
    query = query.order_by(OperationLog.created_at.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify(code=200, data={
        'items': [log.to_dict() for log in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
    })


@admin_bp.route('/logs/<int:log_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_log(log_id):
    log = OperationLog.query.get(log_id)
    if not log:
        return jsonify(code=404, msg='日志不存在')

    # 管理员操作日志不可删除
    if log.target_type == 'admin' or log.target_type == 'system':
        return jsonify(code=400, msg='管理员操作日志不可删除')
    # 检查操作用户是否为管理员
    if log.user and log.user.role == 'admin':
        return jsonify(code=400, msg='管理员操作日志不可删除')

    admin_id = int(get_jwt_identity())
    db.session.delete(log)
    db.session.commit()

    log_operation(admin_id, '删除日志', 'log', log_id, f'删除操作日志 ID: {log_id}')
    return jsonify(code=200, msg='日志已删除')


@admin_bp.route('/logs/date-range', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_logs_by_date_range():
    data = request.get_json() or {}
    start_date = data.get('start_date', '').strip()
    end_date = data.get('end_date', '').strip()

    if not start_date or not end_date:
        return jsonify(code=400, msg='请选择开始和结束日期')

    # 先找出符合条件的非管理员日志ID
    admin_user_ids = [u.id for u in User.query.filter_by(role='admin').all()]

    query = OperationLog.query.filter(
        OperationLog.created_at >= start_date,
        OperationLog.created_at <= end_date + ' 23:59:59',
    )
    if admin_user_ids:
        query = query.filter(~OperationLog.user_id.in_(admin_user_ids))

    deleted_count = query.delete(synchronize_session=False)
    db.session.commit()

    admin_id = int(get_jwt_identity())
    log_operation(admin_id, '批量删除日志', 'log', 0, f'按时间范围删除了 {deleted_count} 条日志（{start_date} 至 {end_date}）')

    return jsonify(code=200, msg=f'已删除 {deleted_count} 条日志', data={'deleted_count': deleted_count})


@admin_bp.route('/ai-config', methods=['GET'])
@jwt_required()
@admin_required
def get_ai_config():
    config = AIConfig.get_config()
    return jsonify(code=200, data=config.to_dict(hide_key=True))


@admin_bp.route('/ai-config', methods=['PUT'])
@jwt_required()
@admin_required
def update_ai_config():
    config = AIConfig.get_config()
    data = request.get_json()

    if 'api_url' in data:
        config.api_url = data['api_url'].strip().rstrip('/')
    if 'api_key' in data and data['api_key'] and not data['api_key'].startswith('***'):
        config.api_key = data['api_key'].strip()
    if 'model_name' in data:
        config.model_name = data['model_name'].strip()
    if 'enabled' in data:
        config.enabled = bool(data['enabled'])

    db.session.commit()

    admin_id = get_jwt_identity()
    log_operation(admin_id, '更新AI配置', 'ai_config', config.id, '更新AI模型配置')
    return jsonify(code=200, msg='配置已保存', data=config.to_dict(hide_key=True))


@admin_bp.route('/ai-config/test', methods=['POST'])
@jwt_required()
@admin_required
def test_ai_config():
    data = request.get_json()
    api_url = data.get('api_url', '').strip().rstrip('/')
    api_key = data.get('api_key', '').strip()
    model_name = data.get('model_name', '').strip()

    if not api_url or not api_key or not model_name:
        return jsonify(code=400, msg='请填写完整的 API 配置')

    if api_key.startswith('***'):
        config = AIConfig.get_config()
        api_key = config.api_key

    success, message = test_connection(api_url, api_key, model_name)
    if success:
        return jsonify(code=200, msg=f'连接成功: {message}')
    return jsonify(code=400, msg=message)


@admin_bp.route('/global-bookmarks', methods=['POST'])
@jwt_required()
@admin_required
def create_global_bookmark():
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        favicon = data.get('favicon', '').strip()
        category_id = data.get('category_id')

        if not url:
            return jsonify(code=400, msg='URL不能为空')
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        # 如果没有标题，尝试抓取
        if not title:
            try:
                info = fetch_url_info(url)
                title = info.get('title', '') or url
                description = description or info.get('description', '')
                favicon = favicon or info.get('favicon', '')
            except Exception as e:
                title = url

        if not title:
            return jsonify(code=400, msg='无法获取网页标题，请手动输入')

        bookmark = Bookmark(
            title=title,
            url=url,
            description=description,
            favicon=favicon,
            user_id=None,
            category_id=category_id,
            is_public=True,
        )
        db.session.add(bookmark)
        db.session.commit()

        admin_id = get_jwt_identity()
        log_operation(admin_id, '添加全局网页', 'bookmark', bookmark.id, f'添加全局网页: {title}')
        return jsonify(code=200, msg='添加成功', data=bookmark.to_dict())
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify(code=500, msg=f'服务器错误: {str(e)}')
