import config
import os
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
login_manager = LoginManager()

#helps to initialize the core applications
def create_app():
    #within this app we create Flask App
    app = Flask(__name__)
    environment_configuration = os.environ['CONFIGURATION_SETUP']
    app.config.from_object(environment_configuration)

    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        #Register blueprints
        from .perm_api import perm_api_blueprint
        app.register_blueprint(perm_api_blueprint)
        return app