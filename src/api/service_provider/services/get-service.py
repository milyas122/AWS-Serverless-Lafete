# import json
import boto3
import os
from botocore.exceptions import ClientError
from src.common import (
    response_builder
)
from boto3.dynamodb.conditions import Key



cognito_client = boto3.client('cognito-idp') # add region 
dynamodb = boto3.resource('dynamodb')

#Table
SERVICES_TABLE = os.environ["SERVICES_TABLE"]
service_table = dynamodb.Table(SERVICES_TABLE)

def lambda_handler(event, context):
    service_id = event["pathParameters"]["service_id"]

    try:
        
        response = service_table.query(
            KeyConditionExpression = Key("Pk").eq(service_id)
        )["Items"]
        
        if not response:
            return response_builder.get_custom_error(
                status_code=400, 
                message='Bad Request',
                data={
                    "message": "Invalid Service Id"
                }
            )
        

        return response_builder.get_success_response(
            status_code=200, 
            message='Success',
            data= {
                "data": response[0]
            }
        )
    except ClientError as e:
        return response_builder.get_custom_error(
            status_code=500, 
            message='Error',
            data={
                "message": e.response['Error']['Message']
            }
        )

# {
#     "name":"Noor Catering service",
#     "about_service":"54e79bc2-600d-4dff-aafd-c4f8dcf4f260",
#     "location":"Lahore",
#     "state":"Lahore",
#     "city":"Punjba",
#     "services":[
#     {
#         "service":"Live Barbq",
#         "about_service":"ilajs",
#         "images":[
#             "https://www.google.com/"
#             ]
#     }    
#     ]
# }