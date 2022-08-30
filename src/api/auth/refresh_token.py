import boto3
import json
import os 

from botocore.exceptions import ClientError
from src.common import (
    response_builder
)

cognito_client = boto3.client('cognito-idp') # add region 


def lambda_handler(event,context):
    refresh_token = json.loads(event["body"])["token"]

    try:
        client_id = os.environ["USER_POOL_CLIENT_ID"]

        initate_response = cognito_client.initiate_auth(
            ClientId=client_id,
            AuthFlow= 'REFRESH_TOKEN_AUTH',
            AuthParameters = {
                'REFRESH_TOKEN': refresh_token
            }
        )
        result = initate_response["AuthenticationResult"]
        
        response = dict(
            AccessToken = result["AccessToken"],
            ExpiresIn = result["ExpiresIn"],
            RefreshToken = refresh_token,
            IdToken = result["IdToken"]
        )
        return response_builder.get_success_response(
                status_code=200, 
                message='Success',
                data= {"data":response}
            )
    except ClientError as e:
        return response_builder.get_custom_error(
            status_code=500, 
            message='Error',
            data={
                "message": e.response['Error']['Message']
            }
        )
