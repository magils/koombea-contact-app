import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from app.config import AppConfig, ProdConfig
from app.errors import APIError, handler_api_errors
from flask_bcrypt import Bcrypt
import os


db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
bcrypt = Bcrypt()

conf = ProdConfig if os.environ.get("ENV", "") == "prod" else AppConfig


def get_logger(name):
    logger = logging.getLogger(name)
    c_handler = logging.StreamHandler()
    c_handler.setLevel(logging.INFO)
    c_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(lineno)d: %(message)s")
    )
    logger.addHandler(c_handler)

    return logger

def setup_modules(app):
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)

def setup_blueprints(app):
    from app.resources.contacts import contacts_resource
    from app.resources.users import users_resource

    app.register_blueprint(contacts_resource)
    app.register_blueprint(users_resource)

def create_app():
    app = Flask(__name__)
    app.config.from_object(conf)
    app.register_error_handler(APIError, handler_api_errors)
    setup_modules(app)
    setup_blueprints(app)

    return app

