from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import BaseModel, model_validator

import app.config as config


class CheckSpec(BaseModel):
    id: str
    type: str
    bucket: Optional[str] = None
    key: Optional[Any] = None
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


class TargetStateItem(BaseModel):
    label: str
    value: str


class StepSpec(BaseModel):
    id: str
    title: str
    goal: str
    why: Optional[str] = None
    target_state: List[TargetStateItem] = []
    action: str
    command_id: str
    check_ids: List[str] = []
    success: Optional[str] = None
    notes: Optional[str] = None


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
    steps: List[StepSpec] = []
    hints: List[HintSpec]
    owned_resources: List[OwnedResource]

    @model_validator(mode="after")
    def validate_steps(self):
        step_ids = set()
        command_ids = {command.id for command in self.commands}
        check_ids = {check.id for check in self.checks}

        for step in self.steps:
            if step.id in step_ids:
                raise ValueError(f"Duplicate step ID in mission {self.id}: {step.id}")
            step_ids.add(step.id)

            if step.command_id not in command_ids:
                raise ValueError(
                    f"Step {step.id} references unknown command_id: {step.command_id}"
                )

            for check_id in step.check_ids:
                if check_id not in check_ids:
                    raise ValueError(
                        f"Step {step.id} references unknown check_id: {check_id}"
                    )

        return self


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
