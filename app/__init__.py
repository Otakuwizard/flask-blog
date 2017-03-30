import pymysql
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_pagedown import PageDown
from ..config import config

bootstrap = Bootstrap()
moment = Moment()
db = SQLAlchemy()
pagedown = PageDown()
mail = Mail()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_nane].init_app(app)
    
    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    pagedown.init_app(app)
    mail.init_app(app)
    
    return app