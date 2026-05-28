from app.validators.apigateway import apigateway_api_exists, apigateway_route_exists, apigateway_http_returns


def test_apigateway_api_exists_pass(monkeypatch):
    class FakeClient:
        def get_apis(self):
            return {"Items": [{"Name": "starter-api", "ApiId": "abc123"}]}

    monkeypatch.setattr("app.validators.apigateway.get_apigateway_client", lambda: FakeClient())

    result = apigateway_api_exists("starter-api")

    assert result["passed"]


def test_apigateway_route_exists_pass(monkeypatch):
    class FakeClient:
        def get_apis(self):
            return {"Items": [{"Name": "starter-api", "ApiId": "abc123"}]}

        def get_routes(self, ApiId):
            return {"Items": [{"RouteKey": "GET /hello"}]}

    monkeypatch.setattr("app.validators.apigateway.get_apigateway_client", lambda: FakeClient())

    result = apigateway_route_exists("starter-api", "GET /hello")

    assert result["passed"]


def test_apigateway_route_exists_validates_target_prefix(monkeypatch):
    class FakeClient:
        def get_apis(self):
            return {"Items": [{"Name": "starter-api", "ApiId": "abc123"}]}

        def get_routes(self, ApiId):
            return {"Items": [{"RouteKey": "GET /hello", "Target": "integrations/int-123"}]}

    monkeypatch.setattr("app.validators.apigateway.get_apigateway_client", lambda: FakeClient())

    result = apigateway_route_exists("starter-api", "GET /hello", target_prefix="integrations/")

    assert result["passed"]


def test_apigateway_route_exists_fails_when_target_missing(monkeypatch):
    class FakeClient:
        def get_apis(self):
            return {"Items": [{"Name": "starter-api", "ApiId": "abc123"}]}

        def get_routes(self, ApiId):
            return {"Items": [{"RouteKey": "GET /hello"}]}

    monkeypatch.setattr("app.validators.apigateway.get_apigateway_client", lambda: FakeClient())

    result = apigateway_route_exists("starter-api", "GET /hello", target_prefix="integrations/")

    assert not result["passed"]


def test_apigateway_route_exists_fails_when_route_missing(monkeypatch):
    class FakeClient:
        def get_apis(self):
            return {"Items": [{"Name": "starter-api", "ApiId": "abc123"}]}

        def get_routes(self, ApiId):
            return {"Items": [{"RouteKey": "POST /other"}]}

    monkeypatch.setattr("app.validators.apigateway.get_apigateway_client", lambda: FakeClient())

    result = apigateway_route_exists("starter-api", "GET /hello")

    assert not result["passed"]


def test_apigateway_http_returns_uses_api_id(monkeypatch):
    class FakeClient:
        def get_apis(self):
            return {"Items": [{"Name": "starter-api", "ApiId": "abc123"}]}

    class FakeResponse:
        status_code = 200

        def json(self):
            return {"message": "Hello from local API"}

    seen = {}

    def fake_request(method, url, timeout):
        seen["method"] = method
        seen["url"] = url
        seen["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr("app.validators.apigateway.get_apigateway_client", lambda: FakeClient())
    monkeypatch.setattr("app.validators.apigateway.requests.request", fake_request)
    monkeypatch.setattr("app.validators.apigateway.config.AWS_ENDPOINT_URL", "http://floci:4566")

    result = apigateway_http_returns("starter-api", "GET /hello", 200, {"message": "Hello from local API"})

    assert result["passed"]
    assert seen == {"method": "GET", "url": "http://floci:4566/restapis/abc123/default/_user_request_/hello", "timeout": 5}
