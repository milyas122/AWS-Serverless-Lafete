import base64
import os
import boto3
from datetime import datetime
import src.common.response_builder as response_builder


# create a DynamoDB object using the AWS SDK
# dynamodb = boto3.resource('dynamodb')
# USERS_TABLE = os.environ['USERS_TABLE']
# table = dynamodb.Table(USERS_TABLE)


def lambda_handler(event, context):
    # Id = event['requestContext']['authorizer']['claims']['sub']
    # Id = '48741c61-f055-426f-a466-1c17191713cc'
    # type = event['pathParameters']['type']

    ts = datetime.timestamp(datetime.now())
    ext = ".png"

    file_name = f'{ts}{ext}'
    url = {'url': upload(event["body"], file_name)}
    return response_builder.get_success_response(status_code=200, message='Success', data=url)


def upload(get_file_content, file_name):
    s3 = boto3.client("s3")
    bucket = os.environ['UploadBucket']
    region = os.environ['Aws_region']

    decode_content = base64.b64decode(get_file_content)

    s3_upload = s3.put_object(Bucket=bucket, Key=file_name, Body=decode_content, ContentType='image/png')
    url = f"https://{bucket}.s3.{region}.amazonaws.com/{file_name}"
    return url
