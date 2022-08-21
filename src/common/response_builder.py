import json



response_headers = {
    # 'Content-Type': 'application/json',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Origin': '*',  # Required for CORS support to work
    'Access-Control-Allow-Credentials': True,  # Required for cookies, authorization headers with HTTPS
    'Access-Control-Allow-Methods': 'GET,POST,PATCH,DELETE,OPTIONS, *'
}

def get_success_response(status_code=200, message='Success', data=None):
    return {
        'statusCode': status_code,
        'headers': response_headers,
        'body': json.dumps({
            'responseCode': status_code,
            'message': message,
            'response': data
        }, indent=2)
    }


def get_custom_error(status_code=400, message='Error', data=None):
    return {
        'statusCode': status_code,
        'headers': response_headers,
        'body': json.dumps({
            'responseCode': status_code,
            'message': message,
            'response': data
        }, indent=2)
    }



class CustomValidationErrors:

    def __init__(self, data) -> None:
        self.data = data

    def extract_value(self):
        for value in self.data.values():
            return value

    def get_error(self):
        self.data = self.data.normalized_messages()
        while isinstance(self.data, dict):
            self.data = self.extract_value()
        return get_custom_error(status_code=400, message='Validation Error',
                                data={"message": self.data[0]})