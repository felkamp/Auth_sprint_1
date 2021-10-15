import os

from dotenv import load_dotenv


dotenv_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path)


class Settings:
    """Base configuration."""

    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")

    REDIS_HOST = os.getenv("REDIS_HOST")
    REDIS_PORT = os.getenv("REDIS_PORT")
    REDIS_DB = os.getenv("REDIS_DB")


settings = Settings()
