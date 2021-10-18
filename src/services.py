import datetime
import time


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
    def is_user_authenticated(self, email: str, password: str) -> bool:
        """Check user credentials - login and password."""
        user = USER_DATASTORE.get_user(identifier=email)

        if not user:
            return False
        password_is_correct = verify_password(password, user.password)
        if not password_is_correct:
            return False
        return True

    def save_refresh_token_in_redis(
            self, token: str,
    ):
        """Save refresh token in Redis db."""
        token_payload = decode_token(token)
        email = token_payload.get('sub')
        expired = token_payload.get('exp')
        expired_seconds_time = int(expired - time.time())

        redis_db.setex(
            name=f'{email}:{expired}',
            time=expired_seconds_time,
            value=token
        )

    def delete_all_refresh_tokens(self, email: str):
        """Delete all refresh user tokens from redis db."""
        keys = redis_db.keys(f'*{email}*')
        if keys:
            redis_db.delete(*keys)

    def get_jwt_tokens(self, email: str) -> dict:
        """Get access and refresh tokens for authenticate user."""
        expires_delta_for_access = datetime.timedelta(hours=1)
        expires_delta_for_refresh = datetime.timedelta(days=1)

        access_token = create_access_token(
            identity=email,
            expires_delta=expires_delta_for_access,
        )
        refresh_token = create_refresh_token(
            identity=email,
            expires_delta=expires_delta_for_refresh,
        )

        return {
            'access': access_token,
            'refresh': refresh_token,
        }
