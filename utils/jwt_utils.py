from flask_jwt_extended import decode_token
import time


def get_jwt_identity(token):
    try:
        decoded_token = decode_token(token[7:])
        if decoded_token['exp'] > time.time():
            return decoded_token['sub']
    except:
        return None
