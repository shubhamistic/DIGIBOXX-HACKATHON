from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from controllers import auth_controller


# Create a blueprint for /auth/ route
auth_routes = Blueprint('auth', __name__)


# route to get access_token in exchange for refresh_token
@auth_routes.route('/authenticate', methods=['GET'])
@jwt_required(refresh=True)
def authenticate():
    return auth_controller.handle_authentication(get_jwt_identity())


@auth_routes.route('/sign-in', methods=['GET'])
def signIn():
    return auth_controller.handle_sign_in(request)


@auth_routes.route('/sign-up', methods=['POST'])
def signUp():
    return auth_controller.handle_sign_up(request)
