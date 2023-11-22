from flask import jsonify
from boto3.dynamodb.conditions import Key
from botocore.exceptions import NoCredentialsError
import boto3
import os
from botocore.exceptions import ClientError

DYNAMO_DB_ENDPOINT_URL = os.getenv("DYNAMO_DB_ENDPOINT_URL")

# Connect to DynamoDB Local without credentials
dynamodb = boto3.resource('dynamodb', region_name='us-west-2', endpoint_url=DYNAMO_DB_ENDPOINT_URL)


# create a new task table
def create_task_table(table_name, key_schema, attribute_definitions, provisioned_throughput):
    try:
        # Connect to DynamoDB Local without credentials (replace with your actual setup)
        dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')

        # Check if the table already exists
        existing_tables = dynamodb.meta.client.list_tables()['TableNames']
        if table_name in existing_tables:
            print(f"Table '{table_name}' already exists. Skipping table creation.")
            return False

        # Create the table
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=key_schema,
            AttributeDefinitions=attribute_definitions,
            ProvisionedThroughput=provisioned_throughput
        )

        # Wait for the table to be created before moving forward
        table.meta.client.get_waiter('table_exists').wait(TableName=table_name)

        print(f"Table '{table_name}' created successfully.")
        return True

    except Exception as e:
        print(f"Error creating table '{table_name}': {e}")
        return False


table_name = 'tasks'
key_schema = [
    {
        'AttributeName': 'task_id',
        'KeyType': 'HASH'  # Partition key
    },
    {
        'AttributeName': 'column_id',
        'KeyType': 'RANGE'  # Sort key
    }
]
attribute_definitions = [
    {
        'AttributeName': 'task_id',
        'AttributeType': 'S'  # String
    },
    {
        'AttributeName': 'column_id',
        'AttributeType': 'S'  # String
    },
]
provisioned_throughput = {
    'ReadCapacityUnits': 5,
    'WriteCapacityUnits': 5
}


# create a new table
def create_column_table(table_name, key_schema, attribute_definitions, provisioned_throughput):
    try:
        # Connect to DynamoDB Local without credentials (replace with your actual setup)
        dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')

        # Check if the table already exists
        existing_tables = dynamodb.meta.client.list_tables()['TableNames']
        if table_name in existing_tables:
            print(f"Table '{table_name}' already exists. Skipping table creation.")
            return False

        # Create the table
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=key_schema,
            AttributeDefinitions=attribute_definitions,
            ProvisionedThroughput=provisioned_throughput
        )

        # Wait for the table to be created before moving forward
        table.meta.client.get_waiter('table_exists').wait(TableName=table_name)

        print(f"Table '{table_name}' created successfully.")
        return True

    except Exception as e:
        print(f"Error creating table '{table_name}': {e}")
        return False


column_table = 'columns'
column_key_schema = [
    {
        'AttributeName': 'column_id',
        'KeyType': 'HASH'  # Partition key
    },
    # {
    #     'AttributeName': 'tasks',
    #     'KeyType': 'RANGE'  # Sort key
    # }
]
column_attribute_definitions = [
    {
        'AttributeName': 'column_id',
        'AttributeType': 'S'  # String
    },
    # {
    #     'AttributeName': 'tasks',
    #     'AttributeType': 'S'
    # },
]
column_provisioned_throughput = {
    'ReadCapacityUnits': 5,
    'WriteCapacityUnits': 5
}
#
create_column_table(column_table, column_key_schema, column_attribute_definitions, column_provisioned_throughput)
create_task_table(table_name, key_schema, attribute_definitions, provisioned_throughput)


def delete_table(table_to_delete):
    table = dynamodb.Table(table_to_delete)
    table.delete()


# delete_table(table_to_delete='columns')


