from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User
from .category import Category
from .bookmark import Bookmark
from .bookmark_visit import BookmarkVisit
from .log import OperationLog
from .ai_config import AIConfig
from .user_interest import UserInterest
from .user_social import UserFollow, PublicUserLike
from .feedback import Feedback
from .feedback_message import FeedbackMessage
