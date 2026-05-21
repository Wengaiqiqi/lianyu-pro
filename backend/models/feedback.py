from datetime import datetime

from . import db
from .feedback_message import FeedbackMessage


class Feedback(db.Model):
    __tablename__ = 'feedbacks'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    subject = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    contact = db.Column(db.String(120), default='')
    status = db.Column(db.String(20), default='pending')
    admin_reply = db.Column(db.Text, default='')
    replied_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    replied_at = db.Column(db.DateTime, nullable=True)
    user_reply = db.Column(db.Text, default='')
    user_replied_at = db.Column(db.DateTime, nullable=True)
    is_read_by_user = db.Column(db.Boolean, default=False)
    is_deleted_by_admin = db.Column(db.Boolean, default=False)
    is_deleted_by_user = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('feedback_items', lazy='dynamic'))
    reply_admin = db.relationship('User', foreign_keys=[replied_by])
    messages = db.relationship(
        'FeedbackMessage',
        backref='feedback',
        lazy='select',
        cascade='all, delete-orphan',
        order_by='FeedbackMessage.created_at.asc(), FeedbackMessage.id.asc()'
    )

    def to_dict(self):
        messages = [message.to_dict() for message in self.messages if not message.is_deleted]
        admin_messages = [message for message in messages if message['sender_type'] == 'admin']
        user_messages = [message for message in messages if message['sender_type'] == 'user']

        latest_admin = admin_messages[-1] if admin_messages else None
        follow_up_user_messages = user_messages[1:] if len(user_messages) > 1 else []
        latest_user_reply = follow_up_user_messages[-1] if follow_up_user_messages else None

        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else None,
            'nickname': self.user.nickname if self.user else None,
            'avatar': self.user.avatar if self.user else None,
            'subject': self.subject,
            'content': self.content,
            'contact': self.contact,
            'status': self.status,
            'admin_reply': latest_admin['content'] if latest_admin else self.admin_reply,
            'replied_by': self.replied_by,
            'reply_admin_name': (
                (self.reply_admin.nickname or self.reply_admin.username)
                if self.reply_admin else None
            ),
            'replied_at': (
                latest_admin['created_at']
                if latest_admin else
                (self.replied_at.isoformat() if self.replied_at else None)
            ),
            'user_reply': latest_user_reply['content'] if latest_user_reply else self.user_reply,
            'user_replied_at': (
                latest_user_reply['created_at']
                if latest_user_reply else
                (self.user_replied_at.isoformat() if self.user_replied_at else None)
            ),
            'is_read_by_user': self.is_read_by_user,
            'has_reply': bool(latest_admin or self.admin_reply),
            'has_user_reply': bool(latest_user_reply or self.user_reply),
            'messages': messages,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
