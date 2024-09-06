# app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from app.config import Config

db = SQLAlchemy()
api = Api()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    api.init_app(app)

    from app.routes import TaskResource
    api.add_resource(TaskResource, '/tasks', '/tasks/<int:task_id>')

    return app
