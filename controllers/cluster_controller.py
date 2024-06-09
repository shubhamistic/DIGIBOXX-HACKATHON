from flask import jsonify
import uuid
from models import cluster
from managers.socket_managers.socket_manager import SocketManager


socket_manager = SocketManager()


def handle_cluster_name_change(request, user_id):
    # Get cluster_id, cluster name from the request
    request_data = request.get_json()
    cluster_id = request_data.get("clusterId")
    cluster_name = request_data.get("clusterName")

    if cluster_id and cluster_name:
        db_response = cluster.update_user_cluster_name(
            user_id=user_id,
            cluster_id=cluster_id,
            cluster_name=cluster_name
        )

        if not db_response["success"]:
            # abort the request
            return jsonify({
                "message": "Error: Database operation failed!",
                "error": db_response["error"]
            }), 500

        return {
            "message": "Success: cluster name changed successfully!"
        }

    # abort the request
    return jsonify({
        "message": "Error: either cluster Id or cluster name not provided!"
    }), 400


def handle_user_feedback(request, user_id):
    # Get cluster_id, cluster name from the request
    request_data = request.get_json()
    cluster_id = request_data.get("clusterId")
    file_id = request_data.get("fileId")
    target_cluster_id = request_data.get("targetClusterId")

    if cluster_id and file_id:
        if not target_cluster_id:
            # create a new target cluster id if not provided
            target_cluster_id = str(uuid.uuid4()).replace('-', '_')

        db_response = cluster.update_file_cluster(
            user_id=user_id,
            cluster_id=cluster_id,
            file_id=file_id,
            target_cluster_id=target_cluster_id
        )

        if not db_response["success"]:
            # abort the request
            return jsonify({
                "message": "Error: Database operation failed!",
                "error": db_response["error"]
            }), 500

        return {
            "message": "Success: file moved to suggested cluster successfully!"
        }

    # abort the request
    return jsonify({
        "message": "Error: either cluster Id or file Id not provided!"
    }), 400
