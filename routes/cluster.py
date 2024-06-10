from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from controllers import cluster_controller


# Create a blueprint for /cluster/ route
cluster_routes = Blueprint('cluster', __name__)


@cluster_routes.route('/change-name', methods=['POST'])
@jwt_required()
def changeName():
    return cluster_controller.handle_cluster_name_change(
        request,
        user_id=get_jwt_identity()
    )


@cluster_routes.route('/user-feedback', methods=['POST'])
@jwt_required()
def userFeedBack():
    return cluster_controller.handle_user_feedback(
        request,
        user_id=get_jwt_identity()
    )


@cluster_routes.route('/get', methods=['POST'])
@jwt_required()
def getCroppedImage():
    return cluster_controller.handle_get_file(
        request,
        user_id=get_jwt_identity()
    )
