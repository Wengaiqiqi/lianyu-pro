import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, os.pardir))


def _load_env_files():
    env_files = [
        os.path.join(ROOT_DIR, '.env'),
        os.path.join(ROOT_DIR, '.env.local'),
        os.path.join(BASE_DIR, '.env'),
        os.path.join(BASE_DIR, '.env.local'),
    ]

    for env_path in env_files:
        if not os.path.exists(env_path):
            continue

        with open(env_path, 'r', encoding='utf-8') as env_file:
            for raw_line in env_file:
                line = raw_line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue

                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                if not key:
                    continue

                if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
                    value = value[1:-1]

                os.environ.setdefault(key, value)


_load_env_files()


def _get_int_env(name, default):
    value = os.environ.get(name)
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24 hours
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    TRUSTED_PROXY_COUNT = _get_int_env('TRUSTED_PROXY_COUNT', 1)
    PROXY_FIX_X_FOR = _get_int_env('PROXY_FIX_X_FOR', TRUSTED_PROXY_COUNT)
    PROXY_FIX_X_PROTO = _get_int_env('PROXY_FIX_X_PROTO', 1 if TRUSTED_PROXY_COUNT > 0 else 0)
    PROXY_FIX_X_HOST = _get_int_env('PROXY_FIX_X_HOST', 1 if TRUSTED_PROXY_COUNT > 0 else 0)
    PROXY_FIX_X_PORT = _get_int_env('PROXY_FIX_X_PORT', 0)
    PROXY_FIX_X_PREFIX = _get_int_env('PROXY_FIX_X_PREFIX', 0)
