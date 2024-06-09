from flask import request
from flask_socketio import Namespace
from . import socketio
from managers.socket_managers.daemon_manager import DaemonSocketManager


daemon_socket_manager = DaemonSocketManager()


class DaemonNamespace(Namespace):
    def on_connect(self):
        global daemon_socket_manager

        # get the daemon authorization key token from the request
        authorization_key = request.args.get("Authorization")

        # authenticate and add the daemon
        response = daemon_socket_manager.authorize_and_add_socket_to_room(
            socket_id=request.sid,
            authorization_key=authorization_key
        )

        if not response["authorized"]:
            socketio.emit(
                'unauthorized',
                {"message": "Error: client unauthorized (invalid authorization key)"},
                namespace='/daemon',
                room=[request.sid]
            )
            socketio.server.disconnect(request.sid, namespace='/daemon')
        else:
            socketio.emit(
                'authorized',
                {
                    "message": "Success: Client Authorized Successfully!",
                    "jwt_token": response["jwt_token"]
                },
                namespace='/daemon',
                room=[request.sid]
            )

    def on_disconnect(self):
        global daemon_socket_manager

        # remove the socket id from the room
        daemon_socket_manager.remove_socket_from_room(socket_id=request.sid)

    def on_task_completed(self, data):
        global daemon_socket_manager

        # get the task_info and clustering_result from the data
        task_info = data["task_info"]
        clustering_result = data["clustering_result"]

        # handle task completion
        daemon_socket_manager.handle_task_complete(
            socket_id=request.sid,
            task_info=task_info,
            clustering_result=clustering_result
        )


socketio.on_namespace(DaemonNamespace('/daemon'))
