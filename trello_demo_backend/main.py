from flask import Flask, request, jsonify
from controllers.db_controller import create_task, get_task, update_task, delete_task, get_columns, move_task_and_update_columns
from models.task_model import Task
from flask import Blueprint
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)
task_blueprint = Blueprint('task_blueprint', __name__)
column_blueprint = Blueprint('column_blueprint', __name__)
PORT = os.getenv("PORT")


@task_blueprint.route('/tasks', methods=['POST'])
def add_task():
    try:
        task = request.get_json()
        task = Task(**task)
        return create_task(task.task_id, task.task_name, task.description, task.column_id, task.index)
    except Exception as e:
        return jsonify({'success': False, 'message': "Internal Server Error", 'Error': e}), 500


@task_blueprint.route('/tasks/<string:task_id>/<string:column_id>', methods=['GET'])
def get_single_task(task_id, column_id):
    return get_task(task_id, column_id)


@task_blueprint.route('/tasks', methods=['PUT'])
def update_single_task():
    try:
        task = request.get_json()
        task = Task(**task)
        return update_task(task.task_id, task.column_id, task.task_name, task.description, task.index)
    except Exception as e:
        return jsonify({'success': False, 'message': "Internal Server Error", 'Error': e})


@task_blueprint.route('/move_task', methods=['PUT'])
def move_task():
    try:
        data = request.get_json()
        if data['destination_column'] is not None:
            return move_task_and_update_columns(data['source_column'], data['destination_column'])
        else:
            destination_column = None
            return move_task_and_update_columns(data['source_column'], destination_column)
    except Exception as e:
        return jsonify({'success': False, 'message': "Internal Server Error", 'error': e}), 500


@task_blueprint.route('/tasks/<string:task_id>/<string:column_id>', methods=['DELETE'])
def delete_single_task(task_id, column_id):
    return delete_task(task_id, column_id)


@task_blueprint.route('/')
def hello_world():
    return 'Hello, World!'


@column_blueprint.route('/columns', methods=['GET'])
def get_all_columns():
    return get_columns()


# Register the blueprint with the main app
app.register_blueprint(task_blueprint, url_prefix='/task_routes')
app.register_blueprint(column_blueprint, url_prefix='/columns_routes')

if __name__ == '__main__':
    app.run(debug=True, port=PORT)
