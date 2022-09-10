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
    try:
        data = json.loads(event["body"])
        
        additon_type = event["pathParameters"]["addition"]
        service_id = event["pathParameters"]["service_id"]
        
        if additon_type.lower() == "menu":
            menus = data.get("menus")
            if not menus:
                raise ValidationError(" Menus is required fields")
        elif additon_type.lower() == "add_on":
            add_ons = data.get("add_ons")
            if not add_ons:
                raise ValidationError("Add_ons is required fields")
        else:
            raise ValidationError("Addition Type either be menu or add_on")

        
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
        
        
        available_menus = service["menus"]
        available_add_ons = service["add_ons"]
        
        
        
        addable_menu = []
        addable_add_ons = []
        add_on_found = menu_found = False
        
        if additon_type.lower() == "menu":
            if available_menus:
                for index, menu in enumerate(menus):
                    for record in available_menus:
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
     
        else:
            if available_add_ons:
                for index, add_on in enumerate(add_ons):
                    for record in available_add_ons:
                        if record.get("id"):
                            record.pop("id")
                        if add_on["add_on"] != record["add_on"]: # make it idempotent
                            add_on["id"] = str(uuid.uuid4())
                            addable_add_ons.append(add_on)
                            add_on_found = True
            else:
                add_on_found = True
                for index, add_on in enumerate(add_ons):
                    add_ons[index]["id"] = str(uuid.uuid4())
                addable_add_ons = add_ons
        
        
        
        query_params = {
            "menu": {
                "UpdateExpression": "SET menus = list_append(menus, :v1)",
                "ExpressionAttributeValues" : {
                    ":v1": addable_menu, # By default menus is list
                }
            },
            "add_ons": {
                "UpdateExpression" : "SET add_ons = list_append(add_ons, :v2)",
                "ExpressionAttributeValues": {
                    ":v2": addable_add_ons # By default add_ons is list
                }
            }
        }
           
        service_table.update_item(
            Key = {
                "Pk": service_id,
                "Sk": sk
            },
            **query_params[additon_type.lower()]
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
    

# def get_menu(menus: list) -> tuple:
#     for record in enumerate(menus):
#         yield record

# def get_add_ons(add_ons: list) -> tuple:
#     for record in add_ons:
#         yield record 

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