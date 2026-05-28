from app.validators.runtime import runtime_floci_available
from app.validators.s3 import s3_bucket_exists, s3_object_exists, s3_object_body_equals
from app.validators.sqs import sqs_queue_exists, sqs_message_available
from app.validators.dynamodb import dynamodb_table_exists, dynamodb_key_schema_equals, dynamodb_item_exists, dynamodb_item_attribute_equals
from app.validators.lambda_ import lambda_function_exists, lambda_invoke_returns
from app.validators.sns import sns_topic_exists, sns_subscription_exists, sns_to_sqs_delivery
from app.validators.apigateway import apigateway_api_exists, apigateway_route_exists, apigateway_http_returns
from app.validators.workflow import workflow_http_sends_sqs, workflow_http_writes_dynamodb

CHECK_REGISTRY = {
    "s3_bucket_exists": s3_bucket_exists,
    "s3_object_exists": s3_object_exists,
    "s3_object_body_equals": s3_object_body_equals,
    "sqs_queue_exists": sqs_queue_exists,
    "sqs_message_available": sqs_message_available,
    "dynamodb_table_exists": dynamodb_table_exists,
    "dynamodb_key_schema_equals": dynamodb_key_schema_equals,
    "dynamodb_item_exists": dynamodb_item_exists,
    "dynamodb_item_attribute_equals": dynamodb_item_attribute_equals,
    "lambda_function_exists": lambda_function_exists,
    "lambda_invoke_returns": lambda_invoke_returns,
    "runtime_floci_available": runtime_floci_available,
    "sns_topic_exists": sns_topic_exists,
    "sns_subscription_exists": sns_subscription_exists,
    "sns_to_sqs_delivery": sns_to_sqs_delivery,
    "apigateway_api_exists": apigateway_api_exists,
    "apigateway_route_exists": apigateway_route_exists,
    "apigateway_http_returns": apigateway_http_returns,
    "workflow_http_writes_dynamodb": workflow_http_writes_dynamodb,
    "workflow_http_sends_sqs": workflow_http_sends_sqs,
}

def run_check(check_spec: dict) -> dict:
    check_type = check_spec.get("type", "")
    validator = CHECK_REGISTRY.get(check_type)
    if not validator:
        return {
            "id": check_spec.get("id", "unknown"),
            "type": check_type,
            "passed": False,
            "message": f"Unknown check type: {check_type}",
        }
    try:
        params = {k: v for k, v in check_spec.items() if k not in ("id", "type") and v is not None}
        return validator(**params)
    except Exception as e:
        return {
            "id": check_spec.get("id", "unknown"),
            "type": check_type,
            "passed": False,
            "message": f"Validation error: {str(e)}",
        }
