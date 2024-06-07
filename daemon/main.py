import os
import cv2
import time
import uuid
import socketio
from detect_face import detect_faces
from recognize_face import compare_face_with_multiple_images
from models import cluster, cluster_queue
from utils import data_utils


sio = socketio.Client()
sio.connect('http://127.0.0.1:5000', namespaces=['/daemon'])


def cluster_image(image, cluster_dict):
    # detect the number of faces in the image and get the coords of it
    faces_coords = detect_faces(image)
    # if no faces found then stop clustering
    if not faces_coords:
        return None

    # traverse through each the face
    clustered_info_list = []
    for face_coords in faces_coords:
        # get the height and width of the image
        image_height, image_width = image.shape[:2]
        if len(face_coords) == 1:
            x1, y1, x2, y2 = 0, 0, image_width, image_height
            face_image = image
        else:
            x, y, w, h = face_coords
            x1, y1, x2, y2 = x, y, x + w, y + h
            w_15_p = int((image_width / 100) * 15)  # width_15_percent
            h_15_p = int((image_height / 100) * 15)  # height_15_percent
            x1, y1, x2, y2 = max(0, x1 - w_15_p), max(0, y1 - h_15_p), min(x2 + w_15_p, image_width), min(y2 + h_15_p, image_height)
            # crop the face out of image to cluster
            face_image = image[y1:y2, x1:x2]

        for cluster_id, clustered_images in cluster_dict.items():
            result = compare_face_with_multiple_images(face_image, clustered_images)
            if result["matched"]:
                clustered_info_list.append({
                    "is_existing_cluster": True,
                    "cluster_id": cluster_id,
                    "coords": [x1, y1, x2, y2],
                    "matched_score": result["matched_score"]
                })
                break
        else:
            cluster_id = str(uuid.uuid4()).replace('-', '_')
            clustered_info_list.append({
                "is_existing_cluster": False,
                "cluster_id": cluster_id,
                "coords": [x1, y1, x2, y2],
                "matched_score": 100
            })

    return clustered_info_list


if __name__ == "__main__":
    file_id, user_id, file_type = None, None, None
    while True:
        try:
            # get a record to cluster from the cluster queue
            db_response = cluster_queue.get_record()
            if db_response["success"]:
                print(db_response["data"])
                file_id = db_response["data"][0]
                user_id = db_response["data"][1]
                file_type = db_response["data"][2]
                print(f"file_id: {file_id} | user_id: {user_id}")
                # currently the algo works for an image file only
                if file_type == "image":
                    # define the path for image to cluster
                    image_to_cluster_path = f"../data/{user_id}/{file_id}.png"
                    # check if the image exists in that path or not
                    if os.path.exists(image_to_cluster_path):
                        # create user cluster table if not exists
                        db_response = cluster.create_user_cluster_table(user_id)
                        if db_response["success"]:
                            # get the already clustered faces data
                            db_response = cluster.get_user_cluster_info(user_id)
                            if db_response["success"]:
                                # read the image using open cv
                                image_to_cluster = cv2.imread(image_to_cluster_path)
                                # populate the cluster dict
                                cluster_dict = data_utils.parse_db_data_to_json(db_response["data"])
                                # replace the file_id in cluster_dict with the cv2 image
                                for cluster_id, clustered_image_file_infos in cluster_dict.items():
                                    clustered_image_list = []
                                    for clustered_image_file_info in clustered_image_file_infos:
                                        clustered_image_file_id = clustered_image_file_info["file_id"]
                                        x1, y1, x2, y2 = clustered_image_file_info["coords"]
                                        # define the path for image to cluster
                                        path_to_clustered_image = f"../data/{user_id}/{clustered_image_file_id}.png"
                                        if os.path.exists(path_to_clustered_image):
                                            clustered_image = cv2.imread(path_to_clustered_image)
                                            clustered_image = clustered_image[y1:y2, x1:x2]
                                            clustered_image_list.append(clustered_image)

                                    if clustered_image_list:
                                        cluster_dict[cluster_id] = clustered_image_list
                                    else:
                                        del cluster_dict[cluster_id]

                                # cluster the image_to_cluster based on cluster_dict
                                clustered_info_list = cluster_image(image_to_cluster, cluster_dict)
                                if clustered_info_list:
                                    for clustered_info in clustered_info_list:
                                        if clustered_info["is_existing_cluster"]:
                                            cluster.insert_user_cluster_record(
                                                user_id=user_id,
                                                cluster_id=clustered_info["cluster_id"],
                                                file_id=file_id,
                                                coords=clustered_info["coords"],
                                                matched_score=clustered_info["matched_score"],
                                            )
                                        else:
                                            cluster.insert_user_cluster_record(
                                                user_id=user_id,
                                                cluster_id=clustered_info["cluster_id"],
                                                file_id=file_id,
                                                coords=clustered_info["coords"],
                                                matched_score=clustered_info["matched_score"],
                                                is_identity=True
                                            )
                                    # write the change to daemon shared file
                                    # so that flask can emit the changes to user through socket
                                    sio.emit(
                                        'daemon_refresh',
                                        {'userId': user_id},
                                        namespace='/daemon'
                                    )

                                # delete the record from the cluster queue
                                cluster_queue.delete_record(file_id)
                    else:
                        # delete the record from the cluster queue
                        cluster_queue.delete_record(file_id)
                        pass
                else:
                    # delete the record from the cluster queue
                    cluster_queue.delete_record(file_id)
                    pass
            else:
                # as no record found make the code sleep for 5 seconds
                print("Waiting 5 seconds")
                time.sleep(5)

        except Exception as error:
            print("ERROR:", error)
            if file_id and user_id and file_type:
                # delete the record from the cluster queue
                cluster_queue.delete_record(file_id)
