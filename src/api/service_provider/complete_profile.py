import json
import boto3
import os
from botocore.exceptions import ClientError
from ...common.response_builder import get_success_response, get_custom_error
from ...common import utils


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
        confirm_password = data["confirm_password"]
        name = data["name"]

        if password != confirm_password:
            raise ValueError("Password not matched enter again")

        client_id = os.environ["USER_POOL_CLIENT_ID"]
        pool_id = os.environ["USER_POOL_ID"]
        user_pool_group = os.environ["USER_POOL_GROUP"]

        uuid = cognito_client.sign_up(
            ClientId = client_id,
            Username = email,
            Password = password,
        )["UserSub"]

        # Use Admin powers to confirm new user
        cognito_client.admin_confirm_sign_up(
            UserPoolId = pool_id,
            Username = email
        )

        cognito_client.admin_add_user_to_group(
            UserPoolId = pool_id,
            Username = email,
            GroupName = user_pool_group
        )

        cognito_client.admin_update_user_attributes(
            UserPoolId = pool_id,
            Username = email,
            UserAttributes = [
                {
                    'Name': 'custom:is_profile_completed',
                    'Value': 'False'
                }
            ]
        )
        current_date_time = utils.get_timeStamp()
        
        user_table.put_item(
            Item = {
                "Pk": str(uuid),
                "Sk": "Profile#User",
                "created_at": current_date_time,
                "name": name
            }
        )

        return get_success_response(
            status_code=200, 
            message='Success',
            data={
                "message": "User Signup Successfully", 
                "data": {"Id": uuid}}
        )
    except ClientError as e:
        return get_custom_error(
            status_code=500, 
            message='Error',
            data={
                "message": e.response['Error']['Message']
            }
        )
    except ValueError as e:
        return get_custom_error(
            status_code=400, 
            message='Bad Request',
            data={
                "message": e
            }
        )
