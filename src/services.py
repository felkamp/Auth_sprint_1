import time
from typing import Optional


from flask_security import SQLAlchemyUserDatastore
from flask_security.utils import verify_password
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    decode_token,
)

from src.db.postgres import db
from src.db.redis import redis_db
from src.models import User, Role


USER_DATASTORE = SQLAlchemyUserDatastore(db, User, Role)


class AuthService:
    """Auth service for users."""
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Check user credentials - login and password.

        If credentials is correct return user object.
        """
        user = USER_DATASTORE.get_user(identifier=email)
        if not user:
            return None
        password_is_correct = verify_password(password, user.password)
        if not password_is_correct:
            return None
        return user

    def save_refresh_token_in_redis(
            self, token: str,
    ):
        """Save refresh token in Redis db."""
        token_payload = decode_token(token)
        user_id = token_payload.get('sub')
        expired = token_payload.get('exp')
        expired_seconds_time = int(expired - time.time())

        redis_db.setex(
            name=f'{user_id}:{expired}',
            time=expired_seconds_time,
            value=token
        )

    def delete_all_refresh_tokens(self, user_id: str):
        """Delete all refresh user tokens from redis db."""
        keys = redis_db.keys(f'*{user_id}*')
        if keys:
            redis_db.delete(*keys)

    def get_jwt_tokens(self, user_id: str) -> dict:
        """Get access and refresh tokens for authenticate user."""
        access_token = create_access_token(identity=user_id)
        refresh_token = create_refresh_token(identity=user_id)
        return {
            'access': access_token,
            'refresh': refresh_token,
        }
