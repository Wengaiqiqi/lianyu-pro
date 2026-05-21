from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db
from models.user import User
from utils.auth import log_operation

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    email = data.get('email', '').strip()

    if not username or not password:
        return jsonify(code=400, msg='用户名和密码不能为空')
    if len(username) < 3 or len(username) > 20:
        return jsonify(code=400, msg='用户名长度为3-20个字符')
    if len(password) < 6:
        return jsonify(code=400, msg='密码长度至少6个字符')
    if User.query.filter_by(username=username).first():
        return jsonify(code=400, msg='用户名已存在')

    user = User(username=username, email=email, nickname=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    
    # 给新用户创建默认分类
    from models.category import Category
    default_categories = ['技术', '工具', '学习', '娱乐', '新闻', '社交', '购物', '其他']
    for i, name in enumerate(default_categories):
        cat = Category(name=name, user_id=user.id, sort_order=i)
        db.session.add(cat)
    db.session.commit()

    log_operation(user.id, '注册', 'user', user.id, f'用户 {username} 注册成功')
    return jsonify(code=200, msg='注册成功', data=user.to_dict())


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        return jsonify(code=400, msg='用户名和密码不能为空')

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify(code=401, msg='用户名或密码错误')
    if not user.is_active:
        return jsonify(code=403, msg='账户已被禁用，请联系管理员')

    token = create_access_token(identity=str(user.id))
    log_operation(user.id, '登录', 'user', user.id, f'用户 {username} 登录成功')
    return jsonify(code=200, msg='登录成功', data={
        'token': token,
        'user': user.to_dict(),
    })


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user:
        log_operation(user.id, '注销', 'user', user.id, f'用户 {user.username} 注销登录')
    return jsonify(code=200, msg='注销成功')


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify(code=404, msg='用户不存在')
    return jsonify(code=200, data=user.to_dict())
