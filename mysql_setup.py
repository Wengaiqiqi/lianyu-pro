from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path
from urllib.parse import quote_plus

import pymysql
from flask import Flask
from sqlalchemy import create_engine, inspect, text


ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / 'backend'
SQLITE_DB_PATH = BACKEND_DIR / 'app.db'
ENV_LOCAL_PATH = ROOT_DIR / '.env.local'

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from migrations import run_migrations  # noqa: E402
from models import db  # noqa: E402
from models.ai_config import AIConfig  # noqa: E402,F401
from models.bookmark import Bookmark  # noqa: E402,F401
from models.bookmark_visit import BookmarkVisit  # noqa: E402,F401
from models.category import Category  # noqa: E402,F401
from models.log import OperationLog  # noqa: E402,F401
from models.user import User  # noqa: E402,F401
from models.user_interest import UserInterest  # noqa: E402,F401
from models.user_social import PublicUserLike, UserFollow  # noqa: E402,F401


MIGRATE_MODE = 'migrate'
RESET_MODE = 'reset'

TABLE_ORDER = [
    'users',
    'ai_config',
    'categories',
    'bookmarks',
    'operation_logs',
    'user_interests',
    'user_follows',
    'public_user_likes',
    'bookmark_visits',
]


def build_backend_app(database_url: str) -> Flask:
    app = Flask(__name__)
    app.config.update(
        SQLALCHEMY_DATABASE_URI=database_url,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    db.init_app(app)
    return app


def prompt(text_value: str, default: str | None = None, secret: bool = False) -> str:
    suffix = f' [{default}]' if default else ''
    prompt_text = f'{text_value}{suffix}: '
    if secret:
        try:
            import getpass

            value = getpass.getpass(prompt_text)
        except Exception:
            value = input(prompt_text)
    else:
        value = input(prompt_text)

    value = value.strip()
    if value:
        return value
    return default or ''


def confirm(text_value: str, default: bool = False) -> bool:
    suffix = 'Y/n' if default else 'y/N'
    value = input(f'{text_value} [{suffix}]: ').strip().lower()
    if not value:
        return default
    return value in {'y', 'yes', '是'}


def build_mysql_url(user: str, password: str, host: str, port: str, database: str) -> str:
    return (
        f'mysql+pymysql://{quote_plus(user)}:{quote_plus(password)}@'
        f'{host}:{port}/{database}?charset=utf8mb4'
    )


def build_mysql_conn_kwargs(user: str, password: str, host: str, port: str, database: str | None = None) -> dict:
    kwargs = {
        'host': host,
        'port': int(port),
        'user': user,
        'password': password,
        'charset': 'utf8mb4',
        'autocommit': True,
    }
    if database:
        kwargs['database'] = database
    return kwargs


def ensure_mysql_database(user: str, password: str, host: str, port: str, database: str) -> None:
    conn = pymysql.connect(**build_mysql_conn_kwargs(user, password, host, port))
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{database}` "
                "DEFAULT CHARACTER SET utf8mb4 DEFAULT COLLATE utf8mb4_unicode_ci"
            )
    finally:
        conn.close()


def write_env_local(database_url: str) -> None:
    lines: list[str] = []
    found = False

    if ENV_LOCAL_PATH.exists():
        existing_lines = ENV_LOCAL_PATH.read_text(encoding='utf-8').splitlines()
        for line in existing_lines:
            if line.strip().startswith('DATABASE_URL='):
                lines.append(f'DATABASE_URL={database_url}')
                found = True
            else:
                lines.append(line)

    if not found:
        lines.append(f'DATABASE_URL={database_url}')

    ENV_LOCAL_PATH.write_text('\n'.join(lines).rstrip() + '\n', encoding='utf-8')


def prepare_mysql_schema(database_url: str, reset: bool) -> None:
    app = build_backend_app(database_url)
    with app.app_context():
        if reset:
            db.drop_all()
            with db.engine.begin() as connection:
                connection.execute(text('DROP TABLE IF EXISTS schema_migrations'))
        run_migrations()


def _sqlite_ro_uri(sqlite_path: Path, immutable: bool = False) -> str:
    uri = f'file:{sqlite_path.as_posix()}?mode=ro'
    if immutable:
        uri += '&immutable=1'
    return uri


def open_sqlite_source(sqlite_path: Path) -> sqlite3.Connection:
    if not sqlite_path.exists():
        raise FileNotFoundError(f'SQLite 数据库不存在: {sqlite_path}')

    attempts = [
        ('readonly', _sqlite_ro_uri(sqlite_path, immutable=False)),
        ('readonly-immutable', _sqlite_ro_uri(sqlite_path, immutable=True)),
    ]
    last_error: Exception | None = None

    for _, uri in attempts:
        try:
            connection = sqlite3.connect(uri, uri=True)
            connection.row_factory = None
            connection.execute('SELECT name FROM sqlite_master LIMIT 1').fetchall()
            return connection
        except sqlite3.Error as exc:
            last_error = exc

    raise RuntimeError(
        f'无法读取 SQLite 源数据库 {sqlite_path}: {last_error}'
    ) from last_error


def sqlite_tables(conn: sqlite3.Connection) -> set[str]:
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    return {row[0] for row in rows}


def fetch_sqlite_rows(conn: sqlite3.Connection, table_name: str) -> tuple[list[str], list[tuple]]:
    columns = [row[1] for row in conn.execute(f'PRAGMA table_info({table_name})').fetchall()]
    if not columns:
        return [], []
    rows = conn.execute(f'SELECT {", ".join(columns)} FROM {table_name}').fetchall()
    return columns, rows


def get_table_counts_sqlite(conn: sqlite3.Connection) -> dict[str, int]:
    counts: dict[str, int] = {}
    existing_tables = sqlite_tables(conn)
    for table_name in TABLE_ORDER:
        if table_name not in existing_tables:
            continue
        counts[table_name] = conn.execute(f'SELECT COUNT(*) FROM {table_name}').fetchone()[0]
    return counts


def get_table_counts_mysql(database_url: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    engine = create_engine(database_url)
    try:
        existing_tables = set(inspect(engine).get_table_names())
        with engine.connect() as connection:
            for table_name in TABLE_ORDER:
                if table_name not in existing_tables:
                    continue
                counts[table_name] = connection.execute(
                    text(f'SELECT COUNT(*) FROM `{table_name}`')
                ).scalar_one()
    finally:
        engine.dispose()
    return counts


def copy_sqlite_to_mysql(sqlite_path: Path, database_url: str) -> dict[str, int]:
    sqlite_conn = open_sqlite_source(sqlite_path)
    engine = create_engine(database_url)
    copied_counts: dict[str, int] = {}

    try:
        existing_tables = sqlite_tables(sqlite_conn)
        mysql_tables = set(inspect(engine).get_table_names())

        with engine.begin() as mysql_conn:
            mysql_conn.execute(text('SET FOREIGN_KEY_CHECKS = 0'))
            try:
                for table_name in TABLE_ORDER:
                    if table_name not in existing_tables or table_name not in mysql_tables:
                        continue

                    columns, rows = fetch_sqlite_rows(sqlite_conn, table_name)
                    if not columns:
                        copied_counts[table_name] = 0
                        continue

                    mysql_conn.execute(text(f'TRUNCATE TABLE `{table_name}`'))
                    copied_counts[table_name] = len(rows)
                    if not rows:
                        continue

                    placeholders = ', '.join(f':{column}' for column in columns)
                    column_sql = ', '.join(f'`{column}`' for column in columns)
                    insert_sql = text(
                        f'INSERT INTO `{table_name}` ({column_sql}) VALUES ({placeholders})'
                    )
                    payload = [dict(zip(columns, row)) for row in rows]
                    mysql_conn.execute(insert_sql, payload)
            finally:
                mysql_conn.execute(text('SET FOREIGN_KEY_CHECKS = 1'))
    finally:
        sqlite_conn.close()
        engine.dispose()

    return copied_counts


def verify_mysql_migration(sqlite_path: Path, database_url: str) -> dict[str, tuple[int, int]]:
    sqlite_conn = open_sqlite_source(sqlite_path)
    try:
        sqlite_counts = get_table_counts_sqlite(sqlite_conn)
    finally:
        sqlite_conn.close()

    mysql_counts = get_table_counts_mysql(database_url)
    mismatches: dict[str, tuple[int, int]] = {}
    for table_name in TABLE_ORDER:
        sqlite_count = sqlite_counts.get(table_name, 0)
        mysql_count = mysql_counts.get(table_name, 0)
        if sqlite_count != mysql_count:
            mismatches[table_name] = (sqlite_count, mysql_count)
    return mismatches


def print_count_summary(prefix: str, counts: dict[str, int]) -> None:
    print(prefix)
    for table_name in TABLE_ORDER:
        if table_name in counts:
            print(f'  - {table_name}: {counts[table_name]}')


def print_header() -> None:
    print('=' * 56)
    print('书签管理系统 MySQL 设置')
    print('=' * 56)
    print('1. 迁移当前 SQLite 数据到 MySQL，并启用 MySQL')
    print('2. 重置 MySQL 表结构，并启用一个空的 MySQL 数据库')
    print()


def choose_mode() -> str:
    while True:
        choice = input('请选择模式 [1/2]: ').strip()
        if choice == '1':
            return MIGRATE_MODE
        if choice == '2':
            return RESET_MODE
        print('请输入 1 或 2。')


def collect_mysql_config() -> tuple[str, str, str, str, str]:
    print('\n请输入 MySQL 连接信息：')
    host = prompt('主机', '127.0.0.1')
    port = prompt('端口', '3306')
    user = prompt('用户名', 'root')
    password = prompt('密码', secret=True)
    database = prompt('数据库名', 'bookmark_system')
    return host, port, user, password, database


def show_summary(mode: str, sqlite_path: Path, database_url: str, write_env: bool) -> None:
    action = (
        '迁移当前 SQLite 数据到 MySQL'
        if mode == MIGRATE_MODE
        else '重置 MySQL 表结构并保持空库'
    )
    print('\n摘要：')
    print(f'- 模式: {action}')
    print(f'- SQLite 来源: {sqlite_path}')
    print(f'- MySQL URL: {database_url}')
    print(f'- 写入 .env.local: {"是" if write_env else "否"}')
    if write_env:
        print(f'- 配置文件: {ENV_LOCAL_PATH}')


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='将书签管理系统数据迁移到 MySQL')
    parser.add_argument('--mode', choices=[MIGRATE_MODE, RESET_MODE])
    parser.add_argument('--sqlite-path', default=str(SQLITE_DB_PATH))
    parser.add_argument('--host')
    parser.add_argument('--port')
    parser.add_argument('--user')
    parser.add_argument('--password')
    parser.add_argument('--database')
    parser.add_argument('--no-write-env', action='store_true')
    parser.add_argument('--yes', action='store_true')
    return parser.parse_args()


def resolve_config(args: argparse.Namespace) -> tuple[str, Path, str, str, str, str, str, bool, bool]:
    interactive = not all([args.mode, args.host, args.port, args.user, args.password, args.database])
    mode = args.mode
    sqlite_path = Path(args.sqlite_path).expanduser().resolve()
    host = args.host
    port = args.port
    user = args.user
    password = args.password
    database = args.database
    write_env = not args.no_write_env

    if interactive:
        print_header()
        mode = mode or choose_mode()
        sqlite_path = Path(prompt('SQLite 数据库路径', str(sqlite_path))).expanduser().resolve()
        host = host or '127.0.0.1'
        port = port or '3306'
        user = user or 'root'
        print('\n请输入 MySQL 连接信息：')
        host = prompt('主机', host)
        port = prompt('端口', port)
        user = prompt('用户名', user)
        password = password or prompt('密码', secret=True)
        database = database or prompt('数据库名', 'bookmark_system')

    if not all([mode, host, port, user, password, database]):
        raise ValueError('缺少必要的 MySQL 配置。请补充参数，或直接以交互模式运行。')

    return mode, sqlite_path, host, port, user, password, database, write_env, args.yes


def main() -> int:
    args = parse_args()
    mode, sqlite_path, host, port, user, password, database, write_env, auto_yes = resolve_config(args)
    database_url = build_mysql_url(user, password, host, port, database)

    show_summary(mode, sqlite_path, database_url, write_env)
    if not auto_yes and not confirm('确认继续吗？', default=False):
        print('已取消。')
        return 0

    print('\n[1/5] 创建或检查 MySQL 数据库...')
    ensure_mysql_database(user, password, host, port, database)
    print('      完成')

    print('[2/5] 通过版本化迁移初始化 MySQL 表结构...')
    prepare_mysql_schema(database_url, reset=(mode == RESET_MODE))
    print('      完成')

    if mode == MIGRATE_MODE:
        print('[3/5] 从 SQLite 复制数据到 MySQL...')
        copied_counts = copy_sqlite_to_mysql(sqlite_path, database_url)
        print('      完成')
        print_count_summary('      已复制的数据行数：', copied_counts)

        print('[4/5] 校验迁移后的数据行数...')
        mismatches = verify_mysql_migration(sqlite_path, database_url)
        if mismatches:
            for table_name, (sqlite_count, mysql_count) in mismatches.items():
                print(f'      不一致 {table_name}: sqlite={sqlite_count}, mysql={mysql_count}')
            raise RuntimeError('迁移校验失败。')
        print('      校验通过')
    else:
        print('[3/5] 按要求保留 MySQL 为空库...')
        print('[4/5] 空库重置模式，跳过数据行数校验...')

    if write_env:
        print('[5/5] 写入 .env.local 以启用 MySQL...')
        write_env_local(database_url)
        print('      完成')
    else:
        print('[5/5] 按要求跳过 .env.local 更新...')

    print('\nMySQL 设置完成。')
    print('写入 .env.local 后，后续启动后端时会优先使用其中的 DATABASE_URL。')
    print('如果后端已经在运行，请重启后端以切换数据库。')
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print('\n已取消。')
        raise SystemExit(1)
