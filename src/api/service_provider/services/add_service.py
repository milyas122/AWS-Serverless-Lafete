import json
import boto3
import os
from botocore.exceptions import ClientError
from src.common import (
    response_builder, utils, decorators
)
import uuid
from src.validation.services import (
    HallSchema, MarqueeSchema, FarmHouseSchema,
    EventOrganizer, CateringSchema, ServicesSchema
)

from marshmallow import ValidationError


cognito_client = boto3.client('cognito-idp') # add region 
dynamodb = boto3.resource('dynamodb')

#Table
SERVICES_TABLE = os.environ["SERVICES_TABLE"]
service_table = dynamodb.Table(SERVICES_TABLE)

@decorators.validate_body(Schema=ServicesSchema())
def lambda_handler(event, context):
    data = json.loads(event["body"])

    try:
        service_type = data['service']

        # Data Validation
        if service_type == "Hall":
            data = HallSchema().load(data)
            data["menus"] = []
            data["add_ons"] = []

        elif service_type == "Marquee":
            data = MarqueeSchema().load(data)
            data["menus"] = []
            data["add_ons"] = []

        elif service_type == "Event Organizer":
            data = EventOrganizer().load(data)

        elif service_type == "Catering":
            data = CateringSchema().load(data)   

        elif service_type == "Farm House":
            data = FarmHouseSchema().load(data)
        

        service_provider_id = event["requestContext"]["authorizer"]['claims']['sub']
        # service_provider_id = "dc42638f-8a88-44a2-b124-96666ddbe6b2"
        
        data.pop("service") # Avoid data duplication
        
        service_table.put_item(
            Item = {
                "Pk": str(uuid.uuid4()),
                "Sk": service_type,
                "service_provider": str(service_provider_id),
                "created_at": utils.get_timeStamp(),
                **data
            }
        )

        return response_builder.get_success_response(
            status_code=200, 
            message='Success',
            data={
                "message": "Serivce added successfully"
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