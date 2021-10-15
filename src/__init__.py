import redis

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from .config import settings

login_manager = LoginManager()
db = SQLAlchemy()
redis_db = redis.Redis(host=settings.REDIS_HOST,
                       port=settings.REDIS_PORT,
                       db=settings.REDIS_DB)


def create_app(config=None):
    app = Flask(__name__)

    login_manager.login_view = 'account.login'
    login_manager.init_app(app)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = settings.SQLALCHEMY_DATABASE_URI
    db.init_app(app)

    from src.account.views import account

    app.register_blueprint(account)

    # flask login
    # from src.models import User

    return app


app = create_app()
