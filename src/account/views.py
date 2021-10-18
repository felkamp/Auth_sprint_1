from flask import Blueprint, abort

from flask_restx import Api, Resource, reqparse
from flask_jwt_extended import decode_token

from src.services import AuthService


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
        args = parser.parse_args()
        error_message = 'Email or password is incorrect'

        email = args.get('email')
        authenticated_user = auth_service.authenticate_user(
            email=email,
            password=args.get('password')
        )
        if not authenticated_user:
            return abort(400, error_message)
        jwt_tokens = auth_service.get_jwt_tokens(authenticated_user.id)
        auth_service.save_refresh_token_in_redis(
            jwt_tokens.get('refresh')
        )

        return jwt_tokens


@api.route('/logout')
class Logout(Resource):
    """Endpoint to user logout."""
    def post(self):
        """Logout user with deleting all refresh tokens."""
        parser = reqparse.RequestParser()
        parser.add_argument('Authorization', location='headers')
        args = parser.parse_args()
        jwt_token = args.get('Authorization').split(' ')[-1]

        token_payload = decode_token(jwt_token)
        if token_payload.get('type') == 'refresh':
            return abort(401, 'Incorrect JWT token type')

        user_id = token_payload.get('sub')
        auth_service.delete_all_refresh_tokens(user_id)

        return {
            'msg': 'Successful logout',
        }
