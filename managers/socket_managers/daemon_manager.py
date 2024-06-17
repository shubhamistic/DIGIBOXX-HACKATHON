from sockets import socketio
from flask_jwt_extended import create_access_token
import uuid
from models import cluster, cluster_queue
from utils import data_utils
from managers.socket_managers.socket_manager import SocketManager


data_socket_manager = SocketManager()


class DaemonSocketManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DaemonSocketManager, cls).__new__(cls, *args, **kwargs)
            # create a daemon client authorization key
            # Initialize shared variables here
            daemon_authorization_key = str(uuid.uuid4())
            cls._instance.daemon_authorization_key = daemon_authorization_key
            cls._instance.daemon_client_socket_information = {}
            cls.local_cluster_queue = {}
            cls.is_local_cluster_queue_initialized = False
            # print the daemon authorization key for clients
            print("Daemon Authorization Key:", daemon_authorization_key)
        return cls._instance

    # method to take pending tasks from MySQL cluster_queue and add that to local cluster queue
    def initialize_local_cluster_queue(self):
        if not self.is_local_cluster_queue_initialized:
            # get the initial tasks from the cluster_queue MySQL database
            db_response = cluster_queue.get_all_records()
            if db_response["success"]:
                for rows in db_response["data"]:
                    file_id = rows[0]
                    user_id = rows[1]
                    file_type = rows[2]

                    self.local_cluster_queue[file_id] = {
                        "file_id": file_id,
                        "user_id": user_id,
                        "file_type": file_type,
                        "client_socket_id": None
                    }

                # set is local cluster queue initialized to true
                self.is_local_cluster_queue_initialized = True

    # method to add a task to local cluster queue
    def add_task_to_cluster_queue(self, user_id, file_id, file_type):
        # save the task to local cluster queue
        self.local_cluster_queue[file_id] = {
            "file_id": file_id,
            "user_id": user_id,
            "file_type": file_type,
            "client_socket_id": None
        }
        # also save the data to mysql database
        cluster_queue.insert_record(
            user_id=user_id,
            file_id=file_id,
            file_type=file_type
        )

        # assign the clustering task to the client
        self.assign_clustering_task()

    # method to remove a task from local cluster queue
    def remove_task_from_cluster_queue(self, user_id, file_id):
        # remove the task from local cluster queue
        if file_id in self.local_cluster_queue:
            del self.local_cluster_queue[file_id]

        # also remove the data from mysql cluster_queue table
        cluster_queue.delete_record(file_id=file_id)

    # method to check if a socket id is an authorized clustering client or not
    def is_socket_authorized(self, socket_id):
        if socket_id in self.daemon_client_socket_information:
            return True
        return False

    # method to authorize and add client's socket I'd to the client information list
    def authorize_and_add_socket_to_room(self, socket_id, authorization_key):
        if socket_id not in self.daemon_client_socket_information:
            # check if the clustering client has the correct authorization key
            if authorization_key == self.daemon_authorization_key:
                self.daemon_client_socket_information[socket_id] = {
                    "is_available": True
                }

                # return the authorization response
                return {
                    "authorized": True,
                    "jwt_token": create_access_token(identity=socket_id)
                }

        # return the authorization response
        return {"authorized": False}

    # method to remove a client's socket I'd from the client information list
    def remove_socket_from_room(self, socket_id):
        if socket_id in self.daemon_client_socket_information:
            # revoke all the task assigned to this client so that another client can proceed with this task
            for task_file_id, task_info in self.local_cluster_queue.items():
                if task_info["client_socket_id"] == socket_id:
                    self.local_cluster_queue[task_file_id]["client_socket_id"] = None

            # remove the socket id from daemon clients
            del self.daemon_client_socket_information[socket_id]

    # method to fetch the tasks from cluster queue and assign it to all the available clustering clients
    def assign_clustering_task(self):
        # initialize the local cluster queue if not initialized
        self.initialize_local_cluster_queue()

        # iterate over all the task in the cluster queue
        for task_file_id, task_info in self.local_cluster_queue.items():
            # check for the available task in cluster queue
            if task_info["client_socket_id"]:
                continue

            # search for the available client and assign the clustering task
            for socket_id, client_info in self.daemon_client_socket_information.items():
                # check if the client is available for work
                if client_info["is_available"]:
                    # create user cluster table if not exists
                    db_response = cluster.create_user_cluster_table(task_info["user_id"])
                    if db_response["success"]:
                        # get the user's already clustered data from MySQL database
                        db_response = cluster.get_user_cluster_info(task_info["user_id"])
                        if db_response["success"]:
                            # parse the MySQL data to json
                            cluster_dict = data_utils.parse_user_cluster_data_to_json_for_clustering(
                                db_data=db_response["data"]
                            )

                            # emit the assign task event to the client
                            socketio.emit(
                                'task',
                                {
                                    "message": "A clustering task has been assigned to you!",
                                    "task_info": {
                                        "file_id": task_info["file_id"],
                                        "user_id": task_info["user_id"],
                                        "file_type": task_info["file_type"]
                                    },
                                    "cluster_dict": cluster_dict
                                },
                                namespace="/daemon",
                                room=[socket_id]
                            )

                            # set the client to is-available false until done with the task
                            self.daemon_client_socket_information[socket_id]["is_available"] = False

                            # also update the cluster queue task with the client that is handling the task
                            self.local_cluster_queue[task_file_id]["client_socket_id"] = socket_id

                            break

    # method to handle the task if a client successfully finishes the task
    def handle_task_complete(self, socket_id, task_info, clustering_result):
        if socket_id in self.daemon_client_socket_information:
            user_id = task_info["user_id"]
            file_id = task_info["file_id"]

            # set the client to is-available True
            self.daemon_client_socket_information[socket_id]["is_available"] = True

            # remove the task from cluster_queue
            self.remove_task_from_cluster_queue(
                user_id=task_info["user_id"],
                file_id=task_info["file_id"]
            )

            for each_result in clustering_result:
                cluster_id = each_result["cluster_id"]
                coords = each_result["coords"]
                matched_score = each_result["matched_score"]
                is_identity = each_result["is_identity"]
                cluster.insert_user_cluster_record(
                    user_id=user_id,
                    cluster_id=cluster_id,
                    file_id=file_id,
                    coords=coords,
                    matched_score=matched_score,
                    is_identity=is_identity
                )

            # emit the changes to all sockets of the current user
            data_socket_manager.emit_cluster_refreshed_event(user_id=user_id)
            data_socket_manager.emit_cluster_id_refreshed_event(user_id=user_id)

            # assign the new task to the client
            self.assign_clustering_task()
