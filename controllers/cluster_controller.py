from flask import jsonify
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