def create_task(task_id, task_name, description, column_id, index):
    print(column_id)
    try:
        table = dynamodb.Table('tasks')

        new_task = {
            'column_id': column_id,
            'task_name': task_name,
            'description': description,
            'task_id': task_id,
            'index': index
        }
        response = table.put_item(
            Item=new_task
        )

        # CHECK IF COLUMN EXISTS
        try:
            column = check_column_exists(column_id)
            if not column:
                new_column = create_new_column(column_id, new_task)
                if not new_column:
                    return jsonify({'success': False, 'message': 'Error creating new Column.'})
                else:
                    print('Task added successfully.')
                    return jsonify({'success': True, 'message': 'Task added Successfully..', 'data': new_task})
        except Exception as e:
            return jsonify({'error': f"Error: {e}"})

        print('here-')
        add_task_to_column = add_task_to_existing_column(column_id, new_task)
        if not add_task_to_column:
            return jsonify({'success': False, 'message': 'Error adding task to column'})
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            print('Task added successfully.')
            return jsonify({'success': True, 'message': 'Task added successfully.', 'data': new_task})
        else:
            print('Failed to add item.')
            return jsonify({'success': False, 'message': 'Error adding Task'})

    except Exception as e:
        print('in exception')
        return jsonify(
            {'success': False, 'message': 'Error Creating and Adding task to column.', 'error': f"Error: {e}"})


def get_task(task_id, column_id):
    try:
        table = dynamodb.Table('tasks')
        response = table.query(
            KeyConditionExpression=Key('task_id').eq(task_id) & Key('column_id').eq(column_id)
        )
        print(response)

        if 'Items' in response and len(response['Items']) > 0:
            return jsonify({'success': True, 'message': 'Task Reterived Successfully', 'data': response['Items']}), 200
        else:
            return jsonify({'success': False, 'message': 'Task not found by this ID'}), 400

    except NoCredentialsError as e:
        return jsonify({'success': False, 'message': 'Internal Server Error', 'error': f"Error: {e}"}), 500


def update_task(task_id, column_id, task_name, description, index):
    try:
        table = dynamodb.Table('tasks')

        response = table.query(
            KeyConditionExpression=Key('task_id').eq(task_id) & Key('column_id').eq(column_id)
        )
        # Check if the task with the given task_id exists
        if 'Items' not in response or not response['Items']:
            return jsonify({'error': 'Error: Task not found with the provided task_id.'}), 400

        response = table.update_item(
            Key={
                'task_id': task_id,
                'column_id': column_id
            },
            UpdateExpression='set task_name = :task_name, description = :description, #index = :index',
            ExpressionAttributeValues={
                ':task_name': task_name,
                ':description': description,
                # ':column_id': column_id,
                ':index': index
            },
            ExpressionAttributeNames={
                '#index': 'index'
            },
            ReturnValues='UPDATED_NEW'
        )
        updated_task = response['Attributes']
        updated_task['column_id'] = column_id
        updated_task['task_id'] = task_id
        # update column in columns table too
        method = 'update'
        update_columns(task_id, column_id, method, updated_task)

        if 'Attributes' in response:
            updated_attributes = response['Attributes']
            return jsonify({'success': True, 'message': 'Task updated successfully', 'data': updated_attributes}), 200
        else:
            return jsonify({'success': False, 'message': 'Task not found by this ID'}), 400

    except Exception as e:
        print(e)
        return jsonify({'success': False, 'message': 'Internal Server Error', 'error': f"Error: {e}"}), 500


def delete_task(task_id, column_id):
    try:
        method = 'delete'  # method is define to differeniate between delete task and update task
        extras = ''
        update_columns(task_id, column_id, method, extras)
        print('now here')
        table = dynamodb.Table('tasks')
        response = table.query(
            KeyConditionExpression=Key('task_id').eq(task_id) & Key('column_id').eq(column_id)
        )
        deleted_item = response['Items']
        if 'Items' in response and len(response['Items']) > 0:
            response = table.delete_item(
                Key={
                    'task_id': task_id,
                    'column_id': column_id
                },
                ConditionExpression=Key('task_id').eq(task_id) & Key('column_id').eq(column_id)
            )
            return jsonify({'success': True, 'message': 'Task deleted successfully', 'data': deleted_item}), 200
        else:
            return jsonify({'success': False, 'message': 'Task Not Found by this Id'}), 400

    except NoCredentialsError as e:
        return jsonify({'success': False, 'message': 'Internal Server Error', 'error': f"Error: {e}"}), 500


def check_column_exists(column_id):
    # Check if the column with the given column_id exists in the columns table
    columns_table = dynamodb.Table('columns')
    response = columns_table.query(
        KeyConditionExpression=Key('column_id').eq(column_id)
    )
    return len(response['Items']) > 0


