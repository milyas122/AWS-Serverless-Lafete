import json
import boto3
import os
from botocore.exceptions import ClientError
from src.common import (
    response_builder, utils
)
import uuid
from src.validation.services import (
    HallSchema, MorqueeSchema, FarmHouseSchema,
    EventOrganizer, CateringSchema
)
from marshmallow import ValidationError


cognito_client = boto3.client('cognito-idp') # add region 
dynamodb = boto3.resource('dynamodb')

#Table
SERVICES_TABLE = os.environ["SERVICES_TABLE"]
service_table = dynamodb.Table(SERVICES_TABLE)

def lambda_handler(event, context):
    data = json.loads(event["body"])


    try:
        service_id = event["pathParameters"]["service_id"] 

        service_type = data['service']

        # Data Validation
        if service_type == "Hall":
            data = HallSchema().load(data)
            UpdateExpression = '''SET about_service = :v1, afternoon_slot = :v2, evening_slot = :v3, city = :v4, images = :v5, 
                                    #l = :v6, max_seating = :v7, #n = :v8, per_head = :v9, #st = :v10, updated_at = :v11'''
            ExpressionAttributeValues = {
                ":v1": data["about_service"],
                ":v2": data["afternoon_slot"],
                ":v3": data["evening_slot"],
                ":v4": data["city"],
                ":v5": data["images"],
                ":v6": data["location"],
                ":v7": data["max_seating"],
                ":v8": data["name"],
                ":v9": data["per_head"],
                ":v10": data["state"],
                ":v11": utils.get_timeStamp()
            }

        elif service_type == "Morquee":
            data = MorqueeSchema().load(data)
            UpdateExpression = '''SET about_service = :v1, afternoon_slot = :v2, evening_slot = :v3, city = :v4, images = :v5, 
                                    #l = :v6, max_seating = :v7, #n = :v8, per_head = :v9, #st = :v10, updated_at = :v11, decores = :v12'''
            ExpressionAttributeValues = {
                ":v1": data["about_service"],
                ":v2": data["afternoon_slot"],
                ":v3": data["evening_slot"],
                ":v4": data["city"],
                ":v5": data["images"],
                ":v6": data["location"],
                ":v7": data["max_seating"],
                ":v8": data["name"],
                ":v9": data["per_head"],
                ":v10": data["state"],
                ":v11": utils.get_timeStamp(),
                ":v12": data["decores"]
            }

        elif service_type == "Farm House":
            data = FarmHouseSchema().load(data)
            UpdateExpression = '''SET about_service = :v1, city = :v4, images = :v5, 
                                    #l = :v6, #n = :v8, #st = :v10, updated_at = :v11, area = :v12, per_hour_rate = :v13'''
            ExpressionAttributeValues = {
                ":v1": data["about_service"],
                ":v4": data["city"],
                ":v5": data["images"],
                ":v6": data["location"],
                ":v8": data["name"],
                ":v10": data["state"],
                ":v11": utils.get_timeStamp(),
                ":v12": data["area"],
                ":v13": data["per_hour_rate"]

            }

        elif service_type == "Event Organizer":
            data = EventOrganizer().load(data)
            UpdateExpression = '''SET about_service = :v1, city = :v4, #l = :v6, #n = :v8, #st = :v10, 
                                    updated_at = :v11, portfolio = :v12'''
            ExpressionAttributeValues = {
                ":v1": data["about_service"],
                ":v4": data["city"],
                ":v6": data["location"],
                ":v8": data["name"],
                ":v10": data["state"],
                ":v11": utils.get_timeStamp(),
                ":v12": data["portfolio"]

            }

        elif service_type == "Catering":
            CateringSchema().load(data)   
            UpdateExpression = '''SET about_service = :v1, city = :v4, #l = :v6, #n = :v8, #st = :v10, 
                                updated_at = :v11, services = :v12'''
            ExpressionAttributeValues = {
                ":v1": data["about_service"],
                ":v4": data["city"],
                ":v6": data["location"],
                ":v8": data["name"],
                ":v10": data["state"],
                ":v11": utils.get_timeStamp(),
                ":v12": data["services"]

            }
        
        data.pop("service") # Avoid data duplication
        
        service_table.update_item(
            Key = {
                "Pk": str(service_id),
                "Sk": service_type
            },
            UpdateExpression = UpdateExpression,
            ExpressionAttributeValues = ExpressionAttributeValues,
            ExpressionAttributeNames = {
                "#n": "name",
                "#l": "location",
                "#st": "state"
            }
        )

        return response_builder.get_success_response(
            status_code=200, 
            message='Success',
            data={
                "message": "Serivce updated successfully"
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
    except ValidationError as e:
        return response_builder.CustomValidationErrors(e).get_error()

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