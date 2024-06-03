from flask import Blueprint, render_template

# Create a blueprint for / route
index_routes = Blueprint('/', __name__)


@index_routes.route('/', methods=['GET'])
def index():
    return render_template('index.html')
