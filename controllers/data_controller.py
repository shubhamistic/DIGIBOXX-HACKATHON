from flask import jsonify
from PIL import Image
import uuid
import os
from models import data, cluster


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
                db_response = cluster.insert_cluster_queue_record(
                    user_id=user_id,
                    file_id=file_id,
                    file_type=file_type
                )

                if not db_response["success"]:
                    # abort the request
                    return jsonify({
                        "message": "Error: Database operation failed!"
                    }), 500

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
        db_response = cluster.delete_cluster_queue_record(file_id=file_id)

        if not db_response["success"]:
            # abort the request
            return jsonify({
                "message": "Error: Database operation failed!"
            }), 500

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
    pass
