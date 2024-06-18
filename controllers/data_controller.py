from flask import jsonify, send_file
from PIL import Image
import uuid
import os
from models import data, cluster
from managers.socket_managers.socket_manager import SocketManager
from managers.socket_managers.daemon_manager import DaemonSocketManager


socket_manager = SocketManager()
daemon_socket_manager = DaemonSocketManager()


# upload a file into the user directory and queue it for clustering
def handle_upload_file(request, user_id):
    # Get file and file_type from the request
    file = request.files['file']
    file_type = request.form.get('fileType')

    if file and file_type:
        # create user_data table in MySQL database if not exists
        db_response = data.create_user_data_table(user_id=user_id)
        if not db_response["success"]:
            # abort the request
            return jsonify({
                "message": "Error: Database operation failed!"
            }), 500

        user_data_path = os.path.join("data", f"{user_id}")
        # Check if the directory exists, if not, create it
        if not os.path.exists(user_data_path):
            # create a user data directory if not exists
            os.makedirs(user_data_path)

        # check if the file type is "image" or "video"
        if file_type == "image":
            try:
                # Open the image file using PIL
                image = Image.open(file)

                # Convert and save the image as PNG
                file_id = str(uuid.uuid4()).replace('-', '_')
                image.save(f"data/{user_id}/{file_id}.png", format='PNG')

                # insert the image record to MySQL database
                db_response = data.insert_file_record(
                    user_id=user_id,
                    file_id=file_id,
                    file_type=file_type
                )

                if not db_response["success"]:
                    # abort the request
                    return jsonify({
                        "message": "Error: Database operation failed!"
                    }), 500

                # queue the image for clustering as well
                daemon_socket_manager.add_task_to_cluster_queue(
                    user_id=user_id,
                    file_id=file_id,
                    file_type=file_type
                )

                # emit the changes to all current user socket connections as well
                socket_manager.emit_data_refreshed_event(user_id=user_id)

                # return the response
                return {
                    "message": "Success: Image successfully uploaded and queued for clustering!",
                    "fileId": file_id,
                    "fileType": file_type
                }

            except Exception as error:
                return jsonify({
                    "message": "Failed to save the image!",
                    "error": error
                }), 500

        elif file_type == "video":
            return jsonify({
                "message": "This functionality is not available yet!"
            }), 501

        else:
            return jsonify({
                "message": "The file type is not supported!"
            }), 415

    # abort the request
    return jsonify({
        "message": "Error: Either file or file_type not provided!"
    }), 400


# delete a file from user directory
def handle_delete_file(request, user_id):
    # Get file_id from the request
    request_data = request.get_json()
    file_id = request_data.get("fileId")

    if file_id:
        user_data_path = os.path.join("data", f"{user_id}")
        if not os.path.exists(user_data_path):
            # abort the request
            return jsonify({
                "message": "Error: User directory not found!"
            }), 404

        file_path = os.path.join(user_data_path, f"{file_id}.png")
        if os.path.exists(file_path):
            os.remove(file_path)

        # delete the file record from MySQL database
        db_response = data.delete_file_record(
            user_id=user_id,
            file_id=file_id
        )

        if not db_response["success"]:
            # abort the request
            return jsonify({
                "message": "Error: Database operation failed!"
            }), 500

        # dequeue the file from clustering queue as well
        daemon_socket_manager.remove_task_from_cluster_queue(
            user_id=user_id,
            file_id=file_id
        )

        # handle deletion from cluster records as well
        file_cluster_info = []
        db_response = cluster.get_file_cluster_info(
            user_id=user_id,
            file_id=file_id
        )

        if db_response["success"]:
            file_cluster_info = db_response["data"]

        # iterate over each row and delete the record
        # if image is identity image then make another image as identity image
        for cluster_row in file_cluster_info:
            cluster_id = cluster_row[1]  # cluster_id

            # check if the file id is identity image in the cluster or not
            is_identity_cluster = False
            db_response = cluster.get_identity_cluster_file_info(
                user_id=user_id,
                cluster_id=cluster_id,
                file_id=file_id
            )

            if db_response["success"] and db_response["data"]:
                is_identity_cluster = True

            # delete the requested file record from the cluster
            cluster.delete_file_from_cluster(
                user_id=user_id,
                file_id=file_id,
                cluster_id=cluster_id
            )

            if is_identity_cluster:
                # make another image in the cluster as identity
                cluster.update_is_identity_true_in_lowest_match_score(
                    user_id=user_id,
                    cluster_id=cluster_id
                )

        # delete the file existence from the cluster table
        cluster.delete_file_existence_from_cluster(
            user_id=user_id,
            file_id=file_id
        )

        # emit the changes to all current user socket connections as well
        socket_manager.emit_data_refreshed_event(user_id=user_id)
        socket_manager.emit_cluster_refreshed_event(user_id=user_id)
        socket_manager.emit_cluster_id_refreshed_event(user_id=user_id)

        # return the response
        return {
            "message": "Success: File successfully deleted!",
            "fileId": file_id
        }

    # abort the request
    return jsonify({
        "message": "Error: file ID not provided!"
    }), 400


# return the requested file to the user
def handle_get_file(request, user_id):
    # Get file_id from the request
    request_data = request.get_json()
    file_id = request_data.get("fileId")

    if file_id:
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

            # Return the image
            return send_file(image_file_path, mimetype='image/png')

        if file_type == 'video':
            # abort the request
            return jsonify({
                "message": "This functionality is not available yet!"
            }), 501

    # abort the request
    return jsonify({
        "message": "Error: file ID not provided!"
    }), 400
