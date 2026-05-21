from datetime import datetime
import json
from . import db


class UserInterest(db.Model):
    __tablename__ = 'user_interests'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    interests = db.Column(db.Text, default='[]')
    recommendations = db.Column(db.Text, default='[]')
    analyzed_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_interests(self):
        try:
            return json.loads(self.interests or '[]')
        except (json.JSONDecodeError, TypeError):
            return []

    def set_interests(self, data):
        self.interests = json.dumps(data or [], ensure_ascii=False)

    def get_recommendations(self):
        try:
            return json.loads(self.recommendations or '[]')
        except (json.JSONDecodeError, TypeError):
            return []

    def set_recommendations(self, data):
        self.recommendations = json.dumps(data or [], ensure_ascii=False)

    def to_dict(self):
        return {
            'interests': self.get_interests(),
            'recommendations': self.get_recommendations(),
            'analyzed_at': self.analyzed_at.isoformat() if self.analyzed_at else None,
        }

    @staticmethod
    def get_or_create(user_id):
        record = UserInterest.query.filter_by(user_id=user_id).first()
        if not record:
            record = UserInterest(user_id=user_id)
            db.session.add(record)
            db.session.commit()
        return record
