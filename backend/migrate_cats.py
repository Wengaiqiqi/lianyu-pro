from app import app
from models import db
from models.bookmark import Bookmark
from models.category import Category
from models.user import User


def run_migration():
    with app.app_context():
        # 1. Give default categories to any user who has no categories yet.
        default_categories = [
            'ææ¯', 'å·¥å·', 'å­¦ä¹ ', 'å¨±ä¹',
            'æ°é»', 'ç¤¾äº¤', 'è´­ç©', 'å¶ä»'
        ]
        users = User.query.all()
        for user in users:
            user_cats = Category.query.filter_by(user_id=user.id).all()
            if not user_cats:
                for i, name in enumerate(default_categories):
                    db.session.add(Category(name=name, user_id=user.id, sort_order=i))
        db.session.commit()

        # 2. Re-fetch user categories and global categories.
        global_cats = {c.id: c.name for c in Category.query.filter_by(user_id=None).all()}

        # 3. If a bookmark points to a global category, ensure the user has the same named category locally.
        for user in users:
            user_cats = {c.name: c for c in Category.query.filter_by(user_id=user.id).all()}
            bookmarks = Bookmark.query.filter_by(user_id=user.id).all()
            for bookmark in bookmarks:
                if bookmark.category_id and bookmark.category_id in global_cats:
                    global_name = global_cats[bookmark.category_id]
                    if global_name not in user_cats:
                        new_cat = Category(name=global_name, user_id=user.id)
                        db.session.add(new_cat)
                        db.session.flush()
                        user_cats[global_name] = new_cat
                    bookmark.category_id = user_cats[global_name].id

        db.session.commit()
        print('Migration finished.')


if __name__ == "__main__":
    run_migration()
