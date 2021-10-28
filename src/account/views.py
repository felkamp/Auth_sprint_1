from http import HTTPStatus
from typing import Optional

from flask import Blueprint, abort
from flask_jwt_extended import get_jwt, jwt_required
from flask_restx import Api, Resource, reqparse
from flask_security.registerable import register_user

from src.models.user import USER_DATASTORE
from src.services.auth import auth_service

account = Blueprint("account", __name__)
api = Api(account)


@api.route("/login")
class Login(Resource):
    """Endpoint to user login."""

    def post(self):
        """Check user credentials and get JWT token for user."""
        parser = reqparse.RequestParser()
        parser.add_argument(
            "email",
            required=True,
            type=str,
            help="Email cannot be blank!",
        )
        parser.add_argument(
            "password",
            required=True,
            type=str,
            help="Password cannot be blank!",
        )
        parser.add_argument("User-Agent", location="headers")
        args = parser.parse_args()

        error_message = "Email or password is incorrect"

        email = args.get("email")
        authenticated_user = auth_service.authenticate_user(
            email=email, password=args.get("password")
        )
        if not authenticated_user:
            return abort(HTTPStatus.FORBIDDEN, error_message)
        jwt_tokens = auth_service.get_jwt_tokens(authenticated_user)

        user_agent = args.get("User-Agent")
        auth_service.save_refresh_token_in_redis(jwt_tokens.get("refresh"), user_agent)
        auth_service.create_user_auth_log(
            user_id=authenticated_user.id, device=user_agent
        )

        return jwt_tokens


@api.route("/login_history")
class LoginHistory(Resource):
    """Endpoint to represent user login history."""

    @jwt_required()
    def get(self):
        """Get user login history info."""
        token_payload = get_jwt()
        user_id = token_payload.get("sub")
        user_logs = auth_service.get_auth_user_logs(user_id)
        return user_logs


@api.route("/account_credentials")
class CredentialsChange(Resource):
    @jwt_required()
    def put(self):
        """Endpoint to change user credentials email or password."""
        parser = reqparse.RequestParser()
        parser.add_argument(
            "credential_type",
            required=True,
            type=str,
            help="Credential type to change!",
        )
        parser.add_argument(
            "old",
            required=True,
            type=str,
            help="Current credential cannot be blank!",
        )
        parser.add_argument(
            "new",
            required=True,
            type=str,
            help="New credential cannot be blank!",
        )
        args = parser.parse_args()
        credential_type = args.get("credential_type")
        old_credential = args.get("old")
        new_credential = args.get("new")

        token_payload = get_jwt()
        user_id = token_payload.get("sub")

        is_credential_chaged = auth_service.change_user_credentials(
            user_id,
            credential_type,
            old_credential,
            new_credential,
        )
        if not is_credential_chaged:
            return abort(HTTPStatus.BAD_REQUEST, "Credentials are incorrect.")
        return {"msg": "Credentials changed successfully."}


@api.route("/logout")
class Logout(Resource):
    """Endpoint to user logout."""

    @jwt_required()
    def post(self):
        """Logout user with deleting refresh tokens.

        If 'is_full' request param exists, then delete all refresh tokens.
        """
        parser = reqparse.RequestParser()
        parser.add_argument("User-Agent", location="headers")
        parser.add_argument(
            "is_full",
            required=False,
            type=bool,
            help="Logout from all accounts!",
        )
        args = parser.parse_args()

        token_payload = get_jwt()

        user_id = token_payload.get("sub")
        user_agent = args.get("User-Agent")
        if args.get("is_full"):
            auth_service.delete_all_refresh_tokens(user_id)
        else:
            auth_service.delete_user_refresh_token(user_id, user_agent)
        return {
            "msg": "Successful logout",
        }


@api.route("/register")
class Register(Resource):
    """Endpoint to sign up."""

    def post(self):
        """Register a new user."""
        parser = reqparse.RequestParser()
        parser.add_argument(
            "email",
            required=True,
            type=str,
            help="Email cannot be blank!",
        )
        parser.add_argument(
            "password",
            required=True,
            type=str,
            help="Password cannot be blank!",
        )
        args = parser.parse_args()
        email = args.get("email")
        password = args.get("password")

        if USER_DATASTORE.get_user(identifier=email):
            return abort(HTTPStatus.BAD_REQUEST, "This email address already exists!")
        register_user(email=email, password=password)
        return {
            "msg": "Thank you for registering. Now you can log in to your account.",
        }


@api.route("/refresh")
class Refresh(Resource):
    """Endpoint to refresh JWT tokens."""

    @jwt_required(refresh=True)
    def post(self):
        """Create new pair of access and refresh JWT tokens for user."""
        parser = reqparse.RequestParser()
        parser.add_argument("User-Agent", location="headers")
        parser.add_argument("Authorization", location="headers")
        args = parser.parse_args()

        user_agent: str = args.get("User-Agent")

        token_payload = get_jwt()
        user_id: str = token_payload.get("sub")

        jwt_tokens: Optional[dict] = auth_service.refresh_jwt_tokens(
            user_id=user_id, user_agent=user_agent
        )

        if not jwt_tokens:
            return abort(HTTPStatus.UNAUTHORIZED, "Authentication Timeout!")
        return jwt_tokens
