from . import api
from flask import jsonify
from app.exceptions import ValidationError

def forbidden(message):
    resp = jsonify({'error': 'forbidden', 'message': message})
    resp.status_code = 403
    return resp
    
def unauhtorized(message):
    resp = jsonify({'error': 'unauthorized', 'message': message})
    resp.status_code = 401
    return resp
    
def bad_request(message).
    resp = jsonify({'error': 'bad request', 'message': message})
    resp.status_code = 400
    return resp
    
@api.errorhandler(ValidationError)
def validation_error(e):
    return bad_request(e.args[0])