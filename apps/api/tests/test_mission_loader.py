import pytest
from app.mission_loader import MissionLoader

def test_mission_loader_schema():
    loader = MissionLoader()
    assert True