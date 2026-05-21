import ipaddress
from functools import wraps
from flask import current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from models.user import User
from models.log import OperationLog
from models import db


def _normalize_ip(value):
    if not value:
        return ''

    candidate = value.strip()
    if not candidate:
        return ''

    if candidate.startswith('for='):
        candidate = candidate[4:]

    if candidate.startswith('"') and candidate.endswith('"'):
        candidate = candidate[1:-1]

    if candidate.startswith('[') and candidate.endswith(']'):
        candidate = candidate[1:-1]

    if candidate.lower() == 'unknown':
        return ''

    try:
        return str(ipaddress.ip_address(candidate))
    except ValueError:
        return ''


def _forwarded_candidates():
    forwarded_for = request.headers.get('X-Forwarded-For', '')
    candidates = []

    for item in forwarded_for.split(','):
        normalized = _normalize_ip(item)
        if normalized:
            candidates.append(normalized)

    return candidates


def _is_private_or_loopback_ip(value):
    normalized = _normalize_ip(value)
    if not normalized:
        return False

    address = ipaddress.ip_address(normalized)
    return (
        address.is_private
        or address.is_loopback
        or address.is_link_local
        or address.is_reserved
    )


def get_client_ip():
    remote_addr = _normalize_ip(request.remote_addr)
    forwarded_candidates = _forwarded_candidates()
    trusted_proxy_count = max(current_app.config.get('TRUSTED_PROXY_COUNT', 0), 0)

    if forwarded_candidates:
        if trusted_proxy_count > 0:
            client_index = max(len(forwarded_candidates) - trusted_proxy_count - 1, 0)
            return forwarded_candidates[client_index]

        if not remote_addr or _is_private_or_loopback_ip(remote_addr):
            return forwarded_candidates[0]

    real_ip = _normalize_ip(request.headers.get('X-Real-IP', ''))
    if real_ip and (not remote_addr or _is_private_or_loopback_ip(remote_addr)):
        return real_ip

    return remote_addr


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or user.role != 'admin':
            return jsonify(code=403, msg='需要管理员权限'), 403
        return fn(*args, **kwargs)
    return wrapper


def active_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or not user.is_active:
            return jsonify(code=403, msg='账户已被禁用'), 403
        return fn(*args, **kwargs)
    return wrapper


def log_operation(user_id, action, target_type='', target_id=None, detail=''):
    log = OperationLog(
        user_id=user_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        detail=detail,
        ip_address=get_client_ip() or '',
    )
    db.session.add(log)
    db.session.commit()
