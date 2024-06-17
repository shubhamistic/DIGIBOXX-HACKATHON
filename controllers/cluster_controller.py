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
        # case 1: same cluster_id and target_cluster_id
        # (i.e.) image is correctly clustered
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
            # set matched_score of the image to zero
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

            # check if the file id is identity image in the cluster or not
            is_identity_cluster = False
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

            if db_response["data"]:
                is_identity_cluster = True

            # case 2: target_cluster_id not provided
            # (i.e.) image is wrongly clustered (user wants to create a new cluster for that image)
            if not target_cluster_id:
                # create a new target cluster id if not provided
                target_cluster_id = str(uuid.uuid4()).replace('-', '_')

                if not is_identity_cluster:
                    # set the cluster as identity cluster
                    db_response = cluster.update_cluster_identity(
                        user_id=user_id,
                        cluster_id=cluster_id,
                        file_id=file_id,
                        identity=True
                    )

                    if not db_response["success"]:
                        # abort the request
                        return jsonify({
                            "message": "Error: Database operation failed!",
                            "error": db_response["error"]
                        }), 500

            # case 3: existing target_cluster_id provided
            # (i.e.) image is wrongly clustered (user wants to change the cluster of that image)
            else:
                if is_identity_cluster:
                    # set the cluster as non-identity cluster
                    db_response = cluster.update_cluster_identity(
                        user_id=user_id,
                        cluster_id=cluster_id,
                        file_id=file_id,
                        identity=False
                    )

                    if not db_response["success"]:
                        # abort the request
                        return jsonify({
                            "message": "Error: Database operation failed!",
                            "error": db_response["error"]
                        }), 500

            # update th cluster_id
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

        # return the response
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


# return the requested file to the user
def handle_delete_file(request, user_id):
    # Get file_id from the request
    request_data = request.get_json()
    file_id = request_data.get("fileId")
    cluster_id = request_data.get("clusterId")

    # remove the file from user's cluster (MySQL table) if already clustered
    # check if the file id is identity image in the cluster or not
    is_identity_cluster = False
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

    if db_response["data"]:
        is_identity_cluster = True

    # delete the requested file from the cluster
    db_response = cluster.delete_file_from_cluster(
        user_id=user_id,
        file_id=file_id
    )

    if not db_response["success"]:
        # abort the request
        return jsonify({
            "message": "Error: Database operation failed!"
        }), 500

    if is_identity_cluster:
        # make another image in the cluster as identity
        cluster.update_is_identity_true_in_lowest_match_score(
            user_id=user_id,
            cluster_id=cluster_id
        )

    # emit the changes to all current user socket connections as well
    socket_manager.emit_cluster_refreshed_event(user_id=user_id)
    socket_manager.emit_cluster_id_refreshed_event(user_id=user_id)

    # return the response
    return {
        "message": "Success: File successfully deleted from the cluster!"
    }