def add_task_to_existing_column(column_id, task):
    try:
        # Retrieve the column with the given column_id
        columns_table = dynamodb.Table('columns')
        response = columns_table.query(
            KeyConditionExpression=Key('column_id').eq(column_id)
        )

        # Check if the column with the given column_id exists
        if 'Items' not in response or not response['Items']:
            return jsonify({'error': 'Error: Column not found with the provided column_id.'}), 400

        # Extract existing tasks and add the new task
        existing_tasks = response['Items'][0].get('tasks', [])

        if not isinstance(existing_tasks, list):
            # If 'tasks' is not a list, convert it to a list
            existing_tasks = [existing_tasks]

        existing_tasks.append(task)

        print(existing_tasks)
        # Update the column with the new tasks array
        columns_table.update_item(
            Key={'column_id': column_id},
            UpdateExpression='set tasks = :tasks',
            ExpressionAttributeValues={':tasks': existing_tasks},
            ReturnValues="UPDATED_NEW",
        )

        return True

    except ClientError as e:
        print(f'Error adding task to existing column: {e.response["Error"]["Message"]}')
        return False
    except Exception as e:
        print(f'Unexpected error: {e}')
        return False


def create_new_column(column_id, new_task):
    try:
        # Create a new column with the given column_id in the columns table
        columns_table = dynamodb.Table('columns')

        # Serialize the list of tasks into a valid DynamoDB data type
        # serialized_tasks = [task.__dict__ for task in new_task]
        task = [new_task]
        new_column = {
            'column_id': column_id,
            'tasks': task
        }

        print(new_column, new_task)
        columns_table.put_item(Item=new_column)
        print(f'New column created with column_id: {column_id}')

        # Retrieve the newly created column to confirm its existence

        response = columns_table.query(
            KeyConditionExpression=Key('column_id').eq(column_id)
        )
        print(response)

        if 'Items' in response:
            print(f'Column retrieval successful. Column_Id: {column_id}')
            return True
        else:
            print(f'Error: New column not found in the database.')
            return False

    except Exception as e:
        print(f'Error creating a new column: {e}')
        return False


def get_columns():
    try:
        table = dynamodb.Table('columns')
        # response = table.query(
        #     KeyConditionExpression=Key('task_id').eq()
        # )
        response = table.scan()
        print(response)
        response = response.get('Items', [])
        print(response)

        if response or response == []:
            return jsonify({'success': True, 'message': 'Columns Reterived Successfully', 'data': response}), 200
        else:
            print('error')

    except NoCredentialsError as e:
        return jsonify({'success': False, 'message': 'Internal Server Error', 'error': f"Error: {e}"}), 500


def update_columns(task_id, column_id, method, updated_task):
    try:
        print(column_id)
        print('update column')
        table = dynamodb.Table('columns')

        response = table.query(
            KeyConditionExpression=Key('column_id').eq(column_id)
        )

        print(response)
        # Check if the Column with the given column_id exists
        if 'Items' not in response or not response['Items']:
            print("Column Not Found by this Id.")
            return jsonify({'error': 'Error: Column not found with the provided column_id.'}), 400

        if method == 'task_moved':
            print('in tasked moved')
            response = table.update_item(
                Key={
                    'column_id': column_id
                },
                UpdateExpression='set tasks = :tasks',
                ExpressionAttributeValues={
                    ':tasks': updated_task,
                },
                ReturnValues='UPDATED_NEW'
            )

            if 'Attributes' in response:
                updated_attributes = response['Attributes']
                return True
            else:
                return False

        for task in response['Items'][0]['tasks']:
            if task["column_id"] == column_id and task["task_id"] == task_id:
                if method == 'delete':
                    response['Items'][0]['tasks'].remove(task)
                    response = table.update_item(
                        Key={
                            'column_id': column_id
                        },
                        UpdateExpression='set tasks = :tasks',
                        ExpressionAttributeValues={
                            ':tasks': response['Items'][0]['tasks'],
                        },
                        ReturnValues='UPDATED_NEW'
                    )

                    if 'Attributes' in response:
                        updated_attributes = response['Attributes']
                        print(updated_attributes)
                        return True
                    else:
                        return False
            elif method == 'update':
                for index, obj in enumerate(response['Items'][0]['tasks']):
                    if obj.get("task_id") == task_id:
                        response['Items'][0]['tasks'][index] = updated_task
                        response = table.update_item(
                            Key={
                                'column_id': column_id
                            },
                            UpdateExpression='set tasks = :tasks',
                            ExpressionAttributeValues={
                                ':tasks': response['Items'][0]['tasks'],
                            },
                            ReturnValues='UPDATED_NEW'
                        )

                        if 'Attributes' in response:
                            updated_attributes = response['Attributes']
                            return True
                        else:
                            return False




    except Exception as e:
        print(e)
        return False


