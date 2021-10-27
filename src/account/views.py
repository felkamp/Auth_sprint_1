from http import HTTPStatus

from flask import Blueprint, abort
from flask_restx import Api, Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt
from flask_security.registerable import register_user

from src.services.auth import AuthService
from src.models.user import USER_DATASTORE

account = Blueprint('account', __name__)
api = Api(account)
auth_service = AuthService()


@api.route('/login')
class Login(Resource):
    """Endpoint to user login."""

    def post(self):
        """Check user credentials and get JWT token for user."""
        parser = reqparse.RequestParser()
        parser.add_argument(
            'email', required=True,
            type=str, help="Email cannot be blank!",
        )
        parser.add_argument(
            'password', required=True,
            type=str, help="Password cannot be blank!",
        )
        parser.add_argument('User-Agent', location='headers')
        args = parser.parse_args()

        error_message = 'Email or password is incorrect'

        email = args.get('email')
        authenticated_user = auth_service.authenticate_user(
            email=email,
            password=args.get('password')
        )
        if not authenticated_user:
            return abort(HTTPStatus.FORBIDDEN, error_message)
        jwt_tokens = auth_service.get_jwt_tokens(authenticated_user)

        user_agent = args.get('User-Agent')
        auth_service.save_refresh_token_in_redis(
            jwt_tokens.get('refresh'),
            user_agent
        )

        return jwt_tokens


@api.route('/logout')
class Logout(Resource):
    """Endpoint to user logout."""

    @jwt_required()
    def post(self):
        """Logout user with deleting all refresh tokens."""
        parser = reqparse.RequestParser()
        parser.add_argument('User-Agent', location='headers')
        args = parser.parse_args()

        token_payload = get_jwt()

        user_id = token_payload.get('sub')
        user_agent = args.get('User-Agent')
        auth_service.delete_user_refresh_token(user_id, user_agent)
        return {
            'msg': 'Successful logout',
        }


@api.route('/register')
class Register(Resource):
    """Endpoint to sign up."""

    def post(self):
        """Register a new user."""
        parser = reqparse.RequestParser()
        parser.add_argument(
            'email', required=True,
            type=str, help="Email cannot be blank!",
        )
        parser.add_argument(
            'password', required=True,
            type=str, help="Password cannot be blank!",
        )
        args = parser.parse_args()
        email = args.get('email')
        password = args.get('password')

        if USER_DATASTORE.get_user(identifier=email):
            return abort(HTTPStatus.BAD_REQUEST, 'This email address already exists!')
        register_user(email=email, password=password)
        return {
            'msg': 'Thank you for registering. Now you can log in to your account.',
        }
