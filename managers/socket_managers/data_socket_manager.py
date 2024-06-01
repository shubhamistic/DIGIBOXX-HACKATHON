from sockets import socketio
from models import data


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
            if user_id in  self.socket_room_information:
                if socket_id in self.socket_room_information[user_id]:
                    self.socket_room_information[user_id].remove(socket_id)
                    if not self.socket_room_information[user_id]:
                        del self.socket_room_information[user_id]
            del self.socket_id_room_information[socket_id]

    def emit_data_refreshed_event(self, user_id):
        if user_id in self.socket_room_information:
            db_response = data.get_all_records_datewise_sorted(user_id)
            if db_response["success"]:
                refreshed_data = []
                cur_data = {}
                for record in db_response["data"]:
                    date = record[2]
                    month_year = f"{date.month}/{date.year}"
                    if cur_data in refreshed_data and cur_data["date"] == month_year:
                        cur_data = {
                            "date": month_year,
                            "info": refreshed_data[-1]["info"] + [{
                                "fileId": record[0],
                                "fileType": record[1],
                                "uploadDate": f"{date.day}/{month_year}"
                            }]
                        }
                        refreshed_data[-1] = cur_data
                    else:
                        cur_data = {
                            "date": month_year,
                            "info": [{
                                "fileId": record[0],
                                "fileType": record[1],
                                "uploadDate": f"{date.day}/{month_year}"
                            }]
                        }
                        refreshed_data.append(cur_data)

                socketio.emit(
                    'refreshed',
                    {
                        "message": "User data refreshed!",
                        "data": refreshed_data
                    },
                    namespace="/data",
                    room=self.socket_room_information[user_id]
                )
