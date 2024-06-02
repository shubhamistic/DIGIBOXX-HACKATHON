from sockets import socketio
import copy
from models import data
from utils import data_utils


class DataSocketManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DataSocketManager, cls).__new__(cls, *args, **kwargs)
            # Initialize shared variables here
            cls._instance.socket_room_information = {}
            cls._instance.socket_id_room_information = {}
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
                refreshed_data = data_utils.parse_db_data_to_json(db_response["data"])

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

    def disconnect_all_sockets(self, socket_id):
        if socket_id in self.socket_id_room_information:
            user_id = self.socket_id_room_information[socket_id]
            if user_id in self.socket_room_information:
                room = copy.deepcopy(self.socket_room_information[user_id])
                for each_socket_id in room:
                    socketio.server.disconnect(each_socket_id, namespace='/data')
