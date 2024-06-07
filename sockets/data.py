from flask import request
from flask_socketio import Namespace
from . import socketio
from managers.socket_managers.socket_manager import SocketManager
from utils import jwt_utils


socket_manager = SocketManager()


class DataNamespace(Namespace):
    def on_connect(self):
        global socket_manager

        # get the jwt token from the socket connection request
        jwt_token = request.args.get("jwt_token")

        # decode the jwt token and get the user Id
        user_id = jwt_utils.get_jwt_identity(jwt_token)

        if jwt_token and user_id:
            # add the socket id to the user room
            socket_manager.add_socket_to_room(
                user_id=user_id,
                socket_id=request.sid
            )

            # emit the data
            socket_manager.emit_data_refreshed_event(
                user_id=user_id,
                emit_to_all=False,
                socket_id=request.sid
            )
        else:
            socketio.server.disconnect(request.sid, namespace='/data')

    def on_disconnect(self):
        global socket_manager

        # remove the socket id from the room
        socket_manager.remove_socket_from_room(socket_id=request.sid)

    def on_disconnect_all_sockets(self, data):
        global socket_manager

        socket_manager.disconnect_all_sockets(socket_id=request.sid)

    def on_cluster(self, data):
        global socket_manager

        # emit the data
        socket_manager.emit_cluster_refreshed_event(
            emit_to_all=False,
            socket_id=request.sid
        )

    def on_cluster_id(self, data):
        global socket_manager

        cluster_id = data["clusterId"]

        # map the cluster_id with the socket id
        socket_manager.add_cluster_id_to_socket(
            socket_id=request.sid,
            cluster_id=cluster_id
        )

        # emit the data
        socket_manager.emit_cluster_id_refreshed_event(
            emit_to_all=False,
            socket_id=request.sid
        )


socketio.on_namespace(DataNamespace('/data'))
