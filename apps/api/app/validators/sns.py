from app.aws_client import get_sns_client, get_sqs_client

def sns_topic_exists(topic_name: str) -> dict:
    client = get_sns_client()
    try:
        client.get_topic_attributes(TopicArn=f"arn:aws:sns:us-east-1:000000000000:{topic_name}")
        return {"id": "topic-exists", "type": "sns_topic_exists", "passed": True, "message": f"Topic {topic_name} exists."}
    except Exception as e:
        return {"id": "topic-exists", "type": "sns_topic_exists", "passed": False, "message": f"Topic {topic_name} was not found."}

def sns_subscription_exists(topic_name: str, queue_name: str) -> dict:
    sns_client = get_sns_client()
    sqs_client = get_sqs_client()
    try:
        topic_arn = f"arn:aws:sns:us-east-1:000000000000:{topic_name}"
        subscriptions = sns_client.list_subscriptions_by_topic(TopicArn=topic_arn)
        for sub in subscriptions.get("Subscriptions", []):
            if queue_name in sub.get("Endpoint", ""):
                return {"id": "subscription-exists", "type": "sns_subscription_exists", "passed": True, "message": f"Subscription from {topic_name} to {queue_name} exists."}
        return {"id": "subscription-exists", "type": "sns_subscription_exists", "passed": False, "message": f"Subscription from {topic_name} to {queue_name} was not found."}
    except Exception as e:
        return {"id": "subscription-exists", "type": "sns_subscription_exists", "passed": False, "message": f"Subscription from {topic_name} to {queue_name} was not found."}

def sns_to_sqs_delivery(topic_name: str, queue_name: str, body: str) -> dict:
    sns_client = get_sns_client()
    sqs_client = get_sqs_client()
    try:
        topic_arn = f"arn:aws:sns:us-east-1:000000000000:{topic_name}"
        sns_client.publish(TopicArn=topic_arn, Message=body)
        queue_url = sqs_client.get_queue_url(QueueName=queue_name)["QueueUrl"]
        response = sqs_client.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=10, WaitTimeSeconds=2, VisibilityTimeout=0)
        messages = response.get("Messages", [])
        for msg in messages:
            if body in msg.get("Body", ""):
                return {"id": "fanout-message", "type": "sns_to_sqs_delivery", "passed": True, "message": f"Message delivered from {topic_name} to {queue_name}."}
        return {"id": "fanout-message", "type": "sns_to_sqs_delivery", "passed": False, "message": f"Message was not delivered from {topic_name} to {queue_name}."}
    except Exception as e:
        return {"id": "fanout-message", "type": "sns_to_sqs_delivery", "passed": False, "message": f"Message was not delivered from {topic_name} to {queue_name}."}