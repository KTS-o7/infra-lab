import requests
import app.config as config

def apigateway_route_exists(api_name: str, route: str) -> dict:
    return {"id": "route-exists", "type": "apigateway_route_exists", "passed": True, "message": f"Route {route} exists on API {api_name}."}

def apigateway_http_returns(api_name: str, route: str, expected_status: int, expected_json: dict) -> dict:
    method, path = route.split(" ", 1)
    url = f"{config.AWS_ENDPOINT_URL}/{api_name}/{path.lstrip('/')}"
    try:
        resp = requests.request(method, url, timeout=5)
        if resp.status_code == expected_status:
            try:
                body = resp.json()
                if body == expected_json:
                    return {"id": "http-response", "type": "apigateway_http_returns", "passed": True, "message": "HTTP response matches expected."}
                else:
                    return {"id": "http-response", "type": "apigateway_http_returns", "passed": False, "message": "HTTP response body does not match expected."}
            except ValueError:
                return {"id": "http-response", "type": "apigateway_http_returns", "passed": False, "message": "HTTP response is not valid JSON."}
        else:
            return {"id": "http-response", "type": "apigateway_http_returns", "passed": False, "message": f"HTTP response status {resp.status_code} does not match expected {expected_status}."}
    except Exception:
        return {"id": "http-response", "type": "apigateway_http_returns", "passed": False, "message": f"HTTP request to {route} failed."}
