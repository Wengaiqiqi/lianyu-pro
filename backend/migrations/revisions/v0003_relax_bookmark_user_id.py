from __future__ import annotations

from sqlalchemy import inspect, text

from models.bookmark import Bookmark


version = '0003'
name = 'relax_bookmark_user_id'


BOOKMARK_COPY_COLUMNS = [
    'id',
    'title',
    'url',
    'description',
    'favicon',
    'user_id',
    'category_id',
    'is_public',
    'is_blocked',
    'visits',
    'is_pending_review',
    'pending_category',
    'pending_type',
    'created_at',
    'updated_at',
]


def _quoted_identifier(dialect: str, name: str) -> str:
    if dialect == 'mysql':
        return f'`{name}`'
    return f'"{name}"'


def upgrade(connection) -> None:
    inspector = inspect(connection)
    if 'bookmarks' not in inspector.get_table_names():
        return

    bookmark_columns = inspector.get_columns('bookmarks')
    user_column = next((column for column in bookmark_columns if column['name'] == 'user_id'), None)
    if not user_column or user_column.get('nullable', True):
        return

    old_table_name = 'bookmarks_old'
    if old_table_name in inspector.get_table_names():
        connection.execute(text(f'DROP TABLE {old_table_name}'))

    if connection.engine.dialect.name == 'mysql':
        connection.execute(text(f'RENAME TABLE bookmarks TO {old_table_name}'))
    else:
        connection.execute(text(f'ALTER TABLE bookmarks RENAME TO {old_table_name}'))
    Bookmark.__table__.create(bind=connection)

    old_column_names = {column['name'] for column in bookmark_columns}
    copy_columns = [column for column in BOOKMARK_COPY_COLUMNS if column in old_column_names]
    if copy_columns:
        dialect = connection.engine.dialect.name
        quoted_columns = ', '.join(_quoted_identifier(dialect, column) for column in copy_columns)
        connection.execute(
            text(
                f'''
                INSERT INTO bookmarks ({quoted_columns})
                SELECT {quoted_columns} FROM {old_table_name}
                '''
            )
        )

    connection.execute(text(f'DROP TABLE {old_table_name}'))
