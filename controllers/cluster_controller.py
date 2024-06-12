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
    # Get cluster I'd, file I'd and target cluster I'd from the request
    request_data = request.get_json()
    cluster_id = request_data.get("clusterId")
    file_id = request_data.get("fileId")
    target_cluster_id = request_data.get("targetClusterId")

    if cluster_id and file_id:
        # check if the file id is identity image in the cluster or not
        db_response = cluster.get_identity_cluster_file_info(
            user_id=user_id,
            cluster_id=cluster_id,
            file_id=file_id
        )

        if not db_response["success"]:
            # abort the request
            return jsonify({
                "message": "Error: Database operation failed!",
                "error": db_response["error"]
            }), 500

        # check if the image is the identity image of cluster or not
        if db_response["data"]:
            # remove the current image from identity image
            db_response = cluster.update_identity_to_false(
                user_id=user_id,
                cluster_id=cluster_id,
                file_id=file_id
            )

            if not db_response["success"]:
                # abort the request
                return jsonify({
                    "message": "Error: Database operation failed!",
                    "error": db_response["error"]
                }), 500

            # make the second highest matching score image as identity image
            db_response = cluster.update_identity_to_second_highest_match_score(
                user_id=user_id,
                cluster_id=cluster_id,
                file_id=file_id
            )

            if not db_response["success"]:
                # abort the request
                return jsonify({
                    "message": "Error: Database operation failed!",
                    "error": db_response["error"]
                }), 500

        if not target_cluster_id:
            # create a new target cluster id if not provided
            target_cluster_id = str(uuid.uuid4()).replace('-', '_')

        if cluster_id == target_cluster_id:
            # update the matched score of the image with 100
            db_response = cluster.update_matched_score(
                user_id=user_id,
                cluster_id=cluster_id,
                file_id=file_id,
                matched_score=100
            )

            if not db_response["success"]:
                # abort the request
                return jsonify({
                    "message": "Error: Database operation failed!",
                    "error": db_response["error"]
                }), 500
        else:
            # update the matched score with 0
            db_response = cluster.update_matched_score(
                user_id=user_id,
                cluster_id=cluster_id,
                file_id=file_id,
                matched_score=0
            )

            if not db_response["success"]:
                # abort the request
                return jsonify({
                    "message": "Error: Database operation failed!",
                    "error": db_response["error"]
                }), 500

        # move the image to target cluster id
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
        socket_manager.emit_cluster_refreshed_event(user_id=user_id)
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
    coords = request_data.get("coords")

    if file_id and cluster_id and coords:
        # Construct the file path
        image_file_path = f"data/{user_id}/{file_id}.png"

        if not os.path.exists(image_file_path):
            # abort the request
            return jsonify({
                "message": "Error: File not found!"
            }), 404

        x1 = coords[0]
        y1 = coords[1]
        x2 = coords[2]
        y2 = coords[3]

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

    # abort the request
    return jsonify({
        "message": "Error: Either file Id, Cluster Id or coords not provided!"
    }), 400
