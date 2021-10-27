from http import HTTPStatus

from flask import Blueprint, abort
from flask_restx import Api, Resource, reqparse, fields
from flask_jwt_extended import jwt_required
from src.services.role import role_service
from src.services.user import user_service
from src.models.user import User, Role, Permission
from src.utils.utils import is_valid_uuid
from src.utils.utils import check_permission


admin = Blueprint('admin', __name__)
api = Api(admin)

role_response_model = api.model(
    'Role data response',
    {
        'id': fields.String(),
        'name': fields.String(),
        'permissions': fields.Integer(),
        'description': fields.String()
    }
)


@api.route('/roles')
class RolesList(Resource):
    """Shows a list of all roles, and lets you POST to add new role"""

    @api.marshal_with(role_response_model, code=HTTPStatus.OK, as_list=True)
    @jwt_required()
    @check_permission(Permission.VIEW)
    def get(self):
        """List all roles."""
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('page', required=True, type=int, location='args')
        parser.add_argument('size', required=True, type=int, location='args')
        args = parser.parse_args()

        return role_service.get_roles(page=args.get('page'), size=args.get('size'))

    @jwt_required()
    @check_permission(Permission.CREATE)
    def post(self):
        """Create a new role."""
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('name', required=True, location='form')
        parser.add_argument('permissions', required=True, type=int, location='form')
        parser.add_argument('description', required=False)
        args = parser.parse_args()
        name = args.get('name')
        permissions = args.get('permissions')
        description = args.get('description')

        if role_service.get_role_by_name(name=name):
            return abort(HTTPStatus.BAD_REQUEST, 'This role already exists!')

        role_service.add_role(role_name=name, permissions=permissions, description=description)
        return {'msg': 'Role created!'}


@api.route('/role/<string:id>')
class RoleDetail(Resource):
    """
    Shows a role, and lets you PUT
    to update role or DELETE to remove it
    """

    @api.marshal_with(role_response_model, code=HTTPStatus.OK)
    @jwt_required()
    @check_permission(Permission.VIEW)
    def get(self, id):
        """Get role by id."""
        return Role.query.filter_by(id=id).first_or_404()

    @jwt_required()
    @check_permission(Permission.UPDATE)
    def put(self, id):
        """Update role by id."""
        parser = reqparse.RequestParser()
        parser.add_argument('name', required=False)
        parser.add_argument('permissions', type=int, required=False)
        parser.add_argument('description', required=False)
        args = parser.parse_args()

        if not (role := role_service.get_role_by_id(id=id)):
            return abort(HTTPStatus.NOT_FOUND, 'Not Found!')

        updated_fields = {
            field: args[field] for field in ['name', 'permissions', 'description'] if args.get(field)
        }

        if not updated_fields:
            return abort(HTTPStatus.BAD_REQUEST)
        if updated_fields.get('name') and role_service.get_role_by_name(name=updated_fields['name']):
            return abort(HTTPStatus.BAD_REQUEST, 'This role already exists!')

        role_service.update_role(role=role, updated_fields=updated_fields)
        return {'msg': 'Role updated!'}

    @jwt_required()
    @check_permission(Permission.DELETE)
    def delete(self, id):
        """Delete role by id."""
        role_service.delete_role(id=id)
        return {'msg': 'Role deleted!'}


@api.route('/user/<string:user_id>/roles')
class UserRole(Resource):
    """
    Lets you PUT to add a new role for user
    """

    @jwt_required()
    @check_permission(Permission.CREATE)
    def post(self, user_id):
        """Add a new user role."""
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('role_id', required=True, location='form')
        args = parser.parse_args()
        role_id = args.get('role_id')
        user = User.query.filter_by(id=user_id).first_or_404()
        role = Role.query.filter_by(id=role_id).first_or_404()

        if not all([is_valid_uuid(user_id), is_valid_uuid(role_id)]):
            return abort(HTTPStatus.BAD_REQUEST)
        if user_service.has_role(user_id=user_id, role_id=role_id):
            return abort(HTTPStatus.BAD_REQUEST, 'User already has this role!')

        user_service.add_role(user=user, role=role)
        return {'msg': 'Role added!'}


@api.route('/user/<string:user_id>/roles/<string:role_id>')
class UserRole(Resource):
    """
    Lets you DELETE to remove user role
    """

    @jwt_required()
    @check_permission(Permission.DELETE)
    def delete(self, user_id, role_id):
        """Delete user role."""
        if not all([is_valid_uuid(user_id), is_valid_uuid(role_id)]):
            return abort(HTTPStatus.BAD_REQUEST)
        if not user_service.has_role(user_id=user_id, role_id=role_id):
            return abort(HTTPStatus.NOT_FOUND, 'User does not have this role!')

        user = User.query.filter_by(id=user_id).first_or_404()
        role = Role.query.filter_by(id=role_id).first_or_404()
        user_service.delete_role(user=user, role=role)
        return {'msg': 'Role deleted!'}
