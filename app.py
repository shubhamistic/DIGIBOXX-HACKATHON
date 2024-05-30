from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from os import environ
from datetime import timedelta
# routes
from routes.auth import auth_routes

app = Flask(__name__)

# configure jwt
app.config['SECRET_KEY'] = environ.get('SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

# define extensions
CORS(app, supports_credentials=True)  # cors
JWTManager(app)  # jwt

app.register_blueprint(auth_routes, url_prefix='/auth')

if __name__ == '__main__':
    app.run(debug=True)
