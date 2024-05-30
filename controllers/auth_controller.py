from flask import abort
from flask_jwt_extended import create_access_token, create_refresh_token, decode_token
import uuid
from models import auth
from utils import bcrypt_utils


# get access token in exchange of refresh token
def handle_authentication(user_id):
    # generate JWT access token
    access_token = create_access_token(identity=user_id)

    # return the response
    return {
        "message": "Success: Authentication Successful!",
        "access_token": f'Bearer {access_token}',
        "userId": user_id
    }


def handle_sign_in(request):
    # Get email id and password from the request
    request_data = request.get_json()
    email_id = request_data.get("emailId")
    password = request_data.get("password")

    if email_id and password:
        # get the actual user credentials from MySQL database
        db_response = auth.read_user_credentials(email_id)

        if db_response["success"]:
            if not db_response["data"]:
                # abort the request
                abort(409, "Error: User with the provided email id does not exists!")
        else:
            # abort the request
            abort(500, "Error: Database operation failed!")

        # match user credentials
        user_id = db_response["data"][0][0]
        actual_password = db_response["data"][0][2]

        if bcrypt_utils.check_password(password, actual_password):
            # create user access and refresh token
            access_token = create_access_token(identity=user_id)
            refresh_token = create_refresh_token(identity=user_id)
            # return the response
            return {
                "message": "Success: Authentication Successful!",
                "userId": user_id,
                "access_token": f'Bearer {access_token}',
                "refresh_token": f'Bearer {refresh_token}'
            }

        # abort the request
        abort(401, "Error: Incorrect user credentials (password)!")

    # abort the request
    abort(400, "Error: Either email id or password not provided!")


def handle_sign_up(request):
    # get the email_id and password from the request
    request_data = request.get_json()
    email_id = request_data.get("emailId")
    password = request_data.get("password")

    if email_id and password:
        # get the actual user credentials from MySQL database
        db_response = auth.read_user_credentials(email_id)

        # check if user with this email id already exists or not
        if db_response["success"]:
            if db_response["data"]:
                # abort the request
                abort(409, "Error: User with the provided email id already exists!")
        else:
            # abort the request
            abort(500, "Error: Database operation failed!")

        # create a new user:-
        # generate a random id for user
        user_id = str(uuid.uuid4())

        # hash the password using bcrypt hashing algorithm
        hashed_password = bcrypt_utils.hash_password(password)

        # insert the user credentials into MySQL database
        db_response = auth.create_user_credentials(user_id, email_id, hashed_password)

        if db_response["success"]:
            # create user access and refresh token
            access_token = create_access_token(identity=user_id)
            refresh_token = create_refresh_token(identity=user_id)
            # return the response
            return {
                "message": "Success: User Successfully Created!",
                "userId": user_id,
                "access_token": f'Bearer {access_token}',
                "refresh_token": f'Bearer {refresh_token}'
            }

        # abort the request
        abort(500, "Error: Database operation failed!")

    # abort the request
    abort(400, "Error: Either email id or password not provided!")
