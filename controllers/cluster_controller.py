from flask import jsonify, send_file
from PIL import Image
import uuid
import os
import io
from models import cluster, data
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

        # emit the changes to all current user socket connections as well
        socket_manager.emit_cluster_refreshed_event(user_id=user_id)

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

        # emit the changes to all current user socket connections as well
        socket_manager.emit_cluster_id_refreshed_event(user_id=user_id)

        return {
            "message": "Success: file moved to suggested cluster successfully!"
        }

    # abort the request
    return jsonify({
        "message": "Error: either cluster Id or file Id not provided!"
    }), 400


# return the requested file to the user
def handle_get_file(request, user_id):
    # Get file_id from the request
    request_data = request.get_json()
    file_id = request_data.get("fileId")
    cluster_id = request_data.get("clusterId")

    if file_id and cluster_id:
        # get the file_id information from MySQL database
        db_response = data.get_file_record(user_id, file_id)

        if db_response["success"]:
            if not db_response["data"]:
                # abort the request
                return jsonify({
                    "message": "Error: File not found!"
                }), 404
        else:
            # abort the request
            return jsonify({
                "message": "Error: Database operation failed!"
            }), 500

        # get the file type from the db response
        file_type = db_response["data"][0][0]

        if file_type == 'image':
            # Construct the file path
            image_file_path = f"data/{user_id}/{file_id}.png"

            if not os.path.exists(image_file_path):
                # abort the request
                return jsonify({
                    "message": "Error: File not found!"
                }), 404

            # get the file_id face coords information from MySQL database
            db_response = cluster.get_cluster_file_info(
                user_id=user_id,
                file_id=file_id,
                cluster_id=cluster_id
            )

            if not db_response["success"]:
                # abort the request
                return jsonify({
                    "message": "Error: Database operation failed!"
                }), 500

            x1 = db_response["data"][3]
            y1 = db_response["data"][4]
            x2 = db_response["data"][5]
            y2 = db_response["data"][6]

            # Open the image file using Pillow
            image = Image.open(image_file_path)

            # Perform the crop operation
            cropped_image = image.crop((x1, y1, x2, y2))

            # Save the cropped image to a BytesIO object
            img_io = io.BytesIO()
            cropped_image.save(img_io, 'PNG')
            img_io.seek(0)

            # Return the image
            return send_file(img_io, mimetype='image/png')

        if file_type == 'video':
            # abort the request
            return jsonify({
                "message": "This functionality is not available yet!"
            }), 501

    # abort the request
    return jsonify({
        "message": "Error: Either file Id or Cluster Id not provided!"
    }), 400
