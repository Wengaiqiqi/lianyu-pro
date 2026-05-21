from __future__ import annotations

from sqlalchemy import inspect, text

from models import db


version = '0007'
name = 'add_feedback_deleted_by_admin'


def upgrade(connection) -> None:
    inspector = inspect(connection)
    table_names = inspector.get_table_names()
    if 'feedbacks' not in table_names:
        return

    columns = [col['name'] for col in inspector.get_columns('feedbacks')]
    if 'is_deleted_by_admin' not in columns:
        connection.execute(text('ALTER TABLE feedbacks ADD COLUMN is_deleted_by_admin BOOLEAN DEFAULT 0'))

    if 'is_deleted_by_user' not in columns:
        connection.execute(text('ALTER TABLE feedbacks ADD COLUMN is_deleted_by_user BOOLEAN DEFAULT 0'))

    if 'feedback_messages' not in table_names:
        return

    messages_columns = [col['name'] for col in inspector.get_columns('feedback_messages')]
    if 'is_deleted' not in messages_columns:
        connection.execute(text('ALTER TABLE feedback_messages ADD COLUMN is_deleted BOOLEAN DEFAULT 0'))
