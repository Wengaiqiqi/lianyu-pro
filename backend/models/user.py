from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from . import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    nickname = db.Column(db.String(80), default='')
    password_hash = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(120), default='')
    avatar = db.Column(db.String(256), default='')
    role = db.Column(db.String(20), default='user')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    bookmarks = db.relationship('Bookmark', backref='user', lazy='dynamic')
    categories = db.relationship('Category', backref='user', lazy='dynamic')
    following = db.relationship(
        'UserFollow',
        foreign_keys='UserFollow.follower_id',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    followers = db.relationship(
        'UserFollow',
        foreign_keys='UserFollow.followed_id',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    given_public_likes = db.relationship(
        'PublicUserLike',
        foreign_keys='PublicUserLike.user_id',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    received_public_likes = db.relationship(
        'PublicUserLike',
        foreign_keys='PublicUserLike.target_user_id',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'nickname': self.nickname,
            'email': self.email,
            'avatar': self.avatar,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
