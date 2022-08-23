from .response_builder import (
    CustomValidationErrors, get_custom_error
)
from marshmallow import ValidationError
from functools import wraps
import json


def validate_body(Schema):
    @wraps(Schema)
    def decorator(func):
        def wrapper(event,context):
            try:
                if 'body' in event and event['body'] is not None:
                    data = json.loads(event['body'])
                else:
                    return get_custom_error(status_code=400, message="Bad Request", data={'message':"Porvide data in body"})
                
                Schema.load(data)
                return func(event,context)
            
            except ValidationError as error:
                return CustomValidationErrors(error).get_error()
        return wrapper
    return decorator