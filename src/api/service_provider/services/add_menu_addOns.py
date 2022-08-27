import uuid
import json
import boto3
import os

from botocore.exceptions import ClientError
from src.common import (
    response_builder, decorators
)
from boto3.dynamodb.conditions import Key
from src.validation.menu import MenuSchema
from marshmallow import ValidationError


cognito_client = boto3.client('cognito-idp') # add region 
dynamodb = boto3.resource('dynamodb')

#Table
SERVICES_TABLE = os.environ["SERVICES_TABLE"]
service_table = dynamodb.Table(SERVICES_TABLE)

@decorators.validate_body(Schema=MenuSchema())
def lambda_handler(event, context):
    data = json.loads(event["body"])

    try:
        # data = MenuSchema().load(data)
        
        service_id = event["pathParameters"]["service_id"]
        menus = data["menus"]
        add_ons = data["add_ons"]
        
        service_result = service_table.query(
            KeyConditionExpression = Key("Pk").eq(service_id),
            ProjectionExpression = "Sk, menus, add_ons"
        )["Items"]

        if not any(service_result):
            raise ValueError("Service id is invalid")
        
        service = service_result[0]
        sk = service["Sk"] # Sort Key

        if sk not in ["Hall", "Morquee"]:
            raise ValueError("Menue/AddOns Only add against Hall/Morquee")
        
        
        avalable_menus = service["menus"]
        avalable_add_ons = service["add_ons"]
        
        
        
        addable_menu = []
        addable_add_ons = []
        add_on_found = menu_found = False
        
        if avalable_menus:
            for index, menu in enumerate(menus):
                for record in avalable_menus:
                    if record.get("id"):
                        record.pop("id")
                    if menu != record: # make it idempotent
                        menu["id"] = str(uuid.uuid4())
                        addable_menu.append(menu)
                        menu_found = True
        else:
            menu_found = True
            for index, menu in enumerate(menus):
                menus[index]["id"] = str(uuid.uuid4())
            addable_menu = menus
     
        
        
        if avalable_add_ons:
            for index, add_on in enumerate(add_ons):
                for record in avalable_add_ons:
                    if record.get("id"):
                        record.pop("id")
                    if add_on["add_on"] != record["add_on"]: # make it idempotent
                        add_on["id"] = str(uuid.uuid4())
                        addable_add_ons.append(add_on)
                        add_on_found = True
        else:
            add_on_found = True
            for index, add_on in enumerate(add_ons):
                add_on[index]["id"] = str(uuid.uuid4())
            addable_add_ons = add_ons
        
        # Make API Idempotent
        if add_on_found and menu_found:
            query_params = dict(
                UpdateExpression = "SET menus = list_append(menus, :v1), add_ons = list_append(add_ons, :v2)",
                ExpressionAttributeValues = {
                    ":v1": addable_menu, # By default menus is list
                    ":v2": addable_add_ons # By default add_ons is list
                }
            )
        elif add_on_found:
            query_params = dict(
                UpdateExpression = "SET add_ons = list_append(add_ons, :v2)",
                ExpressionAttributeValues = {
                    ":v2": addable_add_ons # By default add_ons is list
                }
            )
        elif menu_found:
            query_params = dict(
                UpdateExpression = "SET menus = list_append(menus, :v1)",
                ExpressionAttributeValues = {
                    ":v1": addable_menu, # By default menus is list
                }
            )
        else: # make it idempotent 
            return response_builder.get_success_response(
                status_code=200, 
                message='Success',
                data={
                    "message": "Serivce added successfully"
                }
            )
         
        service_table.update_item(
            Key = {
                "Pk": service_id,
                "Sk": sk
            },
            **query_params
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
#     "menus": [
#         {
#    "bread": "Nan",
#    "curry": "Qorma",
#    "desserts": "Gajjar Halwa",
#    "per_head": 100,
#    "rice": "Biryani",
#    "salad": "Russian",
#    "yogurt": "Raita"
#   }
#     ],
#     "add_ons": [
#         {
#             "add_on":"drink",
#             "per_head":100
#         },
#         {
#             "add_on":"frink",
#             "per_head":100
#         }
#     ]
# }