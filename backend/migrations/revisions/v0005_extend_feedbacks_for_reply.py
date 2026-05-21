from __future__ import annotations

from sqlalchemy import inspect, text


version = '0005'
name = 'extend_feedbacks_for_reply'


def upgrade(connection) -> None:
    inspector = inspect(connection)
    if 'feedbacks' not in inspector.get_table_names():
        return

    columns = {column['name'] for column in inspector.get_columns('feedbacks')}
    statements = []

    if 'user_reply' not in columns:
        statements.append("ALTER TABLE feedbacks ADD COLUMN user_reply TEXT DEFAULT ''")
    if 'user_replied_at' not in columns:
        statements.append('ALTER TABLE feedbacks ADD COLUMN user_replied_at DATETIME')

    for statement in statements:
        connection.execute(text(statement))
