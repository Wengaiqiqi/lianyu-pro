from collections import OrderedDict
from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required, verify_jwt_in_request

from models import db
from models.bookmark import Bookmark
from models.category import Category
from models.feedback import Feedback
from models.feedback_message import FeedbackMessage
from models.user import User
from models.user_social import PublicUserLike, UserFollow
from utils.auth import active_required, log_operation

user_bp = Blueprint('user', __name__)


def _get_public_user_metrics(current_user_id=None):
    public_rows = db.session.query(
        Bookmark.user_id.label('user_id'),
        db.func.count(Bookmark.id).label('public_count')
    ).filter(
        Bookmark.user_id.isnot(None),
        Bookmark.is_public.is_(True),
        Bookmark.is_blocked.is_(False)
    ).group_by(Bookmark.user_id).all()

    if not public_rows:
        return []

    user_ids = [row.user_id for row in public_rows]
    public_count_map = {row.user_id: int(row.public_count or 0) for row in public_rows}

    follow_rows = db.session.query(
        UserFollow.followed_id.label('user_id'),
        db.func.count(UserFollow.id).label('follower_count')
    ).filter(UserFollow.followed_id.in_(user_ids)).group_by(UserFollow.followed_id).all()
    follower_count_map = {row.user_id: int(row.follower_count or 0) for row in follow_rows}

    like_rows = db.session.query(
        PublicUserLike.target_user_id.label('user_id'),
        db.func.count(PublicUserLike.id).label('like_count')
    ).filter(PublicUserLike.target_user_id.in_(user_ids)).group_by(PublicUserLike.target_user_id).all()
    like_count_map = {row.user_id: int(row.like_count or 0) for row in like_rows}

    following_ids = set()
    liked_ids = set()
    if current_user_id:
        following_ids = {
            row.followed_id
            for row in UserFollow.query.filter(
                UserFollow.follower_id == current_user_id,
                UserFollow.followed_id.in_(user_ids)
            ).all()
        }
        liked_ids = {
            row.target_user_id
            for row in PublicUserLike.query.filter(
                PublicUserLike.user_id == current_user_id,
                PublicUserLike.target_user_id.in_(user_ids)
            ).all()
        }

    users = User.query.filter(User.id.in_(user_ids)).all()
    user_map = {user.id: user for user in users}

    result = []
    for user_id in user_ids:
        user = user_map.get(user_id)
        if not user:
            continue
        result.append({
            'id': user.id,
            'username': user.username,
            'nickname': user.nickname,
            'avatar': user.avatar,
            'public_count': public_count_map.get(user.id, 0),
            'follower_count': follower_count_map.get(user.id, 0),
            'like_count': like_count_map.get(user.id, 0),
            'is_following': user.id in following_ids,
            'is_liked': user.id in liked_ids,
        })
    return result


def _serialize_feedback_list(query):
    return [item.to_dict() for item in query.order_by(Feedback.updated_at.desc(), Feedback.id.desc()).all()]


def _append_feedback_message(feedback, sender_type, sender_id, content, created_at=None):
    message = FeedbackMessage(
        feedback_id=feedback.id,
        sender_type=sender_type,
        sender_id=sender_id,
        content=content,
        created_at=created_at or datetime.utcnow(),
    )
    db.session.add(message)
    return message


@user_bp.route('/profile', methods=['GET'])
@jwt_required()
@active_required
def get_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify(code=404, msg='用户不存在')
    return jsonify(code=200, data=user.to_dict())


@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
@active_required
def update_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify(code=404, msg='用户不存在')

    data = request.get_json() or {}
    if 'username' in data:
        new_username = (data.get('username') or '').strip()
        if new_username and new_username != user.username:
            existing_user = User.query.filter_by(username=new_username).first()
            if existing_user:
                return jsonify(code=400, msg='用户名已被占用')
            user.username = new_username
    if 'email' in data:
        user.email = (data.get('email') or '').strip()
    if 'avatar' in data:
        user.avatar = (data.get('avatar') or '').strip()
    if 'nickname' in data:
        user.nickname = (data.get('nickname') or '').strip()

    db.session.commit()
    log_operation(user_id, '修改资料', 'user', user.id, '修改个人资料')
    return jsonify(code=200, msg='更新成功', data=user.to_dict())


@user_bp.route('/password', methods=['PUT'])
@jwt_required()
@active_required
def change_password():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify(code=404, msg='用户不存在')

    data = request.get_json() or {}
    old_password = data.get('old_password', '')
    new_password = data.get('new_password', '')

    if not user.check_password(old_password):
        return jsonify(code=400, msg='原密码错误')
    if len(new_password) < 6:
        return jsonify(code=400, msg='新密码长度至少 6 个字符')

    user.set_password(new_password)
    db.session.commit()
    log_operation(user_id, '修改密码', 'user', user.id, '修改密码')
    return jsonify(code=200, msg='密码修改成功')


