import pytest
import tempfile
import os
import yaml
from pathlib import Path
from typing import Iterator, Tuple
from jsonschema import validate

from custom.utils.yaml_helper import YamlHelper
from custom.enums.action_mapping import ActionType
from custom.business.dm_carto_configuration_model import DmCartoConfigurationModel

VALID_YAML = {
    "object_types": {"hero": {"sprite": "hero.png"}},
    "init_predicats": {"p1": {"type": "position", "mobile_var": "?hero", "fixed_var": "?castle"}},
    "actions": {
        "a1": {
            "duration": 10,
            "animations": [
                {
                    "name": "move_to",
                    "start_at": 0,
                    "end_at": 10,
                    "var_object_to_move": "?hero",
                    "var_object_destination": "?castle",
                    "text": "Go!"
                }
            ]
        }
    },
    "fixed_position": [{"var": "?castle", "x": 1.0, "y": 2.0}]
}

VALID_SCHEMA = {
    "type": "object",
    "required": ["object_types", "init_predicats", "actions", "fixed_position"],
    "properties": {
        "object_types": {"type": "object"},
        "init_predicats": {"type": "object"},
        "actions": {"type": "object"},
        "fixed_position": {"type": "array"}
    }
}

INVALID_YAML_CONTENT = "object_types: {hero: sprite: hero.png"
INVALID_SCHEMA = "type: object\nproperties:\n  object_types: {type: string"

@pytest.fixture
def yaml_and_schema_files() -> Iterator[Tuple[str, str]]:
    with tempfile.TemporaryDirectory() as tmpdir:
        yaml_path = os.path.join(tmpdir, "config.yaml")
        schema_path = os.path.join(tmpdir, "schema.yaml")

        with open(yaml_path, "w", encoding="utf-8") as f:
            yaml.dump(VALID_YAML, f)

        with open(schema_path, "w", encoding="utf-8") as f:
            yaml.dump(VALID_SCHEMA, f)

        yield yaml_path, schema_path

def test_valid_yaml_and_schema(yaml_and_schema_files: Tuple[str, str]) -> None:
    yaml_path, schema_path = yaml_and_schema_files
    model = YamlHelper.read_file(yaml_path, schema_path)
    assert isinstance(model, DmCartoConfigurationModel)
    assert "hero" in model.object_types  # pas ?hero
    assert "a1" in model.actions

def test_invalid_extension(tmp_path: Path) -> None:
    fake_path = tmp_path / "config.txt"
    fake_path.write_text("object_types: {}")
    with pytest.raises(ValueError, match="extension"):
        YamlHelper.read_file(str(fake_path), str(fake_path))

def test_missing_yaml_file(tmp_path: Path) -> None:
    schema_path = tmp_path / "schema.yaml"
    yaml.dump(VALID_SCHEMA, schema_path.open("w", encoding="utf-8"))
    with pytest.raises(FileNotFoundError):
        YamlHelper.read_file("missing.yaml", str(schema_path))

def test_yaml_parsing_error(tmp_path: Path) -> None:
    bad_yaml = tmp_path / "bad.yaml"
    bad_yaml.write_text(INVALID_YAML_CONTENT)
    schema_path = tmp_path / "schema.yaml"
    yaml.dump(VALID_SCHEMA, schema_path.open("w", encoding="utf-8"))
    with pytest.raises(ValueError, match="lecture YAML"):
        YamlHelper.read_file(str(bad_yaml), str(schema_path))

def test_schema_parsing_error(tmp_path: Path) -> None:
    good_yaml = tmp_path / "config.yaml"
    yaml.dump(VALID_YAML, good_yaml.open("w", encoding="utf-8"))
    bad_schema = tmp_path / "bad_schema.yaml"
    bad_schema.write_text(INVALID_SCHEMA)
    with pytest.raises(ValueError, match="lecture du schéma"):
        YamlHelper.read_file(str(good_yaml), str(bad_schema))

def test_schema_validation_error(tmp_path: Path) -> None:
    invalid_yaml = {
        "object_types": {},
        "init_predicats": {},
        "actions": {},  # manque fixed_position
    }
    yaml_path = tmp_path / "config.yaml"
    yaml.dump(invalid_yaml, yaml_path.open("w", encoding="utf-8"))
    schema_path = tmp_path / "schema.yaml"
    yaml.dump(VALID_SCHEMA, schema_path.open("w", encoding="utf-8"))
    with pytest.raises(ValueError, match="Validation échouée"):
        YamlHelper.read_file(str(yaml_path), str(schema_path))

def test_action_type_enum_matching():
    for action in ActionType:
        assert ActionType(action.value) == action

def test_get_action_type_by_value_valid():
    action_type = YamlHelper.get_action_type_by_value("move_to")
    assert action_type is not None
    assert isinstance(action_type, ActionType)

def test_get_action_type_by_value_invalid():
    assert YamlHelper.get_action_type_by_value("nonexistent") is None

def test_validate_animation_success():
    anim = {
        "name": "move_to",
        "start_at": 0,
        "end_at": 10,
        "var_object_to_move": "?hero",
        "var_object_destination": "?castle",
        "text": "Go!"
    }
    YamlHelper.validate_animation(anim)

def test_validate_animation_failure():
    anim = {
        "name": "move_to",  # manque les champs requis
        "start_at": 0,
        "end_at": 10
    }
    with pytest.raises(ValueError, match="Validation échouée"):
        YamlHelper.validate_animation(anim)

def test_validate_actions_success():
    YamlHelper.validate_actions(VALID_YAML)

def test_validate_actions_failure():
    bad_data = {
        "actions": {
            "a1": {
                "duration": 10,
                "animations": [
                    {
                        "name": "move_to",
                        "start_at": 0,
                        "end_at": 10
                        # manque var_object_to_move et var_object_destination
                    }
                ]
            }
        }
    }
    with pytest.raises(ValueError, match="Validation échouée"):
        YamlHelper.validate_actions(bad_data)
