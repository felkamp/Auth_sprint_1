from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from src.config import settings


db = SQLAlchemy()


def init_db(app: Flask):
    app.config['SQLALCHEMY_DATABASE_URI'] = settings.SQLALCHEMY_DATABASE_URI
    db.init_app(app)
    with app.app_context():
        db.create_all()
        db.session.commit()
