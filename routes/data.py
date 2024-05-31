from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from controllers import data_controller


# Create a blueprint for /data/ route
data_routes = Blueprint('data', __name__)


@data_routes.route('/upload', methods=['POST'])
@jwt_required()
def uploadFile():
    return data_controller.handle_upload_file(
        request,
        user_id=get_jwt_identity()
    )


@data_routes.route('/delete', methods=['POST'])
@jwt_required()
def deleteFile():
    return data_controller.handle_delete_file(
        request,
        user_id=get_jwt_identity()
    )


@data_routes.route('/get', methods=['POST'])
@jwt_required()
def getFile():
    return data_controller.handle_get_file(
        request,
        user_id=get_jwt_identity()
    )
