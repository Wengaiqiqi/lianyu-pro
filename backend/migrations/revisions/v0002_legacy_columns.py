from __future__ import annotations

from sqlalchemy import inspect, text


version = '0002'
name = 'legacy_columns'


def _column_names(inspector, table_name: str) -> set[str]:
    return {column['name'] for column in inspector.get_columns(table_name)}


def _add_column(connection, table_name: str, column_sql: str) -> None:
    connection.execute(text(f'ALTER TABLE {table_name} ADD COLUMN {column_sql}'))


def upgrade(connection) -> None:
    inspector = inspect(connection)
    table_names = set(inspector.get_table_names())

    if 'bookmarks' in table_names:
        bookmark_columns = _column_names(inspector, 'bookmarks')
        if 'visits' not in bookmark_columns:
            _add_column(connection, 'bookmarks', 'visits INTEGER DEFAULT 0')
        if 'is_pending_review' not in bookmark_columns:
            _add_column(connection, 'bookmarks', 'is_pending_review BOOLEAN DEFAULT 0')
        if 'pending_category' not in bookmark_columns:
            _add_column(connection, 'bookmarks', "pending_category VARCHAR(256) DEFAULT ''")
        if 'pending_type' not in bookmark_columns:
            _add_column(connection, 'bookmarks', "pending_type VARCHAR(32) DEFAULT ''")

    if 'users' in table_names:
        user_columns = _column_names(inspector, 'users')
        if 'nickname' not in user_columns:
            _add_column(connection, 'users', "nickname VARCHAR(80) DEFAULT ''")
