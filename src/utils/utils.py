from http import HTTPStatus
from uuid import UUID
from functools import wraps
from src.models.user import Permission
from flask_jwt_extended import get_jwt
from flask import abort


def is_valid_uuid(uuid, version=4):
    try:
        UUID(uuid, version=version)
    except ValueError:
        return False
    return True


def check_permission(permission: Permission):
    """
    Check user permissions using jwt
    """

    def decorator(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            jwt = get_jwt()
            if jwt.get('perms') and (jwt['perms'] & permission):
                return func(*args, **kwargs)
            return abort(HTTPStatus.FORBIDDEN, 'Not enough rights')
        return wrapped
    return decorator
