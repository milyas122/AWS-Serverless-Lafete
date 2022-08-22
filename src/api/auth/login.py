import json
import boto3
import os
from botocore.exceptions import ClientError
from ...common.response_builder import get_success_response, get_custom_error

cognito_client = boto3.client('cognito-idp') # add region 
dynamodb = boto3.resource('dynamodb')

#Table
USER_TABLE = os.environ["USERS_TABLE"]
user_table = dynamodb.Table(USER_TABLE)

def lambda_handler(event, context):
    data = json.loads(event["body"])
    try:
        email = data["email"]
        password = data["password"]

        client_id = os.environ["USER_POOL_CLIENT_ID"]

        initate_response = cognito_client.initiate_auth(
            ClientId=client_id,
            AuthFlow= 'USER_PASSWORD_AUTH',
            AuthParameters = {
                'USERNAME': email,
                'PASSWORD': password
            }
        )

        
        result = initate_response["AuthenticationResult"]
        response = dict(
            AccessToken = result["AccessToken"],
            ExpiresIn = result["ExpiresIn"],
            RefreshToken = result["RefreshToken"],
            IdToken = result["IdToken"]
        )
        

        return get_success_response(
            status_code=200, 
            message='Success',
            data={
                "message": "User SignIn Successfully", 
                "data": response}
        )
    except ClientError as e:
        if e.response['Error']['Code'] in ["UserNotFoundException", "NotAuthorizedException"] :
            return get_custom_error(
                status_code=400, 
                message='Bad Request',
                data={
                    "message": e.response['Error']['Message']
                }
            )
        return get_custom_error(
                status_code=400, 
                message='Bad Request',
                data={
                    "message": str(e)
                }
            )
    except ValueError as e:
        return get_custom_error(
            status_code=400, 
            message='Bad Request',
            data={
                "message": str(e)
            }
        )
