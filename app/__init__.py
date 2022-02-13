import logging
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from app.config import AppConfig
from app.errors import APIError, handler_api_errors

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


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

def setup_blueprints(app):
    from app.resources import contacts_resource
    app.register_blueprint(contacts_resource)

def create_app():
    app = Flask(__name__)
    app.config.from_object(AppConfig)
    app.register_error_handler(APIError, handler_api_errors)
    setup_modules(app)
    setup_blueprints(app)

    return app

