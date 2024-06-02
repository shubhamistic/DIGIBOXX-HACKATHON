from flask import request
from flask_socketio import Namespace
from . import socketio
from managers.socket_managers.data_socket_manager import DataSocketManager
from utils import jwt_utils


data_socket_manager = DataSocketManager()


class DataNamespace(Namespace):
    def on_connect(self):
        global data_socket_manager

        # get the jwt token from the socket connection request
        jwt_token = request.args.get("jwt_token")

        if jwt_token:
            # decode the jwt token and get the user Id
            user_id = jwt_utils.get_jwt_identity(jwt_token)

            # add the socket id to the user room
            data_socket_manager.add_socket_to_room(
                user_id=user_id,
                socket_id=request.sid
            )

            # emit the data
            data_socket_manager.emit_data_refreshed_event(user_id=user_id)

    def on_disconnect(self):
        global data_socket_manager

        # remove the socket id from the room
        data_socket_manager.remove_socket_from_room(socket_id=request.sid)


socketio.on_namespace(DataNamespace('/data'))
