import pytest
import tempfile
import os
import yaml
from pathlib import Path
from typing import Iterator, Tuple
from jsonschema import validate, ValidationError
from custom.utils.yaml_helper import YamlHelper
from custom.enums.action_mapping import ActionType
from custom.business.domain_problem_model import DomainProblemModel

VALID_YAML: dict[str, object] = {
    "actions": [
        {
            "animations": [
                {
                    "name": "text",
                    "text": "Hello",
                    "var_object": "hero"
                }
            ]
        }
    ]
}

VALID_SCHEMA: dict[str, object] = {
    "type": "object",
    "properties": {
        "actions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "animations": {
                        "type": "array",
                        "items": {"type": "object"}
                    }
                },
                "required": ["animations"]
            }
        }
    },
    "required": ["actions"]
}

INVALID_YAML_CONTENT = "name: Alice\nage: ["
INVALID_SCHEMA = "type: object\nproperties:\n  name: {type: string"

@pytest.fixture
def yaml_and_schema_files() -> Iterator[Tuple[str, str]]:
    with tempfile.TemporaryDirectory() as tmpdir:
        yaml_path: str = os.path.join(tmpdir, "data.yaml")
        schema_path: str = os.path.join(tmpdir, "schema.yaml")

        with open(yaml_path, "w", encoding="utf-8") as f:
            yaml.dump(VALID_YAML, f)

        with open(schema_path, "w", encoding="utf-8") as f:
            yaml.dump(VALID_SCHEMA, f)

        yield yaml_path, schema_path

def test_valid_yaml_and_schema(yaml_and_schema_files: Tuple[str, str]) -> None:
    yaml_path, schema_path = yaml_and_schema_files
    data = YamlHelper.read_file(yaml_path, schema_path)
    assert data == VALID_YAML

def test_invalid_extension(tmp_path: Path) -> None:
    fake_path = tmp_path / "data.txt"
    fake_path.write_text("name: Bob")
    with pytest.raises(ValueError, match="extension"):
        YamlHelper.read_file(str(fake_path), str(fake_path))

def test_missing_yaml_file(tmp_path: Path) -> None:
    schema_path = tmp_path / "schema.yaml"
    schema_path.write_text("type: object")
    with pytest.raises(FileNotFoundError):
        YamlHelper.read_file("inexistant.yaml", str(schema_path))

def test_yaml_parsing_error(tmp_path: Path) -> None:
    bad_yaml = tmp_path / "bad.yaml"
    bad_yaml.write_text(INVALID_YAML_CONTENT)
    schema = tmp_path / "schema.yaml"
    yaml.dump(VALID_SCHEMA, schema.open("w", encoding="utf-8"))
    with pytest.raises(ValueError, match="lecture YAML"):
        YamlHelper.read_file(str(bad_yaml), str(schema))

def test_schema_parsing_error(tmp_path: Path) -> None:
    good_yaml = tmp_path / "data.yaml"
    yaml.dump(VALID_YAML, good_yaml.open("w", encoding="utf-8"))
    bad_schema = tmp_path / "bad_schema.yaml"
    bad_schema.write_text(INVALID_SCHEMA)
    with pytest.raises(ValueError, match="lecture du schéma"):
        YamlHelper.read_file(str(good_yaml), str(bad_schema))

def test_schema_validation_error(tmp_path: Path) -> None:
    invalid_yaml = tmp_path / "data.yaml"
    yaml.dump({"actions": [{}]}, invalid_yaml.open("w", encoding="utf-8"))  # manque animations
    schema = tmp_path / "schema.yaml"
    yaml.dump(VALID_SCHEMA, schema.open("w", encoding="utf-8"))
    with pytest.raises(ValueError, match="Validation échouée"):
        YamlHelper.read_file(str(invalid_yaml), str(schema))

def test_action_type_enum_matching():
    for action in ActionType:
        assert ActionType(action.value) == action

def test_get_action_type_by_value():
    move = YamlHelper.get_action_type_by_value("move")
    assert move is not None
    assert move.get_classname() == "ActionMove"
    assert "entity_id" in move.get_attributes()

def test_invalid_action_type():
    invalid = YamlHelper.get_action_type_by_value("non_existing")
    assert invalid is None

def test_validate_animation_success():
    animation = {
        "name": "text",
        "text": "Hello",
        "var_object": "hero"
    }
    YamlHelper.validate_animation(animation)

def test_validate_animation_failure():
    animation = {
        "name": "text",
        "text": "Hello"
        # manque "var_object"
    }
    with pytest.raises(ValueError, match="Validation échouée"):
        YamlHelper.validate_animation(animation)

def test_validate_actions_success():
    data = {
        "actions": [
            {
                "animations": [
                    {
                        "name": "move_to",
                        "var_object_to_move": "hero",
                        "var_object_destination": "castle",
                        "text": "Go!"
                    }
                ]
            }
        ]
    }
    YamlHelper.validate_actions(data)

def test_validate_actions_failure():
    data = {
        "actions": [
            {
                "animations": [
                    {
                        "name": "move_to",
                        "text": "Go!"
                        # manque les deux variables requises
                    }
                ]
            }
        ]
    }
    with pytest.raises(ValueError, match="Validation échouée"):
        YamlHelper.validate_actions(data)
