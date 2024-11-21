from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user
from flask_sslify import SSLify
import os

# git reset --hard HEAD

app = Flask(__name__)
if 'DYNO' in os.environ:  # Força HTTPS na heroku
    sslify = SSLify(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
token = os.environ.get('TOKEN_CRIAR_ACESSO')

# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.session_protection = 'strong'
login_manager.login_message = "É necessário fazer login para acessar essa página."
login_manager.login_message_category = 'alert-info'


database = SQLAlchemy(app)

from . import routes
