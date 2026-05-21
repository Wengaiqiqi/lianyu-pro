from datetime import datetime
from . import db


class AIConfig(db.Model):
    __tablename__ = 'ai_config'

    id = db.Column(db.Integer, primary_key=True)
    api_url = db.Column(db.String(512), default='')
    api_key = db.Column(db.String(512), default='')
    model_name = db.Column(db.String(100), default='')
    enabled = db.Column(db.Boolean, default=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self, hide_key=False):
        return {
            'id': self.id,
            'api_url': self.api_url,
            'api_key': ('*' * 8 + self.api_key[-4:]) if hide_key and self.api_key and len(self.api_key) > 4 else ('' if hide_key else self.api_key),
            'model_name': self.model_name,
            'enabled': self.enabled,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    @staticmethod
    def get_config():
        config = AIConfig.query.first()
        if not config:
            config = AIConfig()
            db.session.add(config)
            db.session.commit()
        return config
