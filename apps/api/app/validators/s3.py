from app.aws_client import get_s3_client

def s3_bucket_exists(bucket: str) -> dict:
    client = get_s3_client()
    try:
        client.head_bucket(Bucket=bucket)
        return {"id": "bucket-exists", "type": "s3_bucket_exists", "passed": True, "message": f"Bucket {bucket} exists."}
    except Exception as e:
        return {"id": "bucket-exists", "type": "s3_bucket_exists", "passed": False, "message": f"Bucket {bucket} was not found."}

def s3_object_exists(bucket: str, key: str) -> dict:
    client = get_s3_client()
    try:
        client.head_object(Bucket=bucket, Key=key)
        return {"id": "object-exists", "type": "s3_object_exists", "passed": True, "message": f"Object {key} exists in bucket {bucket}."}
    except Exception as e:
        return {"id": "object-exists", "type": "s3_object_exists", "passed": False, "message": f"Object {key} was not found in bucket {bucket}."}

def s3_object_body_equals(bucket: str, key: str, value: str) -> dict:
    client = get_s3_client()
    try:
        response = client.get_object(Bucket=bucket, Key=key)
        body = response["Body"].read().decode("utf-8")
        if body.endswith("\n"):
            body = body[:-1]
        if body == value:
            return {"id": "object-body", "type": "s3_object_body_equals", "passed": True, "message": f"Object {key} content matches."}
        else:
            return {"id": "object-body", "type": "s3_object_body_equals", "passed": False, "message": f"Object {key} exists, but its content does not match the expected value."}
    except Exception as e:
        return {"id": "object-body", "type": "s3_object_body_equals", "passed": False, "message": f"Object {key} was not found in bucket {bucket}."}