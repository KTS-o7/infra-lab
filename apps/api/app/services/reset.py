from app.aws_client import (
    get_apigateway_client,
    get_dynamodb_client,
    get_lambda_client,
    get_s3_client,
    get_sns_client,
    get_sqs_client,
)


def _resource_id(resource: dict) -> str:
    res_type = resource.get("type")
    if res_type == "s3_object":
        return f"{resource.get('bucket')}/{resource.get('key')}"
    if res_type == "s3_bucket":
        return resource.get("bucket", "")
    if res_type == "sqs_queue":
        return resource.get("queue_name", "")
    if res_type == "dynamodb_table":
        return resource.get("table_name", "")
    if res_type == "lambda_function":
        return resource.get("function_name", "")
    if res_type == "sns_topic":
        return resource.get("topic_name", "")
    if res_type == "apigateway_api":
        return resource.get("api_name", "")
    return ""


def _deleted(resource: dict) -> dict:
    return {"type": resource.get("type"), "id": _resource_id(resource), "status": "deleted"}


def _failed(resource: dict, exc: Exception) -> dict:
    return {
        "type": resource.get("type"),
        "id": _resource_id(resource),
        "status": "error",
        "message": str(exc) or "Resource deletion failed",
    }


def reset_owned_resources(owned_resources: list) -> dict:
    deleted = []
    failed = []
    s3_objects = []
    s3_buckets = []

    for resource in owned_resources:
        res_type = resource.get("type")
        if res_type == "s3_object":
            s3_objects.append(resource)
        elif res_type == "s3_bucket":
            s3_buckets.append(resource)
        elif res_type == "sqs_queue":
            try:
                client = get_sqs_client()
                url = client.get_queue_url(QueueName=resource["queue_name"])["QueueUrl"]
                client.delete_queue(QueueUrl=url)
                deleted.append(_deleted(resource))
            except Exception as exc:  # noqa: BLE001
                failed.append(_failed(resource, exc))
        elif res_type == "dynamodb_table":
            try:
                get_dynamodb_client().delete_table(TableName=resource["table_name"])
                deleted.append(_deleted(resource))
            except Exception as exc:  # noqa: BLE001
                failed.append(_failed(resource, exc))
        elif res_type == "lambda_function":
            try:
                get_lambda_client().delete_function(FunctionName=resource["function_name"])
                deleted.append(_deleted(resource))
            except Exception as exc:  # noqa: BLE001
                failed.append(_failed(resource, exc))
        elif res_type == "sns_topic":
            try:
                get_sns_client().delete_topic(TopicArn=f"arn:aws:sns:us-east-1:000000000000:{resource['topic_name']}")
                deleted.append(_deleted(resource))
            except Exception as exc:  # noqa: BLE001
                failed.append(_failed(resource, exc))
        elif res_type == "apigateway_api":
            try:
                client = get_apigateway_client()
                apis = client.get_apis()
                for api in apis.get("Items", []):
                    if api.get("Name") == resource["api_name"]:
                        client.delete_api(ApiId=api["ApiId"])
                        deleted.append(_deleted(resource))
                        break
            except Exception as exc:  # noqa: BLE001
                failed.append(_failed(resource, exc))

    for resource in s3_objects:
        try:
            get_s3_client().delete_object(Bucket=resource["bucket"], Key=resource["key"])
            deleted.append(_deleted(resource))
        except Exception as exc:  # noqa: BLE001
            failed.append(_failed(resource, exc))

    for resource in s3_buckets:
        try:
            get_s3_client().delete_bucket(Bucket=resource["bucket"])
            deleted.append(_deleted(resource))
        except Exception as exc:  # noqa: BLE001
            failed.append(_failed(resource, exc))

    return {"deleted": deleted, "failed": failed, "skipped": []}
