from app.aws_client import get_s3_client, get_sqs_client, get_dynamodb_client, get_lambda_client, get_sns_client, get_apigateway_client

def reset_owned_resources(owned_resources: list) -> list:
    deleted = []
    s3_objects = []
    s3_buckets = []

    for res in owned_resources:
        res_type = res.get("type")
        if res_type == "s3_object":
            s3_objects.append(res)
        elif res_type == "s3_bucket":
            s3_buckets.append(res)
        elif res_type == "sqs_queue":
            try:
                client = get_sqs_client()
                url = client.get_queue_url(QueueName=res["queue_name"])["QueueUrl"]
                client.delete_queue(QueueUrl=url)
                deleted.append(f"sqs://{res['queue_name']}")
            except Exception:
                pass
        elif res_type == "dynamodb_table":
            try:
                client = get_dynamodb_client()
                client.delete_table(TableName=res["table_name"])
                deleted.append(f"dynamodb://{res['table_name']}")
            except Exception:
                pass
        elif res_type == "lambda_function":
            try:
                client = get_lambda_client()
                client.delete_function(FunctionName=res["function_name"])
                deleted.append(f"lambda://{res['function_name']}")
            except Exception:
                pass
        elif res_type == "sns_topic":
            try:
                client = get_sns_client()
                client.delete_topic(TopicArn=f"arn:aws:sns:us-east-1:000000000000:{res['topic_name']}")
                deleted.append(f"sns://{res['topic_name']}")
            except Exception:
                pass
        elif res_type == "apigateway_api":
            try:
                client = get_apigateway_client()
                apis = client.get_apis()
                for api in apis.get("Items", []):
                    if api.get("Name") == res["api_name"]:
                        client.delete_api(ApiId=api["ApiId"])
                        deleted.append(f"apigateway://{res['api_name']}")
                        break
            except Exception:
                pass
        elif res_type == "none":
            pass

    for obj in s3_objects:
        try:
            client = get_s3_client()
            client.delete_object(Bucket=obj["bucket"], Key=obj["key"])
            deleted.append(f"s3://{obj['bucket']}/{obj['key']}")
        except Exception:
            pass

    for buc in s3_buckets:
        try:
            client = get_s3_client()
            client.delete_bucket(Bucket=buc["bucket"])
            deleted.append(f"s3://{buc['bucket']}")
        except Exception:
            pass

    return deleted