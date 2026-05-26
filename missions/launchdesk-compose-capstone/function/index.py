import json
import os

import boto3


ENDPOINT_URL = os.environ.get("AWS_ENDPOINT_URL", "http://floci:4566")
REGION = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")


def handler(event, context):
    body = event.get("body", event)
    if isinstance(body, str):
        body = json.loads(body or "{}")

    order_id = body["orderId"]
    item = body.get("item", "unknown")
    pk = f"order#{order_id}"

    dynamodb = boto3.client("dynamodb", endpoint_url=ENDPOINT_URL, region_name=REGION)
    sqs = boto3.client("sqs", endpoint_url=ENDPOINT_URL, region_name=REGION)

    dynamodb.put_item(
        TableName="orders-table",
        Item={
            "pk": {"S": pk},
            "orderId": {"S": order_id},
            "item": {"S": item},
            "processed": {"BOOL": True},
        },
    )
    queue_url = sqs.get_queue_url(QueueName="orders-queue")["QueueUrl"]
    sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps({"event": "order.created", "orderId": order_id, "item": item}),
    )

    return {
        "statusCode": 200,
        "headers": {"content-type": "application/json"},
        "body": json.dumps({"orderId": order_id, "item": item, "processed": True}),
    }
