from __future__ import annotations

from sqlalchemy import inspect

from models.feedback import Feedback


version = '0004'
name = 'create_feedbacks'


def upgrade(connection) -> None:
    inspector = inspect(connection)
    if 'feedbacks' in inspector.get_table_names():
        return

    Feedback.__table__.create(bind=connection)
