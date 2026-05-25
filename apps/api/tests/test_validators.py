import pytest
from app.validators import run_check

def test_unknown_check_type():
    result = run_check({"id": "test", "type": "nonexistent_type"})
    assert result["passed"] == False
    assert "Unknown check type" in result["message"]