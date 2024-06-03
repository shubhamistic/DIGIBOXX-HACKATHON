from flask import Blueprint
from models import auth

# Create a blueprint for / route
null_routes = Blueprint('null', __name__)


@null_routes.route('/', methods=['GET'])
def index():
    # null request does nothing but keeps the db connection active
    auth.read_user_credentials(None)
    # return the response
    return {
        "message": "Successful!"
    }
