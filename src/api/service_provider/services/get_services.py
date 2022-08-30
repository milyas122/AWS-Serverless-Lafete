import json
import boto3
import os
from botocore.exceptions import ClientError
from src.common import (
    response_builder
)
from boto3.dynamodb.conditions import Key, Attr



cognito_client = boto3.client('cognito-idp') # add region 
dynamodb = boto3.resource('dynamodb')

#Table
SERVICES_TABLE = os.environ["SERVICES_TABLE"]
service_table = dynamodb.Table(SERVICES_TABLE)

def lambda_handler(event, context):
    query_string_params: dict = event["queryStringParameters"]

    service = query_string_params.get("service")
    city = query_string_params.get('city')
    name = query_string_params.get('name')
    
    query_params: dict = dict(
        KeyConditionExpression = Key('Sk').eq(service)
    )

    if city:
        query_params["KeyConditionExpression"] = Key('Sk').eq(service) & Key('city').eq(city)
    
    if name:
        query_params["FilterExpression"] = Attr('name').begins_with(name)


    try:
        response = service_table.query(
            IndexName = "service-city-index",
            **query_params
        )["Items"]

        

        return response_builder.get_success_response(
            status_code=200, 
            message='Success',
            data= response
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