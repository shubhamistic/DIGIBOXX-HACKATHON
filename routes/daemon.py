from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from controllers import daemon_controller


# Create a blueprint for /daemon/ route
daemon_routes = Blueprint('daemon', __name__)


@daemon_routes.route('/get', methods=['POST'])
@jwt_required()
def getFile():
    return daemon_controller.handle_get_file(
        request,
        daemon_client_id=get_jwt_identity()
    )
