from datetime import datetime

from . import db


class FeedbackMessage(db.Model):
    __tablename__ = 'feedback_messages'

    id = db.Column(db.Integer, primary_key=True)
    feedback_id = db.Column(db.Integer, db.ForeignKey('feedbacks.id'), nullable=False, index=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    sender_type = db.Column(db.String(20), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    sender = db.relationship('User')

    def to_dict(self):
        return {
            'id': self.id,
            'feedback_id': self.feedback_id,
            'sender_id': self.sender_id,
            'sender_type': self.sender_type,
            'sender_name': (
                (self.sender.nickname or self.sender.username)
                if self.sender else None
            ),
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
