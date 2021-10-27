from http import HTTPStatus

from flask import Blueprint, abort
from flask_restx import Api, Resource, reqparse, fields
from flask_jwt_extended import jwt_required
from src.services.admin import admin_service

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
    def get(self):
        """List all roles."""
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('page', required=True, type=int, location='args')
        parser.add_argument('size', required=True, type=int, location='args')
        args = parser.parse_args()

        return admin_service.get_roles(page=args.get('page'), size=args.get('size'))

    @jwt_required()
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

        if admin_service.get_role_by_name(name=name):
            return abort(HTTPStatus.BAD_REQUEST, 'This role already exists!')

        admin_service.add_role(role_name=name, permissions=permissions, description=description)
        return {'msg': 'Role created!'}


@api.route('/role/<string:id>')
class Role(Resource):
    """
    Shows a role, and lets you PUT
    to update role or DELETE to remove it
    """

    @api.marshal_with(role_response_model, code=HTTPStatus.OK)
    @jwt_required()
    def get(self, id):
        """Get role by id."""
        if not (role := admin_service.get_role_by_id(id=id)):
            return abort(HTTPStatus.NOT_FOUND, 'Not Found!')
        return role

    @jwt_required()
    def put(self, id):
        """Update role by id."""
        parser = reqparse.RequestParser()
        parser.add_argument('name', required=False)
        parser.add_argument('permissions', type=int, required=False)
        parser.add_argument('description', required=False)
        args = parser.parse_args()

        if not (role := admin_service.get_role_by_id(id=id)):
            return abort(HTTPStatus.NOT_FOUND, 'Not Found!')

        updated_fields = {
            field: args[field] for field in ['name', 'permissions', 'description'] if args.get(field)
        }

        if not updated_fields:
            return abort(HTTPStatus.BAD_REQUEST)
        if updated_fields.get('name') and admin_service.get_role_by_name(name=updated_fields['name']):
            return abort(HTTPStatus.BAD_REQUEST, 'This role already exists!')

        admin_service.update_role(role=role, updated_fields=updated_fields)
        return {'msg': 'Role updated!'}

    @jwt_required()
    def delete(self, id):
        """Delete role by id."""
        admin_service.delete_role(id=id)
        return {'msg': 'Role deleted!'}
