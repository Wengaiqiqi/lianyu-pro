from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db
from models.category import Category
from utils.auth import active_required, log_operation

category_bp = Blueprint('category', __name__)


@category_bp.route('', methods=['GET'])
@jwt_required()
@active_required
def get_categories():
    user_id = get_jwt_identity()
    categories = Category.query.filter(
        Category.user_id == user_id
    ).filter_by(parent_id=None).order_by(Category.sort_order).all()

    return jsonify(code=200, data=[c.to_dict(include_children=True) for c in categories])


@category_bp.route('/admin', methods=['GET'])
@jwt_required()
@active_required
def get_admin_categories():
    """获取管理员（首页）分类"""
    categories = Category.query.filter(
        Category.user_id == None
    ).filter_by(parent_id=None).order_by(Category.sort_order).all()
    return jsonify(code=200, data=[c.to_dict(include_children=True) for c in categories])


@category_bp.route('/flat', methods=['GET'])
@jwt_required()
@active_required
def get_categories_flat():
    user_id = get_jwt_identity()
    categories = Category.query.filter(
        Category.user_id == user_id
    ).order_by(Category.sort_order).all()
    return jsonify(code=200, data=[c.to_dict() for c in categories])


@category_bp.route('', methods=['POST'])
@jwt_required()
@active_required
def create_category():
    user_id = get_jwt_identity()
    data = request.get_json()
    name = data.get('name', '').strip()

    if not name:
        return jsonify(code=400, msg='分类名称不能为空')

    parent_id = data.get('parent_id')
    if parent_id:
        parent = Category.query.get(parent_id)
        if not parent:
            return jsonify(code=400, msg='父分类不存在')

    category = Category(
        name=name,
        description=data.get('description', ''),
        parent_id=parent_id,
        user_id=user_id,
        sort_order=data.get('sort_order', 0),
    )
    db.session.add(category)
    db.session.commit()

    log_operation(user_id, '创建分类', 'category', category.id, f'创建分类: {name}')
    return jsonify(code=200, msg='创建成功', data=category.to_dict())


@category_bp.route('/<int:category_id>', methods=['PUT'])
@jwt_required()
@active_required
def update_category(category_id):
    user_id = get_jwt_identity()
    category = Category.query.filter_by(id=category_id, user_id=user_id).first()
    if not category:
        return jsonify(code=404, msg='分类不存在')

    data = request.get_json()
    if 'name' in data:
        category.name = data['name'].strip()
    if 'description' in data:
        category.description = data['description']
    if 'parent_id' in data:
        if data['parent_id'] == category.id:
            return jsonify(code=400, msg='不能将分类设为自己的子分类')
        category.parent_id = data['parent_id']
    if 'sort_order' in data:
        category.sort_order = data['sort_order']

    db.session.commit()
    log_operation(user_id, '编辑分类', 'category', category.id, f'编辑分类: {category.name}')
    return jsonify(code=200, msg='更新成功', data=category.to_dict())


@category_bp.route('/<int:category_id>', methods=['DELETE'])
@jwt_required()
@active_required
def delete_category(category_id):
    user_id = get_jwt_identity()
    category = Category.query.filter_by(id=category_id, user_id=user_id).first()
    if not category:
        return jsonify(code=404, msg='分类不存在')

    if category.children:
        return jsonify(code=400, msg='该分类下有子分类，请先删除子分类')
    if category.bookmarks.count() > 0:
        return jsonify(code=400, msg='该分类下有收藏，请先移除收藏')

    name = category.name
    db.session.delete(category)
    db.session.commit()

    log_operation(user_id, '删除分类', 'category', category_id, f'删除分类: {name}')
    return jsonify(code=200, msg='删除成功')
