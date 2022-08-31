import json
import boto3
import os
from botocore.exceptions import ClientError
from ...common.response_builder import get_success_response, get_custom_error
from ...common import utils
from ...common.decorators import (
    validate_body
)
from ...validation.complete_profile import CompleteProfileSchema



cognito_client = boto3.client('cognito-idp') # add region 
dynamodb = boto3.resource('dynamodb')

#Table
USER_TABLE = os.environ["USERS_TABLE"]
user_table = dynamodb.Table(USER_TABLE)

@validate_body(Schema=CompleteProfileSchema())
def lambda_handler(event, context):
    data = json.loads(event["body"])

    try:
        uuid = event["requestContext"]["authorizer"]['claims']['sub']
        email = event["requestContext"]["authorizer"]['claims']['email']
        is_profile_completed = event["requestContext"]["authorizer"]['claims']['custom:is_profile_completed']
        

        if is_profile_completed == "True":
            return get_success_response(
                status_code=400, 
                message='Bad Request',
                data={
                    "message": "Profile already completed "
                }
            )
        
        # uuid = "54e79bc2-600d-4dff-aafd-c4f8dcf4f260"
        # email = "ammer@gmail.com"
        
        business_name = data["business_name"]
        phone_no = data["phone_no"]
        landline_no = data.get("landline_no")

        pool_id = os.environ["USER_POOL_ID"]
        service_provider_group = os.environ["SERVICE_PROVIDER_GROUP"]
        user_group = os.environ["USER_POOL_GROUP"]

        cognito_client.admin_update_user_attributes(
            UserPoolId = pool_id,
            Username = email,
            UserAttributes = [
                {
                    'Name': 'custom:is_profile_completed',
                    'Value': 'True'
                }
            ]
        )

        cognito_client.admin_remove_user_from_group(
            UserPoolId = pool_id,
            Username = email,
            GroupName = user_group
        )
        
        # Add user to service provider group
        cognito_client.admin_add_user_to_group(
            UserPoolId = pool_id,
            Username = email,
            GroupName = service_provider_group
        )
        updated_at = utils.get_timeStamp()
        user_object = user_table.delete_item(
            Key = {
                "Pk": str(uuid),
                "Sk": "Profile#User"
            },
            ReturnValues = 'ALL_OLD'
        )["Attributes"]

        put_query = {
                "Pk": str(uuid),
                "Sk": "Profile#ServiceProvider",
                "created_at": user_object["created_at"],
                "updated_at": updated_at,
                "name": user_object["name"],
                "business_name": business_name,
                "phone_no": phone_no
        }

        if landline_no:
            put_query["landline_no"] = landline_no
        
        user_table.put_item(
            Item = {
                **put_query
            }
        )

        return get_success_response(
            status_code=200, 
            message='Success',
            data={
                "message": "Profile Completed Successfully"
            }
        )
    except ClientError as e:
        return get_custom_error(
            status_code=500, 
            message='Error',
            data={
                "message": e.response['Error']['Message']
            }
        )
    