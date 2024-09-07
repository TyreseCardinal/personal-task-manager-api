from flask_restful import Resource
from flask import request
from app import db
from app.models import Task

class TaskResource(Resource):
    def get(self, task_id=None):
        if task_id:
            task = Task.query.get_or_404(task_id)
            return task.to_dict(), 200
        tasks = Task.query.all()
        return [task.to_dict() for task in tasks], 200

    def post(self):
        data = request.get_json()
        task = Task(title=data['title'], completed=data.get('completed', False))
        db.session.add(task)
        db.session.commit()
        return task.to_dict(), 201

    def put(self, task_id):
        data = request.get_json()
        task = Task.query.get_or_404(task_id)
        task.title = data['title']
        task.completed = data.get('completed', task.completed)
        db.session.commit()
        return task.to_dict(), 200

    def delete(self, task_id):
        task = Task.query.get_or_404(task_id)
        db.session.delete(task)
        db.session.commit()
        return {'message': 'Task deleted'}, 204
