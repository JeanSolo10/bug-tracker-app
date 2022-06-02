from flask import Flask
import os
from dotenv import load_dotenv, find_dotenv
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = "bugtracker_db"

def create_app():
    app = Flask(__name__)
    load_dotenv(find_dotenv())
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    # db config
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Project, Ticket, Comment

    create_database(app)

    # check for authenticated users and redirect accordingly
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app

def create_database(app):
    # check if database exists
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)