from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from app.config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    
    from app.resources import TaskResource
    api = Api(app)
    api.add_resource(TaskResource, '/api/tasks', '/api/tasks/<int:task_id>')
    
    return app
