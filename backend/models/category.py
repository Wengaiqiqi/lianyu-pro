from datetime import datetime
from . import db


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(256), default='')
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    children = db.relationship('Category', backref=db.backref('parent', remote_side='Category.id'), lazy='select')
    bookmarks = db.relationship('Bookmark', backref='category', lazy='dynamic')

    def get_descendant_ids(self):
        descendant_ids = [self.id]
        for child in self.children:
            descendant_ids.extend(child.get_descendant_ids())
        return descendant_ids

    def get_root_category(self):
        category = self
        while category.parent is not None:
            category = category.parent
        return category

    def _bookmark_count(self):
        if self.user_id is None:
            from .bookmark import Bookmark

            category_ids = self.get_descendant_ids()
            return Bookmark.query.filter(Bookmark.category_id.in_(category_ids)).count()
        return self.bookmarks.filter_by(user_id=self.user_id).count()

    def to_dict(self, include_children=False):
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'parent_id': self.parent_id,
            'user_id': self.user_id,
            'sort_order': self.sort_order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'bookmark_count': self._bookmark_count(),
        }
        if include_children:
            data['children'] = [child.to_dict(include_children=True) for child in self.children]
        return data
