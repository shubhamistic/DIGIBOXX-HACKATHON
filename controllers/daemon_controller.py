from flask import jsonify, send_file
import os
from models import data
from managers.socket_managers.daemon_manager import DaemonSocketManager


daemon_socket_manager = DaemonSocketManager()


# return the requested file to the daemon client
def handle_get_file(request, daemon_client_id):
    global daemon_socket_manager

    # Get file_id from the request
    request_data = request.get_json()
    user_id = request_data.get("userId")
    file_id = request_data.get("fileId")

    # check if daemon_client_id is authorized or not
    if not daemon_socket_manager.is_socket_authorized(socket_id=daemon_client_id):
        return jsonify({
            "message": "Error: Client Unauthorized!"
        }), 401

    if user_id and file_id:
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
        "message": "Error: Either User Id or file Id not provided!"
    }), 400
