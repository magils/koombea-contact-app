from flask import jsonify
from werkzeug.exceptions import HTTPException


class APIError(Exception):
    
    def __init__(self, error_message, status_code=400):
        self.status_code = status_code
        self.error_message = error_message

def handler_api_errors(error):
    payload = {
        "message": error.error_message
    }
    return jsonify(payload), error.status_code