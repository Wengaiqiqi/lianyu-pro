from datetime import datetime

from . import db


TARGET_TYPE_LABELS = {
    'bookmark': '书签',
    'category': '分类',
    'user': '用户',
    'feedback': '反馈',
    'ai_config': 'AI配置',
}

GENERIC_ACTION_ALIASES = {
    'create': '创建',
    'update': '更新',
    'delete': '删除',
    'remove': '删除',
    '创建': '创建',
    '更新': '更新',
    '修改': '修改',
    '编辑': '编辑',
    '删除': '删除',
}

ACTION_LABEL_ALIASES = {
    'approve': '通过审核',
    'reject': '拒绝审核',
    'login': '登录',
    'register': '注册',
    'logout': '注销',
    '登录': '登录',
    '注册': '注册',
    '注销': '注销',
    '提交反馈': '提交反馈',
    '回复反馈': '回复反馈',
    '回信反馈': '回信反馈',
}

TEXT_REPLACEMENTS = {
    '鐧诲綍': '登录',
    '娉ㄥ唽': '注册',
    '娉ㄩ攢': '注销',
    '淇敼': '修改',
    '鍒犻櫎': '删除',
    '鍒涘缓': '创建',
    '缂栬緫': '编辑',
    '鍥炲': '回复',
    '鍥炰俊': '回信',
    '鍙嶉': '反馈',
    '鐢ㄦ埛': '用户',
    '鍒嗙被': '分类',
    '鏍囬': '标题',
    '璇︽儏': '详情',
    '鍏ㄥ眬': '全局',
    '閾炬帴': '链接',
    '缃戝潃': '网址',
    '璧勬枡': '资料',
    '瀵嗙爜': '密码',
}

DETAIL_PREFIX_ALIASES = {
    'create:': '创建书签：',
    'update:': '更新书签：',
    'approve:': '通过审核：',
    'reject:': '拒绝审核：',
    '删除:': '删除书签：',
    '创建书签:': '创建书签：',
    '更新书签:': '更新书签：',
    '删除书签:': '删除书签：',
    '通过审核:': '通过审核：',
    '拒绝审核:': '拒绝审核：',
    '添加全局网页:': '添加全局网页：',
    '创建分类:': '创建分类：',
    '编辑分类:': '编辑分类：',
    '删除分类:': '删除分类：',
    '创建全局分类:': '创建全局分类：',
    '编辑全局分类:': '编辑全局分类：',
    '删除全局分类:': '删除全局分类：',
    '反馈标题:': '反馈标题：',
    '回信反馈:': '回信反馈：',
}


def _normalize_text(value):
    text = str(value or '').strip()
    if not text:
        return ''

    for source, target in TEXT_REPLACEMENTS.items():
        text = text.replace(source, target)

    return text


def _is_unknown_marker(value):
    normalized = str(value or '').strip()
    return bool(normalized) and set(normalized) == {'?'}


def _normalize_target_type(value):
    normalized = _normalize_text(value).lower()
    return TARGET_TYPE_LABELS.get(normalized, _normalize_text(value))


def _normalize_action(value, target_type):
    normalized = _normalize_text(value)
    normalized_lower = normalized.lower()
    target_label = _normalize_target_type(target_type)

    if _is_unknown_marker(normalized):
        return f'{target_label}操作' if target_label else '操作记录'

    if normalized_lower in ACTION_LABEL_ALIASES:
        return ACTION_LABEL_ALIASES[normalized_lower]
    if normalized in ACTION_LABEL_ALIASES:
        return ACTION_LABEL_ALIASES[normalized]

    if normalized_lower in GENERIC_ACTION_ALIASES:
        verb = GENERIC_ACTION_ALIASES[normalized_lower]
        return f'{verb}{target_label}' if target_label else verb
    if normalized in GENERIC_ACTION_ALIASES:
        verb = GENERIC_ACTION_ALIASES[normalized]
        return f'{verb}{target_label}' if target_label else verb

    return normalized


def _normalize_detail(value, target_type=''):
    normalized = _normalize_text(value)
    normalized_lower = normalized.lower()

    for source, target in DETAIL_PREFIX_ALIASES.items():
        if normalized_lower.startswith(source.lower()):
            return f'{target}{normalized[len(source):].lstrip()}'

    if ':' in normalized:
        prefix, suffix = normalized.split(':', 1)
        if _is_unknown_marker(prefix):
            target_label = _normalize_target_type(target_type)
            if target_label and suffix.strip():
                return f'{target_label}操作：{suffix.strip()}'
            if target_label:
                return f'{target_label}操作'

    if '：' in normalized:
        prefix, suffix = normalized.split('：', 1)
        if _is_unknown_marker(prefix):
            target_label = _normalize_target_type(target_type)
            if target_label and suffix.strip():
                return f'{target_label}操作：{suffix.strip()}'
            if target_label:
                return f'{target_label}操作'

    if _is_unknown_marker(normalized):
        target_label = _normalize_target_type(target_type)
        return f'{target_label}操作' if target_label else '操作记录'

    return normalized


class OperationLog(db.Model):
    __tablename__ = 'operation_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)
    target_type = db.Column(db.String(50), default='')
    target_id = db.Column(db.Integer, nullable=True)
    detail = db.Column(db.Text, default='')
    ip_address = db.Column(db.String(50), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='logs')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else None,
            'is_admin_log': self.user.role == 'admin' if self.user else False,
            'action': _normalize_action(self.action, self.target_type),
            'target_type': _normalize_target_type(self.target_type),
            'target_id': self.target_id,
            'detail': _normalize_detail(self.detail, self.target_type),
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
