import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@Done uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

## ROUTES
'''
@Done implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods = ['GET'])
def get_drinks():
    """
    Public endpoint to get metadata of the available drinks
    :return:
    """
    drinks_dbo = Drink.query.all()
    drinks = [drink_dbo.short() for drink_dbo in drinks_dbo]
    return jsonify({'success': True, 'drinks': drinks}), 200


'''
@Done implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks-detail', methods = ['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    """
    Checkd whether end user has the valid get:drinks-detail permission to access the long description of the drinks
    :param payload: Payload received after jwt decode
    :return:
    """
    drinks_dbo = Drink.query.all()
    drinks = [drink_dbo.long() for drink_dbo in drinks_dbo]
    return jsonify({'success': True, 'drinks': drinks}), 200


'''
@Done implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods = ['POST'])
@requires_auth('post:drinks')
def add_drinks(payload):
    """
    Adds the new drink to the drinks collection
    :return: JSON (success)
    """
    if 'id' in payload:
        del payload['id']
    drink_dbo = Drink(**payload)
    drink_dbo.insert()
    return jsonify({'success': True, 'drinks': [drink_dbo.long()]}), 200


'''
@Done implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<id>', methods = ['PATCH'])
@requires_auth('patch:drinks')
def update_drinks(payload, id):
    """
    Updates the drink based on the given drink id
    :return: JSON (success) / raise exception 404 if id not found
    """
    drink_dbo = Drink.query.filter_by(Drink.id == id).first()
    if drink_dbo is None:
        abort(404, message=f'Cannot find the drink for the given id: {payload["id"]}')
    drink_dbo.title = payload['title']
    drink_dbo.recipe = payload['recipe']
    drink_dbo.update()
    return jsonify({'success': True, 'drinks': [drink_dbo.long()]}), 200

'''
@Done implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<id>', methods = ['DELETE'])
@requires_auth('delete:drinks')
def del_drinks(payload, id):
    """
    Deletes the drink based on the given drink id
    :return: JSON (success) / raise exception 404 if id not found
    """
    drink_dbo = Drink.query.filter_by(Drink.id == id).first()
    if drink_dbo is None:
        abort(404, message=f'Cannot find the drink for the given id: {payload["id"]}. Delete failed.')
    drink_dbo.delete()
    return jsonify({'success': True, 'delete': id}), 200


## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

'''
@Done implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@Done implement error handler for 404
    error handler should conform to general task above 
'''
@app.errorhandler(404)
def cannot_access_resource(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': str(error)
    }), 404


'''
@Done implement error handler for AuthError
    error handler should conform to general task above 
'''
@app.errorhandler(AuthError)
def send_auth_error(error):
    return jsonify({
        'success': False,
        'error': error.status_code,
        'message': f'Reason: {error.error["code"]}. {error.error["description"]}'
    }), error.status_code
