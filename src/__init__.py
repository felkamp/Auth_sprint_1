import redis
from flask import Flask
from flask_login import LoginManager
from flask_security import Security, SQLAlchemyUserDatastore

from .config import settings
from src.account.views import account
from src.db.postgres import db, init_db
from src.models.user import User, Role


login_manager = LoginManager()

redis_db = redis.Redis(host=settings.REDIS_HOST,
                       port=settings.REDIS_PORT,
                       db=settings.REDIS_DB)


def create_app(config=None):
    app = Flask(__name__)

    login_manager.login_view = 'account.login'
    login_manager.init_app(app)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = settings.SECRET_KEY
    app.config['SECURITY_PASSWORD_SALT'] = settings.SECURITY_PASSWORD_SALT

    init_db(app)
    Security(app, SQLAlchemyUserDatastore(db, User, Role))

    app.register_blueprint(account)

    return app


app = create_app()