@user_bp.route('/stats', methods=['GET'])
@jwt_required()
@active_required
def get_stats():
    user_id = get_jwt_identity()

    total_bookmarks = Bookmark.query.filter_by(user_id=user_id).count()
    total_categories = Category.query.filter_by(user_id=user_id).count()
    public_bookmarks = Bookmark.query.filter_by(user_id=user_id, is_public=True).count()
    following_public_users = UserFollow.query.filter_by(follower_id=user_id).count()

    uncategorized_count = Bookmark.query.filter_by(user_id=user_id, category_id=None).count()
    categorized_bookmarks = Bookmark.query.filter(
        Bookmark.user_id == user_id,
        Bookmark.category_id.isnot(None)
    ).all()

    category_counter = OrderedDict()
    for bookmark in categorized_bookmarks:
        if not bookmark.category:
            continue
        root_category = bookmark.category.get_root_category()
        if bookmark.category.id != root_category.id:
            continue
        root_name = root_category.name
        category_counter[root_name] = category_counter.get(root_name, 0) + 1

    category_data = [{'name': name, 'count': count} for name, count in category_counter.items()]
    if uncategorized_count > 0:
        category_data.append({'name': '未分类', 'count': uncategorized_count})

    recent_bookmarks = Bookmark.query.filter_by(user_id=user_id).order_by(
        Bookmark.created_at.desc()
    ).limit(5).all()

    return jsonify(code=200, data={
        'total_bookmarks': total_bookmarks,
        'total_categories': total_categories,
        'public_bookmarks': public_bookmarks,
        'following_public_users': following_public_users,
        'category_stats': category_data,
        'recent_bookmarks': [bookmark.to_dict() for bookmark in recent_bookmarks],
    })


