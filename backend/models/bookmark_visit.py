from datetime import datetime
from . import db


class BookmarkVisit(db.Model):
    __tablename__ = 'bookmark_visits'

    id = db.Column(db.Integer, primary_key=True)
    bookmark_id = db.Column(db.Integer, db.ForeignKey('bookmarks.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    bookmark = db.relationship('Bookmark', backref=db.backref('visit_records', lazy='dynamic'))
