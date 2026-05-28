from app.aws_client import get_client

def runtime_floci_available() -> dict:
    try:
        client = get_client("s3")
        client.list_buckets()
        return {"id": "floci-available", "type": "runtime_floci_available", "passed": True, "message": "The local AWS emulator is reachable."}
    except Exception:
        return {"id": "floci-available", "type": "runtime_floci_available", "passed": False, "message": "The local AWS emulator is not reachable at http://floci:4566."}