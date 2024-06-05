from flask import jsonify, send_file
from PIL import Image
import uuid
import os
from models import cluster
from managers.socket_managers.data_socket_manager import DataSocketManager


def handle_get_distinct_cluster(request, user_id):
    pass
