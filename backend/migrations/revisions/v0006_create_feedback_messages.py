from __future__ import annotations

from sqlalchemy import inspect, text

from models.feedback_message import FeedbackMessage


version = '0006'
name = 'create_feedback_messages'


def upgrade(connection) -> None:
    inspector = inspect(connection)
    table_names = inspector.get_table_names()
    if 'feedbacks' not in table_names:
        return

    if 'feedback_messages' not in table_names:
        FeedbackMessage.__table__.create(bind=connection)

    existing_rows = connection.execute(
        text(
            '''
            SELECT id, user_id, content, created_at, admin_reply, replied_by, replied_at, user_reply, user_replied_at
            FROM feedbacks
            '''
        )
    ).mappings().all()

    existing_message_feedback_ids = {
        row[0]
        for row in connection.execute(text('SELECT DISTINCT feedback_id FROM feedback_messages')).fetchall()
    }

    for row in existing_rows:
        feedback_id = row['id']
        if feedback_id in existing_message_feedback_ids:
            continue

        messages = []
        if row['content']:
            messages.append({
                'feedback_id': feedback_id,
                'sender_id': row['user_id'],
                'sender_type': 'user',
                'content': row['content'],
                'created_at': row['created_at'],
            })
        if row['admin_reply'] and row['replied_by']:
            messages.append({
                'feedback_id': feedback_id,
                'sender_id': row['replied_by'],
                'sender_type': 'admin',
                'content': row['admin_reply'],
                'created_at': row['replied_at'] or row['created_at'],
            })
        if row['user_reply']:
            messages.append({
                'feedback_id': feedback_id,
                'sender_id': row['user_id'],
                'sender_type': 'user',
                'content': row['user_reply'],
                'created_at': row['user_replied_at'] or row['created_at'],
            })

        for message in messages:
            connection.execute(
                text(
                    '''
                    INSERT INTO feedback_messages (feedback_id, sender_id, sender_type, content, created_at)
                    VALUES (:feedback_id, :sender_id, :sender_type, :content, :created_at)
                    '''
                ),
                message,
            )
