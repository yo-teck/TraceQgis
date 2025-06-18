from dataclasses import dataclass, field
from typing import Dict, List, Union

from ..enums.action_mapping import ActionType

@dataclass
class ObjectType:
    sprite: str

@dataclass
class Predicate:
    type: str  # 'position' or 'storage'
    mobile_var: str
    fixed_var: str

@dataclass
class Animation:
    action_type: ActionType
    start_at: int
    end_at: int
    attributes: Dict[str, any] = field(default_factory=dict)

    def __post_init__(self):
        required = self.action_type.schema.get('required', [])
        missing = [k for k in required if k not in self.attributes]
        if missing:
            raise ValueError(f"Attributes missing for {self.action_type.name}: {missing}")

@dataclass
class Action:
    duration: int
    animations: List[Animation] = field(default_factory=list)

    def __post_init__(self):
        if not self.animations:
            raise ValueError("'animations' must contain at least one Animation instance")

@dataclass
class FixedPositionVar:
    var: str
    x: float
    y: float

FixedPositionEntry = Union[str, FixedPositionVar]

@dataclass
class DmCartoConfigurationModel:
    object_types: Dict[str, ObjectType] = field(default_factory=dict)
    init_predicats: Dict[str, Predicate] = field(default_factory=dict)
    actions: Dict[str, Action] = field(default_factory=dict)
    fixed_position: List[FixedPositionEntry] = field(default_factory=list)

    def validate(self):
        if not self.object_types:
            raise ValueError("'object_types' must have at least one entry")
        if not self.init_predicats:
            raise ValueError("'init_predicats' must have at least one entry")
        if not self.actions:
            raise ValueError("'actions' must have at least one entry")

    def load_from_parsed(self, data: dict):
        for key, val in data.get('object_types', {}).items():
            self.object_types[key] = ObjectType(**val)
        for key, val in data.get('init_predicats', {}).items():
            self.init_predicats[key] = Predicate(**val)
        for key, val in data.get('actions', {}).items():
            anims = []
            for anim in val.get('animations', []):
                atype = ActionType.from_str(anim['name'])
                attrs = {k: v for k, v in anim.items() if k not in {'name', 'start_at', 'end_at'}}
                anims.append(Animation(
                    action_type=atype,
                    start_at=anim['start_at'], end_at=anim['end_at'],
                    attributes=attrs
                ))
            self.actions[key] = Action(duration=val['duration'], animations=anims)
        for entry in data.get('fixed_position', []):
            if isinstance(entry, str):
                self.fixed_position.append(entry)
            elif isinstance(entry, dict):
                self.fixed_position.append(FixedPositionVar(**entry))
            else:
                raise ValueError(f"Invalid fixed_position entry: {entry}")
        self.validate()

    def get_sprite_url_by_object_type(self, object_type: str):
        object_type = self.object_types[object_type]
        return object_type.sprite
