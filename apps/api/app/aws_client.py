import boto3
from botocore.config import Config
import app.config as config

_boto_config = Config(
    region_name=config.AWS_DEFAULT_REGION,
    signature_version='v4',
    retries={'max_attempts': 3, 'mode': 'standard'},
)

def get_client(service: str):
    return boto3.client(
        service,
        endpoint_url=config.AWS_ENDPOINT_URL,
        aws_access_key_id=config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
        region_name=config.AWS_DEFAULT_REGION,
        config=_boto_config,
    )

def get_s3_client():
    return get_client("s3")

def get_sqs_client():
    return get_client("sqs")

def get_dynamodb_client():
    return get_client("dynamodb")

def get_lambda_client():
    return get_client("lambda")

def get_sns_client():
    return get_client("sns")

def get_apigateway_client():
    return get_client("apigatewayv2")