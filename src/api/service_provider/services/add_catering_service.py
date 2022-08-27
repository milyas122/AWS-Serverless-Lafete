import json
import boto3
import os

from botocore.exceptions import ClientError
from src.common import (
    response_builder, decorators
)
from boto3.dynamodb.conditions import Key
from src.validation.services import CateringService
from marshmallow import ValidationError


cognito_client = boto3.client('cognito-idp') # add region 
dynamodb = boto3.resource('dynamodb')

#Table
SERVICES_TABLE = os.environ["SERVICES_TABLE"]
service_table = dynamodb.Table(SERVICES_TABLE)

@decorators.validate_body(Schema=CateringService())
def lambda_handler(event, context):
    data = json.loads(event["body"])

    try:
        # data = MenuSchema().load(data)
        
        service_id = event["pathParameters"]["service_id"]
        
        data: dict = CateringService().load(data)

        service_result = service_table.query(
            KeyConditionExpression = Key("Pk").eq(service_id),
            ProjectionExpression = "Sk, services"
        )["Items"]

        if not any(service_result):
            raise ValueError("Service id is invalid1")
        
        catering_service = service_result[0]
        sk = catering_service["Sk"] # Sort Key

        if sk != "Catering":
            raise ValueError("Catering services only add against Catering")
        
        
        available_services = catering_service["services"]
        
        # Check whether catering service already exist or not ?
        for service in available_services:
            if service["service"].lower() == data["service"].lower():
                # We Make api Idempotent
                return response_builder.get_success_response(
                    status_code=200, 
                    message='Success',
                    data={
                        "message": "Catering Serivce added successfully"
                    }
                )
         
        service_table.update_item(
            Key = {
                "Pk": service_id,
                "Sk": sk
            }, 
            UpdateExpression = "SET services = list_append(services, :v1)",
                ExpressionAttributeValues = {
                    ":v1": [data], 
                }
        )
        
        return response_builder.get_success_response(
            status_code=200, 
            message='Success',
            data={
                "message": "Catering Serivce added successfully"
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
    except ValueError as e:
        return response_builder.get_custom_error(
            status_code=400, 
            message='Bad Request',
            data={
                "message": str(e)
            }
        )
    except ValidationError as e:
        return response_builder.CustomValidationErrors(e).get_error()
#  {
#         "service":"Live Barb",
#         "about_service":"ilajs",
#         "images":[
#             "https://www.google.com/"]
# }