from datetime import timedelta

from flask import Flask
from flask_login import LoginManager
from flask_security import Security, SQLAlchemyUserDatastore
from flask_jwt_extended import JWTManager

from .config import settings
from src.account.views import account
from src.account.views import api as auth_api
from src.db.postgres import db, init_db
from src.db.redis import init_redis_db
from src.models.user import User, Role


login_manager = LoginManager()


def create_app(config=None):
    app = Flask(__name__)

    login_manager.login_view = 'account.login'
    login_manager.init_app(app)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = settings.SECRET_KEY
    app.config['SECURITY_PASSWORD_SALT'] = settings.SECURITY_PASSWORD_SALT
    app.config["SECURITY_SEND_REGISTER_EMAIL"] = False
    app.config["JWT_SECRET_KEY"] = settings.JWT_SECRET_KEY
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=1)

    init_db(app)
    init_redis_db(app)
    Security(app, SQLAlchemyUserDatastore(db, User, Role))

    # Setup the Flask-JWT-Extended extension
    JWTManager(app)

    app.register_blueprint(account, url_prefix='/api/v1')

    return app


app = create_app()
