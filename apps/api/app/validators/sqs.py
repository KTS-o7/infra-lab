from app.aws_client import get_sqs_client

def sqs_queue_exists(queue_name: str) -> dict:
    client = get_sqs_client()
    try:
        client.get_queue_url(QueueName=queue_name)
        return {"id": "queue-exists", "type": "sqs_queue_exists", "passed": True, "message": f"Queue {queue_name} exists."}
    except Exception as e:
        return {"id": "queue-exists", "type": "sqs_queue_exists", "passed": False, "message": f"Queue {queue_name} was not found."}

def sqs_message_available(queue_name: str, body: str) -> dict:
    client = get_sqs_client()
    try:
        queue_url = client.get_queue_url(QueueName=queue_name)["QueueUrl"]
        response = client.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=10, WaitTimeSeconds=1, VisibilityTimeout=0)
        messages = response.get("Messages", [])
        for msg in messages:
            if msg["Body"] == body:
                return {"id": "message-available", "type": "sqs_message_available", "passed": True, "message": f"Queue {queue_name} contains the expected message."}
        return {"id": "message-available", "type": "sqs_message_available", "passed": False, "message": f"Queue {queue_name} does not contain the expected message."}
    except Exception as e:
        return {"id": "message-available", "type": "sqs_message_available", "passed": False, "message": f"Queue {queue_name} does not contain the expected message."}