def move_task_and_update_columns(source_column, destination_column):
    try:
        print(source_column)
        method = 'task_moved'
        if destination_column:
            print('in destinaton')
            destination_column_id = destination_column["columnId"]
            destination_column_updated_task = destination_column["tasks"]
            # CHECK IF COLUMN EXISTS
            try:
                column = check_column_exists(destination_column_id)
                if not column:
                    new_column = create_new_column(destination_column_id, destination_column_updated_task)
                    if not new_column:
                        return jsonify({'success': False, 'message': 'Error creating new Column.'})
            except Exception as e:
                return jsonify({'error': f"Error: {e}"})

            task = None
            update_destination_column = update_columns(task, destination_column_id, method,
                                                       destination_column_updated_task)
            print(update_destination_column)

            # update moved task
            for task in destination_column['tasks']:
                column_id = task["column_id"]
                description = task["description"]
                index = task["index"]
                task_id = task["task_id"]
                task_name = task["task_name"]
                table = dynamodb.Table('tasks')
                response = table.query(
                    KeyConditionExpression=Key('task_id').eq(task_id) & Key('column_id').eq(column_id)
                )
                # Check if the task with the given task_id exists
                if 'Items' not in response or not response['Items']:
                    return jsonify({'error': 'Error: Task not found with the provided task_id.'}), 400

                response = table.update_item(
                    Key={
                        'task_id': task_id,
                        'column_id': column_id
                    },
                    UpdateExpression='set task_name = :task_name, description = :description, #index = :index',
                    ExpressionAttributeValues={
                        ':task_name': task_name,
                        ':description': description,
                        # ':column_id': column_id,
                        ':index': index
                    },
                    ExpressionAttributeNames={
                        '#index': 'index'
                    },
                    ReturnValues='UPDATED_NEW'
                )
                updated_task = response['Attributes']

        print('in source')
        source_column_id = source_column["columnId"]
        source_column_updated_task = source_column["tasks"]
        task = None
        print(source_column_id)
        print(source_column_updated_task)
        update_source_column = update_columns(task, source_column_id, method, source_column_updated_task)

        print(update_source_column)

        # update moved task
        source_column_length = len(source_column['tasks'])
        if source_column_length is not 0:
            for task in source_column['tasks']:
                column_id = task["column_id"]
                description = task["description"]
                index = task["index"]
                task_id = task["task_id"]
                task_name = task["task_name"]
                table = dynamodb.Table('tasks')
                response = table.query(
                    KeyConditionExpression=Key('task_id').eq(task_id) & Key('column_id').eq(column_id)
                )
                # Check if the task with the given task_id exists
                if 'Items' not in response or not response['Items']:
                    print('Task not found with the provided task_id.')
                    return jsonify({'error': 'Error: Task not found with the provided task_id.'}), 400

                response = table.update_item(
                    Key={
                        'task_id': task_id,
                        'column_id': column_id
                    },
                    UpdateExpression='set task_name = :task_name, description = :description, #index = :index',
                    ExpressionAttributeValues={
                        ':task_name': task_name,
                        ':description': description,
                        # ':column_id': column_id,
                        ':index': index
                    },
                    ExpressionAttributeNames={
                        '#index': 'index'
                    },
                    ReturnValues='UPDATED_NEW'
                )
                updated_task = response['Attributes']
                if 'Attributes' in response:
                    return jsonify({'success': True, 'message': 'Task moved Successfully.', 'data': updated_task}), 200
        return jsonify({'success': True, 'message': 'Task moved Successfully.'}), 200


    except Exception as e:
        print(e)
        return jsonify({'success': False, 'message': 'Internal Server Error', 'error': f"Error: {e}"}), 500