@user_bp.route('/feedbacks', methods=['GET'])
@jwt_required()
@active_required
def get_feedbacks():
    user_id = int(get_jwt_identity())
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    per_page = min(per_page, 100)
    query = Feedback.query.filter_by(user_id=user_id, is_deleted_by_user=False)
    pagination = query.order_by(Feedback.updated_at.desc(), Feedback.id.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return jsonify(code=200, data={
        'items': [item.to_dict() for item in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
    })


@user_bp.route('/feedbacks/<int:feedback_id>', methods=['DELETE'])
@jwt_required()
@active_required
def delete_feedback(feedback_id):
    user_id = int(get_jwt_identity())
    feedback = Feedback.query.filter_by(id=feedback_id, user_id=user_id).first()
    if not feedback:
        return jsonify(code=404, msg='反馈不存在')

    subject = feedback.subject
    feedback.is_deleted_by_user = True
    for message in feedback.messages:
        message.is_deleted = True
    db.session.commit()

    log_operation(user_id, '删除反馈', 'feedback', feedback_id, f'删除反馈: {subject}')
    return jsonify(code=200, msg='反馈已删除')


@user_bp.route('/feedbacks', methods=['POST'])
@jwt_required()
@active_required
def create_feedback():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify(code=404, msg='用户不存在')

    data = request.get_json() or {}
    subject = (data.get('subject') or '').strip()
    content = (data.get('content') or '').strip()
    contact = (data.get('contact') or '').strip()

    if not subject:
        return jsonify(code=400, msg='反馈标题不能为空')
    if not content:
        return jsonify(code=400, msg='反馈内容不能为空')
    if len(subject) > 200:
        return jsonify(code=400, msg='反馈标题不能超过 200 个字符')
    if len(content) > 5000:
        return jsonify(code=400, msg='反馈内容不能超过 5000 个字符')
    if len(contact) > 120:
        return jsonify(code=400, msg='联系方式不能超过 120 个字符')

    feedback = Feedback(
        user_id=user.id,
        subject=subject,
        content=content,
        contact=contact,
        status='pending',
        is_read_by_user=True,
    )
    db.session.add(feedback)
    db.session.flush()
    _append_feedback_message(feedback, 'user', user.id, content)
    db.session.commit()

    log_operation(user.id, '提交反馈', 'feedback', feedback.id, f'反馈标题: {subject}')
    return jsonify(code=200, msg='反馈已提交', data=feedback.to_dict())


@user_bp.route('/mailbox', methods=['GET'])
@jwt_required()
@active_required
def get_mailbox():
    user_id = int(get_jwt_identity())
    items = _serialize_feedback_list(
        Feedback.query.filter(
            Feedback.user_id == user_id,
            db.or_(
                Feedback.admin_reply != '',
                Feedback.messages.any(),
            ),
            Feedback.is_deleted_by_user == False,
        )
    )
    unread_count = Feedback.query.filter(
        Feedback.user_id == user_id,
        Feedback.admin_reply != '',
        Feedback.is_read_by_user.is_(False),
        Feedback.is_deleted_by_user == False,
    ).count()
    return jsonify(code=200, data={'items': items, 'unread_count': unread_count})


@user_bp.route('/mailbox/<int:feedback_id>/reply', methods=['PUT'])
@jwt_required()
@active_required
def reply_mailbox(feedback_id):
    user_id = int(get_jwt_identity())
    feedback = Feedback.query.filter_by(id=feedback_id, user_id=user_id, is_deleted_by_user=False).first()
    if not feedback:
        return jsonify(code=404, msg='信件不存在')

    has_admin_reply = feedback.admin_reply and feedback.admin_reply.strip()
    has_admin_messages = any(m.sender_type == 'admin' for m in feedback.messages if not m.is_deleted)
    if feedback.is_deleted_by_admin and not has_admin_reply and not has_admin_messages:
        return jsonify(code=400, msg='该信件暂时不能回信')

    data = request.get_json() or {}
    reply = (data.get('reply') or '').strip()
    if not reply:
        return jsonify(code=400, msg='回信内容不能为空')
    if len(reply) > 5000:
        return jsonify(code=400, msg='回信内容不能超过 5000 个字符')

    feedback.user_reply = reply
    feedback.user_replied_at = datetime.utcnow()
    feedback.status = 'pending'
    if feedback.is_deleted_by_admin:
        feedback.is_deleted_by_admin = False
    _append_feedback_message(feedback, 'user', user_id, reply, feedback.user_replied_at)
    db.session.commit()

    log_operation(user_id, '回信反馈', 'feedback', feedback.id, f'回信反馈: {feedback.subject}')
    return jsonify(code=200, msg='回信已发送', data=feedback.to_dict())


@user_bp.route('/mailbox/unread-count', methods=['GET'])
@jwt_required()
@active_required
def get_mailbox_unread_count():
    user_id = int(get_jwt_identity())
    unread_count = Feedback.query.filter(
        Feedback.user_id == user_id,
        Feedback.admin_reply != '',
        Feedback.is_read_by_user.is_(False),
        Feedback.is_deleted_by_user == False,
    ).count()
    return jsonify(code=200, data={'unread_count': unread_count})


@user_bp.route('/mailbox/<int:feedback_id>/read', methods=['PUT'])
@jwt_required()
@active_required
def mark_mailbox_read(feedback_id):
    user_id = int(get_jwt_identity())
    feedback = Feedback.query.filter(
        Feedback.id == feedback_id,
        Feedback.user_id == user_id,
        db.or_(
            Feedback.admin_reply != '',
            Feedback.messages.any(),
        ),
        Feedback.is_deleted_by_user == False,
    ).first()
    if not feedback:
        return jsonify(code=404, msg='信件不存在')

    updated = 0
    if not feedback.is_read_by_user:
        feedback.is_read_by_user = True
        updated = 1
        db.session.commit()

    unread_count = Feedback.query.filter(
        Feedback.user_id == user_id,
        Feedback.admin_reply != '',
        Feedback.is_read_by_user.is_(False),
        Feedback.is_deleted_by_user == False,
    ).count()
    return jsonify(code=200, msg='已更新信件状态', data={'updated': updated, 'unread_count': unread_count})


@user_bp.route('/public-users', methods=['GET'])
def get_public_users():
    current_user_id = None
    try:
        verify_jwt_in_request(optional=True)
        current_user_id = get_jwt_identity()
    except Exception:
        current_user_id = None

    return jsonify(code=200, data=_get_public_user_metrics(current_user_id))


@user_bp.route('/following/public-users', methods=['GET'])
@jwt_required()
@active_required
def get_following_public_users():
    user_id = get_jwt_identity()
    all_public_users = _get_public_user_metrics(user_id)
    followed_users = [user for user in all_public_users if user['is_following']]
    return jsonify(code=200, data=followed_users)


@user_bp.route('/public-users/rankings', methods=['GET'])
def get_public_user_rankings():
    metric = request.args.get('metric', 'followers')
    limit = request.args.get('limit', 8, type=int)
    current_user_id = None

    try:
        verify_jwt_in_request(optional=True)
        current_user_id = get_jwt_identity()
    except Exception:
        current_user_id = None

    users = _get_public_user_metrics(current_user_id)
    metric_map = {
        'followers': 'follower_count',
        'likes': 'like_count',
        'public': 'public_count',
    }
    metric_key = metric_map.get(metric, 'follower_count')
    users.sort(
        key=lambda item: (
            -int(item.get(metric_key, 0)),
            -int(item.get('public_count', 0)),
            item.get('nickname') or item.get('username') or ''
        )
    )
    return jsonify(code=200, data={
        'metric': metric,
        'items': users[:limit],
    })


@user_bp.route('/public-users/<int:target_user_id>/follow', methods=['POST'])
@jwt_required()
@active_required
def follow_public_user(target_user_id):
    user_id = get_jwt_identity()
    if user_id == target_user_id:
        return jsonify(code=400, msg='不能关注自己')

    target_user = User.query.get(target_user_id)
    if not target_user:
        return jsonify(code=404, msg='目标用户不存在')

    existing_follow = UserFollow.query.filter_by(
        follower_id=user_id,
        followed_id=target_user_id
    ).first()
    if existing_follow:
        follower_count = UserFollow.query.filter_by(followed_id=target_user_id).count()
        return jsonify(code=200, msg='已关注', data={'is_following': True, 'follower_count': follower_count})

    follow = UserFollow(follower_id=user_id, followed_id=target_user_id)
    db.session.add(follow)
    db.session.commit()
    log_operation(user_id, '关注公开用户', 'user', target_user_id, f'关注用户: {target_user.username}')

    follower_count = UserFollow.query.filter_by(followed_id=target_user_id).count()
    return jsonify(code=200, msg='关注成功', data={'is_following': True, 'follower_count': follower_count})


@user_bp.route('/public-users/<int:target_user_id>/follow', methods=['DELETE'])
@jwt_required()
@active_required
def unfollow_public_user(target_user_id):
    user_id = get_jwt_identity()
    follow = UserFollow.query.filter_by(
        follower_id=user_id,
        followed_id=target_user_id
    ).first()
    if not follow:
        follower_count = UserFollow.query.filter_by(followed_id=target_user_id).count()
        return jsonify(code=200, msg='未关注', data={'is_following': False, 'follower_count': follower_count})

    db.session.delete(follow)
    db.session.commit()
    log_operation(user_id, '取消关注公开用户', 'user', target_user_id, f'取消关注用户 ID: {target_user_id}')

    follower_count = UserFollow.query.filter_by(followed_id=target_user_id).count()
    return jsonify(code=200, msg='已取消关注', data={'is_following': False, 'follower_count': follower_count})


@user_bp.route('/public-users/<int:target_user_id>/like', methods=['POST'])
@jwt_required()
@active_required
def like_public_user(target_user_id):
    user_id = get_jwt_identity()
    if user_id == target_user_id:
        return jsonify(code=400, msg='不能给自己点赞')

    target_user = User.query.get(target_user_id)
    if not target_user:
        return jsonify(code=404, msg='目标用户不存在')

    existing_like = PublicUserLike.query.filter_by(
        user_id=user_id,
        target_user_id=target_user_id
    ).first()
    if existing_like:
        like_count = PublicUserLike.query.filter_by(target_user_id=target_user_id).count()
        return jsonify(code=200, msg='已点赞', data={'is_liked': True, 'like_count': like_count})

    like = PublicUserLike(user_id=user_id, target_user_id=target_user_id)
    db.session.add(like)
    db.session.commit()
    log_operation(user_id, '点赞公开用户', 'user', target_user_id, f'点赞用户: {target_user.username}')

    like_count = PublicUserLike.query.filter_by(target_user_id=target_user_id).count()
    return jsonify(code=200, msg='点赞成功', data={'is_liked': True, 'like_count': like_count})


@user_bp.route('/public-users/<int:target_user_id>/like', methods=['DELETE'])
@jwt_required()
@active_required
def unlike_public_user(target_user_id):
    user_id = get_jwt_identity()
    like = PublicUserLike.query.filter_by(
        user_id=user_id,
        target_user_id=target_user_id
    ).first()
    if not like:
        like_count = PublicUserLike.query.filter_by(target_user_id=target_user_id).count()
        return jsonify(code=200, msg='未点赞', data={'is_liked': False, 'like_count': like_count})

    db.session.delete(like)
    db.session.commit()
    log_operation(user_id, '取消点赞公开用户', 'user', target_user_id, f'取消点赞用户 ID: {target_user_id}')

    like_count = PublicUserLike.query.filter_by(target_user_id=target_user_id).count()
    return jsonify(code=200, msg='已取消点赞', data={'is_liked': False, 'like_count': like_count})
