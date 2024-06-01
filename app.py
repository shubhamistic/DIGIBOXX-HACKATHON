from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from os import environ
from datetime import timedelta
# routes
from routes.index import index_routes
from routes.auth import auth_routes
from routes.data import data_routes

app = Flask(__name__)

# configure jwt
app.config['SECRET_KEY'] = environ.get('SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

# define extensions
CORS(app, supports_credentials=True)  # cors
JWTManager(app)  # jwt

# define the routes
app.register_blueprint(index_routes, url_prefix='/')
app.register_blueprint(auth_routes, url_prefix='/auth')
app.register_blueprint(data_routes, url_prefix='/data')

if __name__ == '__main__':
    app.run(debug=True)
