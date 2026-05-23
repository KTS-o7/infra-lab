from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import yaml
from pathlib import Path
import app.config as config

class CheckSpec(BaseModel):
    id: str
    type: str
    bucket: Optional[str] = None
    key: Optional[Dict[str, Any]] = None
    value: Optional[str] = None
    queue_name: Optional[str] = None
    body: Optional[str] = None
    table_name: Optional[str] = None
    partition_key: Optional[Dict[str, Any]] = None
    sort_key: Optional[Dict[str, Any]] = None
    attribute: Optional[str] = None
    expected: Optional[Dict[str, Any]] = None
    function_name: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None
    api_name: Optional[str] = None
    route: Optional[str] = None
    expected_status: Optional[int] = None
    expected_json: Optional[Dict[str, Any]] = None
    request_json: Optional[Dict[str, Any]] = None
    topic_name: Optional[str] = None

class CommandSpec(BaseModel):
    id: str
    label: str
    command: str

class HintSpec(BaseModel):
    id: str
    title: str
    text: str
    penalty_xp: int = 0

class OwnedResource(BaseModel):
    type: str
    bucket: Optional[str] = None
    key: Optional[str] = None
    queue_name: Optional[str] = None
    topic_name: Optional[str] = None
    table_name: Optional[str] = None
    function_name: Optional[str] = None
    api_name: Optional[str] = None

class MissionDefinition(BaseModel):
    id: str
    order: int
    title: str
    summary: str
    difficulty: str
    services: List[str]
    xp: int
    estimated_minutes: int
    prerequisites: List[str] = []
    story: str
    learning_objectives: List[str]
    commands: List[CommandSpec]
    checks: List[CheckSpec]
    hints: List[HintSpec]
    owned_resources: List[OwnedResource]

class MissionLoader:
    _instances: Dict[str, MissionDefinition] = {}
    _loaded: bool = False

    @classmethod
    def load_missions(cls, missions_dir: str) -> Dict[str, MissionDefinition]:
        if cls._loaded:
            return cls._instances

        cls._instances = {}
        seen_ids: set = set()
        seen_orders: set = set()

        path = Path(missions_dir)
        if not path.exists():
            return cls._instances

        for mission_path in sorted(path.iterdir()):
            if not mission_path.is_dir():
                continue
            yml_file = mission_path / "mission.yml"
            if not yml_file.exists():
                continue

            with open(yml_file) as f:
                raw = yaml.safe_load(f)

            mission = MissionDefinition(**raw)

            if mission.id in seen_ids:
                raise ValueError(f"Duplicate mission ID: {mission.id}")
            if mission.order in seen_orders:
                raise ValueError(f"Duplicate mission order: {mission.order}")

            seen_ids.add(mission.id)
            seen_orders.add(mission.order)
            cls._instances[mission.id] = mission

        cls._loaded = True
        return cls._instances

    @classmethod
    def get_sorted_missions(cls) -> List[MissionDefinition]:
        instances = cls.load_missions(Path(config.MISSIONS_DIR))
        return sorted(instances.values(), key=lambda m: (m.order, m.id))