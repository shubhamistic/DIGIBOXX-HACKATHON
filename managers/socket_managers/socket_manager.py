from sockets import socketio
import copy
from models import data, cluster
from utils import data_utils


class SocketManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SocketManager, cls).__new__(cls, *args, **kwargs)
            # Initialize shared variables here
            cls._instance.socket_room_information = {}
            cls._instance.socket_id_room_information = {}
            cls._instance.socket_id_cluster_information = {}
        return cls._instance

    def add_socket_to_room(self, user_id, socket_id):
        if user_id in self.socket_room_information:
            if socket_id not in self.socket_room_information[user_id]:
                self.socket_room_information[user_id].append(socket_id)
                self.socket_id_room_information[socket_id] = user_id
        else:
            self.socket_room_information[user_id] = [socket_id]
            self.socket_id_room_information[socket_id] = user_id

    def remove_socket_from_room(self, socket_id):
        if socket_id in self.socket_id_room_information:
            user_id = self.socket_id_room_information[socket_id]
            if user_id in self.socket_room_information:
                if socket_id in self.socket_room_information[user_id]:
                    self.socket_room_information[user_id].remove(socket_id)
                    if not self.socket_room_information[user_id]:
                        del self.socket_room_information[user_id]
            del self.socket_id_room_information[socket_id]

    def emit_data_refreshed_event(self, user_id, emit_to_all=True, socket_id=None):
        if user_id in self.socket_room_information:
            db_response = data.get_all_records_datewise_sorted(user_id)
            if db_response["success"]:
                # parse the data received from the db to json format
                refreshed_data = data_utils.parse_user_data_to_json(db_response["data"])

                if emit_to_all:
                    room = self.socket_room_information[user_id]
                else:
                    room = [socket_id]

                # emit the refreshed data
                socketio.emit(
                    'refreshed',
                    {
                        "message": "User data refreshed!",
                        "data": refreshed_data
                    },
                    namespace="/data",
                    room=room
                )

    def add_cluster_id_to_socket(self, socket_id, cluster_id):
        if socket_id in self.socket_id_room_information:
            self.socket_id_cluster_information[socket_id] = cluster_id

    def emit_cluster_refreshed_event(self, emit_to_all=True, socket_id=None, user_id=None):
        if not emit_to_all:
            if socket_id in self.socket_id_room_information:
                user_id = self.socket_id_room_information[socket_id]

        if user_id in self.socket_room_information:
            db_response = cluster.get_user_identity_cluster_info(user_id)
            if db_response["success"]:
                # parse the data received from the db to json format
                refreshed_data = data_utils.parse_user_distinct_cluster_to_json(db_response["data"])

                if emit_to_all:
                    room = self.socket_room_information[user_id]
                else:
                    room = [socket_id]

                # emit the refreshed data
                socketio.emit(
                    'cluster_refreshed',
                    {
                        "message": "Cluster data refreshed!",
                        "data": refreshed_data
                    },
                    namespace="/data",
                    room=room
                )

    def _emit_cluster_id_refreshed_event(self, socket_id, user_id):
        if socket_id in self.socket_id_cluster_information:
            cluster_id = self.socket_id_cluster_information[socket_id]
            db_response = cluster.get_specific_cluster_info(
                user_id=user_id,
                cluster_id=cluster_id
            )
            if db_response["success"]:
                # parse the data received from the db to json format
                refreshed_data = data_utils.parse_user_cluster_data_to_json(db_response["data"])

                # emit the refreshed data
                socketio.emit(
                    'cluster_id_refreshed',
                    {
                        "message": "Cluster Id data refreshed!",
                        "data": refreshed_data
                    },
                    namespace="/data",
                    room=[socket_id]
                )

    def emit_cluster_id_refreshed_event(self, emit_to_all=True, socket_id=None, user_id=None):
        if not emit_to_all:
            if socket_id in self.socket_id_room_information:
                user_id = self.socket_id_room_information[socket_id]
                self._emit_cluster_id_refreshed_event(socket_id, user_id)
        else:
            if user_id in self.socket_room_information:
                for socket_id in self.socket_room_information[user_id]:
                    self._emit_cluster_id_refreshed_event(socket_id, user_id)

    def disconnect_all_sockets(self, socket_id):
        if socket_id in self.socket_id_room_information:
            user_id = self.socket_id_room_information[socket_id]
            if user_id in self.socket_room_information:
                room = copy.deepcopy(self.socket_room_information[user_id])

                # emit the disconnect user event
                socketio.emit(
                    'disconnect_user',
                    {
                        "message": "All sockets in current user disconnected!"
                    },
                    namespace="/data",
                    room=room
                )

                # break the socket connections
                for each_socket_id in room:
                    socketio.server.disconnect(each_socket_id, namespace='/data')
