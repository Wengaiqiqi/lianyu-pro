from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db
from models.bookmark import Bookmark
from models.ai_config import AIConfig
from models.user_interest import UserInterest
from utils.auth import active_required
from utils.ai_service import analyze_interests, recommend_urls, evaluate_url_safety

ai_bp = Blueprint('ai', __name__)


@ai_bp.route('/interests', methods=['GET'])
@jwt_required()
@active_required
def get_interests():
    user_id = get_jwt_identity()
    record = UserInterest.get_or_create(user_id)
    return jsonify(code=200, data=record.to_dict())


@ai_bp.route('/interests/analyze', methods=['POST'])
@jwt_required()
@active_required
def analyze():
    config = AIConfig.get_config()
    if not config.enabled or not config.api_key:
        return jsonify(code=400, msg='AI 功能未启用，请联系管理员配置')

    user_id = get_jwt_identity()
    bookmarks = Bookmark.query.filter_by(user_id=user_id).order_by(
        Bookmark.created_at.desc()
    ).limit(100).all()

    if not bookmarks:
        return jsonify(code=200, data={'interests': [], 'recommendations': [], 'analyzed_at': None},
                       msg='暂无收藏数据，请先添加收藏')

    bookmark_data = [b.to_dict() for b in bookmarks]
    try:
        interests = analyze_interests(
            config.api_url, config.api_key, config.model_name, bookmark_data
        )

        recommendations = []
        if interests:
            recommendations = recommend_urls(
                config.api_url, config.api_key, config.model_name,
                interests, bookmark_data
            )

        record = UserInterest.get_or_create(user_id)
        record.set_interests(interests)
        record.set_recommendations(recommendations)
        record.analyzed_at = datetime.utcnow()
        db.session.commit()

        return jsonify(code=200, data=record.to_dict())
    except Exception as e:
        return jsonify(code=500, msg=f'AI 分析失败: {str(e)}')


@ai_bp.route('/evaluate-url', methods=['POST'])
@jwt_required()
@active_required
def evaluate_url():
    """评估单个 URL 是否安全健康"""
    config = AIConfig.get_config()
    if not config.enabled or not config.api_key:
        return jsonify(code=400, msg='AI 功能未启用，请联系管理员配置')

    data = request.get_json()
    url = data.get('url', '').strip()
    title = data.get('title', '').strip()

    if not url:
        return jsonify(code=400, msg='URL 不能为空')

    try:
        result = evaluate_url_safety(config.api_url, config.api_key, config.model_name, url, title)
        return jsonify(code=200, data=result)
    except Exception as e:
        return jsonify(code=500, msg=f'AI 评估失败: {str(e)}')
