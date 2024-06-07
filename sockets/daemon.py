from flask_socketio import Namespace
from . import socketio
from managers.socket_managers.socket_manager import SocketManager


socket_manager = SocketManager()


class DaemonNamespace(Namespace):
    def on_connect(self):
        pass

    def on_disconnect(self):
        pass

    def on_daemon_refresh(self, data):
        user_id = data["userId"]
        # emit the events
        socket_manager.emit_cluster_refreshed_event(user_id=user_id)
        socket_manager.emit_cluster_id_refreshed_event(user_id=user_id)


socketio.on_namespace(DaemonNamespace('/daemon'))
