from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from werkzeug.middleware.proxy_fix import ProxyFix

from config import Config
from migrations import run_migrations
from models import db
from routes import register_routes


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.wsgi_app = ProxyFix(
        app.wsgi_app,
        x_for=app.config.get('PROXY_FIX_X_FOR', 0),
        x_proto=app.config.get('PROXY_FIX_X_PROTO', 0),
        x_host=app.config.get('PROXY_FIX_X_HOST', 0),
        x_port=app.config.get('PROXY_FIX_X_PORT', 0),
        x_prefix=app.config.get('PROXY_FIX_X_PREFIX', 0),
    )

    CORS(app, supports_credentials=True)
    JWTManager(app)
    db.init_app(app)

    register_routes(app)

    with app.app_context():
        run_migrations()
        init_admin()

    return app


def init_admin():
    from models.category import Category
    from models.user import User

    admin = User.query.filter_by(role='admin').first()
    if admin:
        return

    admin = User(
        username='admin',
        email='admin@example.com',
        role='admin',
        nickname='admin',
    )
    admin.set_password('admin123')
    db.session.add(admin)
    db.session.flush()

    default_categories = ['技术', '工具', '学习', '娱乐', '新闻', '社交', '购物', '其他']
    for index, name in enumerate(default_categories):
        db.session.add(Category(name=name, user_id=admin.id, sort_order=index))
        db.session.add(Category(name=name, user_id=None, sort_order=index))

    db.session.commit()


app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
