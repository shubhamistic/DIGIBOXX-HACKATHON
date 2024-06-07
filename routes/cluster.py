from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from controllers import cluster_controller


# Create a blueprint for /cluster/ route
cluster_routes = Blueprint('cluster', __name__)


@cluster_routes.route('/change-name', methods=['POST'])
@jwt_required()
def getDistinctCluster():
    return cluster_controller.handle_cluster_name_change(
        request,
        user_id=get_jwt_identity()
    )
