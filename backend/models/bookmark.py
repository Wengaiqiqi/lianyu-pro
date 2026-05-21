from datetime import datetime
from . import db


class Bookmark(db.Model):
    __tablename__ = 'bookmarks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    url = db.Column(db.String(1024), nullable=False)
    description = db.Column(db.Text, default='')
    favicon = db.Column(db.String(512), default='')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    is_public = db.Column(db.Boolean, default=False)
    is_blocked = db.Column(db.Boolean, default=False)
    visits = db.Column(db.Integer, default=0)
    is_pending_review = db.Column(db.Boolean, default=False)
    pending_category = db.Column(db.String(256), default='')
    pending_type = db.Column(db.String(32), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'url': self.url,
            'description': self.description,
            'favicon': self.favicon,
            'user_id': self.user_id,
            'username': self.user.username if self.user else None,
            'nickname': self.user.nickname if self.user else None,
            'avatar': self.user.avatar if self.user else None,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'is_public': self.is_public,
            'is_blocked': self.is_blocked,
            'visits': self.visits,
            'is_pending_review': self.is_pending_review,
            'pending_category': self.pending_category,
            'pending_type': self.pending_type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
