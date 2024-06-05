from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mysqldb import MySQL
from os import environ
from datetime import timedelta
# routes
from routes.index import index_routes
from routes.auth import auth_routes
from routes.data import data_routes
from routes.null import null_routes
# sockets
from sockets import socketio
import sockets.data

app = Flask(__name__)

# configure jwt
app.config['SECRET_KEY'] = environ.get('SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

# configure MySQL
app.config['MYSQL_USER'] = environ.get('DB_USER')
app.config['MYSQL_PASSWORD'] = environ.get('DB_PASS')
app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_DB'] = "digiboxx"

# define extensions
CORS(app, supports_credentials=True)  # cors
JWTManager(app)  # jwt
socketio.init_app(app, cors_allowed_origins="*", async_mode='gevent')  # socket
mysql = MySQL(app)  # MySQL

# define the routes
app.register_blueprint(index_routes, url_prefix='/')
app.register_blueprint(auth_routes, url_prefix='/auth')
app.register_blueprint(data_routes, url_prefix='/data')
app.register_blueprint(null_routes, url_prefix='/null')

if __name__ == '__main__':
    app.run(debug=True)
    socketio.run(app)
