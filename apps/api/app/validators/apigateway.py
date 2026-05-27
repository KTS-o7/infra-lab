import requests
import app.config as config
from app.aws_client import get_apigateway_client


def _api_id_by_name(api_name: str) -> str | None:
    client = get_apigateway_client()
    apis = client.get_apis()
    for api in apis.get("Items", []):
        if api.get("Name") == api_name:
            return api.get("ApiId")
    return None


def apigateway_api_exists(api_name: str) -> dict:
    if _api_id_by_name(api_name):
        return {"id": "api-exists", "type": "apigateway_api_exists", "passed": True, "message": f"API {api_name} exists."}
    return {"id": "api-exists", "type": "apigateway_api_exists", "passed": False, "message": f"API {api_name} was not found."}


def apigateway_route_exists(api_name: str, route: str, target_prefix: str | None = None) -> dict:
    try:
        client = get_apigateway_client()
        api_id = _api_id_by_name(api_name)
        if not api_id:
            return {"id": "route-exists", "type": "apigateway_route_exists", "passed": False, "message": f"API {api_name} was not found."}
        routes = client.get_routes(ApiId=api_id)
        for item in routes.get("Items", []):
            if item.get("RouteKey") == route:
                if target_prefix and not str(item.get("Target", "")).startswith(target_prefix):
                    return {"id": "route-exists", "type": "apigateway_route_exists", "passed": False, "message": f"Route {route} is not wired to the expected integration."}
                return {"id": "route-exists", "type": "apigateway_route_exists", "passed": True, "message": f"Route {route} exists on API {api_name}."}
        return {"id": "route-exists", "type": "apigateway_route_exists", "passed": False, "message": f"Route {route} was not found on API {api_name}."}
    except Exception:
            return {"id": "route-exists", "type": "apigateway_route_exists", "passed": False, "message": f"Route {route} was not found on API {api_name}."}


def api_url_by_name(api_name: str, path: str) -> str | None:
    api_id = _api_id_by_name(api_name)
    if not api_id:
        return None
    return f"{config.AWS_ENDPOINT_URL}/restapis/{api_id}/default/_user_request_/{path.lstrip('/')}"


def apigateway_http_returns(api_name: str, route: str, expected_status: int, expected_json: dict) -> dict:
    method, path = route.split(" ", 1)
    try:
        url = api_url_by_name(api_name, path)
        if not url:
            return {"id": "http-response", "type": "apigateway_http_returns", "passed": False, "message": f"API {api_name} was not found."}
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
