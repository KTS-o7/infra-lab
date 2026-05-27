from pydantic import BaseModel, model_validator
from typing import List, Optional, Dict, Any
import yaml
from pathlib import Path
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
    target_prefix: Optional[str] = None
    expected_status: Optional[int] = None
    expected_json: Optional[Dict[str, Any]] = None
    request_json: Optional[Dict[str, Any]] = None
    expected_body_contains: Optional[str] = None
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
    command_id: Optional[str] = None
    check_ids: List[str] = []
    success: Optional[str] = None
    notes: Optional[str] = None

class HintSpec(BaseModel):
    id: str
    title: str
    text: str
    level: str = "nudge"
    applies_to_checks: List[str] = []
    penalty_xp: int = 0

class CourseModule(BaseModel):
    id: str
    order: int
    title: str
    required: bool = True
    capability: str
    capability_label: str
    summary: str
    capstone_mission_id: Optional[str] = None
    capstone_required: bool = False

class CourseDefinition(BaseModel):
    id: str
    title: str
    summary: str
    modules: List[CourseModule]

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
    module: str = "legacy"
    submodule: str = "legacy"
    mission_type: str = "lesson"
    required: bool = True
    capability: Optional[str] = None
    title: str
    summary: str
    difficulty: str
    services: List[str]
    xp: int
    estimated_minutes: int
    prerequisites: List[str] = []
    story: str
    learning_objectives: List[str]
    motivation: Optional[str] = None
    theory: Optional[str] = None
    thought_process: Optional[str] = None
    debrief: Optional[str] = None
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

            if step.command_id and step.command_id not in command_ids:
                raise ValueError(f"Step {step.id} references unknown command_id: {step.command_id}")

            for check_id in step.check_ids:
                if check_id not in check_ids:
                    raise ValueError(f"Step {step.id} references unknown check_id: {check_id}")

        return self

class MissionLoader:
    _instances: Dict[str, MissionDefinition] = {}
    _course: Optional[CourseDefinition] = None
    _loaded: bool = False

    @classmethod
    def load_missions(cls, missions_dir: str) -> Dict[str, MissionDefinition]:
        if cls._loaded:
            return cls._instances

        cls._instances = {}
        seen_ids: set = set()
        path = Path(missions_dir)
        if not path.exists():
            cls._course = cls._load_course(path, cls._instances)
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

            seen_ids.add(mission.id)
            cls._instances[mission.id] = mission

        cls._course = cls._load_course(path, cls._instances)
        cls._loaded = True
        return cls._instances

    @classmethod
    def load_course(cls, missions_dir: str) -> CourseDefinition:
        cls.load_missions(missions_dir)
        return cls._course

    @classmethod
    def _load_course(cls, path: Path, missions: Dict[str, MissionDefinition]) -> CourseDefinition:
        course_file = path / "course.yml"
        if not course_file.exists():
            return cls._legacy_course(missions)

        with open(course_file) as f:
            raw = yaml.safe_load(f)
        course = CourseDefinition(**raw)
        module_ids = set()
        module_orders = set()
        modules_by_id = {}
        for module in course.modules:
            if module.id in module_ids:
                raise ValueError(f"Duplicate module ID: {module.id}")
            if module.order in module_orders:
                raise ValueError(f"Duplicate module order: {module.order}")
            if module.capstone_required and not module.capstone_mission_id:
                raise ValueError(f"Module {module.id} requires a capstone but has no capstone_mission_id")
            if module.capstone_mission_id and module.capstone_mission_id not in missions:
                raise ValueError(f"Module {module.id} references unknown capstone_mission_id: {module.capstone_mission_id}")
            module_ids.add(module.id)
            module_orders.add(module.order)
            modules_by_id[module.id] = module

        for mission in missions.values():
            if mission.module not in modules_by_id:
                raise ValueError(f"Mission {mission.id} references unknown module: {mission.module}")
            module = modules_by_id[mission.module]
            if mission.capability and mission.capability != module.capability:
                raise ValueError(f"Mission {mission.id} capability does not match module {mission.module}")
            if mission.mission_type == "module_capstone":
                mission.required = module.capstone_required
            if not mission.capability:
                mission.capability = module.capability

        return course

    @classmethod
    def _legacy_course(cls, missions: Dict[str, MissionDefinition]) -> CourseDefinition:
        for mission in missions.values():
            mission.module = mission.module or "legacy"
            mission.submodule = mission.submodule or "legacy"
            mission.mission_type = mission.mission_type or "lesson"
            mission.required = True
            mission.capability = mission.capability or "legacy_infrastructure"
        return CourseDefinition(
            id="legacy-infra-quest",
            title="Infra Quest",
            summary="Local infrastructure missions.",
            modules=[
                CourseModule(
                    id="legacy",
                    order=0,
                    title="Missions",
                    required=True,
                    capability="legacy_infrastructure",
                    capability_label="Infrastructure",
                    summary="Existing local infrastructure missions.",
                )
            ],
        )

    @classmethod
    def get_sorted_missions(cls) -> List[MissionDefinition]:
        instances = cls.load_missions(Path(config.MISSIONS_DIR))
        course = cls.load_course(config.MISSIONS_DIR)
        module_order = {module.id: module.order for module in course.modules}
        return sorted(instances.values(), key=lambda m: (module_order.get(m.module, 999), m.order, m.id))
