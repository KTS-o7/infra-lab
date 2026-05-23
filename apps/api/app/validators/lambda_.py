from app.aws_client import get_lambda_client
import json

def lambda_function_exists(function_name: str) -> dict:
    client = get_lambda_client()
    try:
        client.get_function(FunctionName=function_name)
        return {"id": "function-exists", "type": "lambda_function_exists", "passed": True, "message": f"Function {function_name} exists."}
    except Exception as e:
        return {"id": "function-exists", "type": "lambda_function_exists", "passed": False, "message": f"Function {function_name} was not found."}

def lambda_invoke_returns(function_name: str, payload: dict, expected: dict) -> dict:
    client = get_lambda_client()
    try:
        response = client.invoke(FunctionName=function_name, Payload=json.dumps(payload))
        result = json.loads(response["Payload"].read().decode("utf-8"))
        if result == expected:
            return {"id": "invoke-result", "type": "lambda_invoke_returns", "passed": True, "message": f"Function {function_name} returned expected response."}
        else:
            return {"id": "invoke-result", "type": "lambda_invoke_returns", "passed": False, "message": f"Function {function_name} response does not match expected."}
    except Exception as e:
        return {"id": "invoke-result", "type": "lambda_invoke_returns", "passed": False, "message": f"Function {function_name} invocation failed."}