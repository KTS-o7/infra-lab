from app.config import (
    AWS_ACCESS_KEY_ID,
    get_local_only_status,
    get_floci_endpoint,
)

def test_fake_credentials():
    assert AWS_ACCESS_KEY_ID == "test"

def test_floci_endpoint():
    assert "floci" in get_floci_endpoint()

def test_local_only_status():
    status = get_local_only_status()
    assert status["status"] == "enforced"