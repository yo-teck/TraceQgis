import json
from pathlib import Path
import copy

import jsonschema
import pytest
from jsonschema import validate, ValidationError

# Récupère le chemin du fichier courant (test_schema.py)
CURRENT_DIR = Path(__file__).parent.parent

# Remonte d'un cran (de test/test_schemas à carto/) et pointe vers le fichier JSON
SCHEMA_PATH = CURRENT_DIR.parent / "schema/base_yaml_validator.json"

# Charge le schéma
def load_schema():
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

VALID_JSON = {
    "object_types": {
        "rover": {
            "sprite": "default.jpg"
        }
    },
    "init_predicats": {
        "at": {
            "type": "position",
            "mobile_var": "?x",
            "fixed_var": "?y"
        }
    },
    "actions": {
        "load": {
            "duration": 10,
            "animations": [
                {
                    "name": "rotate",
                    "start_at": 0,
                    "end_at": 10,
                    "entity_vars": ["?x", "?y"]
                }
            ]
        }
    },
    "fixed_position": [
        "?z",
        {
            "var": "?c",
            "x": 10,
            "y": 10
        }
    ]
}

def test_valid_json():
    schema = load_schema()
    validate(instance=VALID_JSON, schema=schema)

def test_no_init_predicats():
    schema = load_schema()
    wrong_json = copy.deepcopy(VALID_JSON)
    wrong_json['init_predicats'] = {}
    with pytest.raises(ValidationError):
        validate(instance=wrong_json, schema=schema)

def test_no_object_types():
    schema = load_schema()
    wrong_json = copy.deepcopy(VALID_JSON)
    wrong_json['object_types'] = {}
    with pytest.raises(ValidationError):
        validate(instance=wrong_json, schema=schema)

def test_no_actions():
    schema = load_schema()
    wrong_json = copy.deepcopy(VALID_JSON)
    wrong_json['actions'] = {}
    with pytest.raises(ValidationError):
        validate(instance=wrong_json, schema=schema)

def test_no_fixed_position():
    schema = load_schema()
    wrong_json = copy.deepcopy(VALID_JSON)
    wrong_json['fixed_position'] = []
    # fixed_position peut être vide, mais minProperties n’est pas imposé pour fixed_position,
    # donc il ne faut pas lever d’erreur ici. Pour tester l’absence complète :
    del wrong_json['fixed_position']
    with pytest.raises(ValidationError):
        validate(instance=wrong_json, schema=schema)

def test_invalid_predicate_type():
    schema = load_schema()
    wrong_json = copy.deepcopy(VALID_JSON)
    wrong_json['init_predicats'] = {
        "at": {
            "type": "invalid_type",
            "mobile_var": "?x",
            "fixed_var": "?y"
        }
    }
    with pytest.raises(ValidationError):
        validate(instance=wrong_json, schema=schema)

def test_predicate_missing_field():
    schema = load_schema()
    wrong_json = copy.deepcopy(VALID_JSON)
    # Supprime mobile_var
    wrong_json['init_predicats'] = {
        "at": {
            "type": "position",
            "fixed_var": "?y"
        }
    }
    with pytest.raises(ValidationError):
        validate(instance=wrong_json, schema=schema)

def test_invalid_fixed_position_type_number():
    schema = load_schema()
    wrong_json = copy.deepcopy(VALID_JSON)
    # Valeur invalide (nombre) dans fixed_position
    wrong_json['fixed_position'] = [42]
    with pytest.raises(ValidationError):
        validate(instance=wrong_json, schema=schema)

def test_invalid_fixed_position_object_missing_key():
    schema = load_schema()
    wrong_json = copy.deepcopy(VALID_JSON)
    # Objet manque la clé 'y'
    wrong_json['fixed_position'] = [
        {
            "var": "?c",
            "x": 10
        }
    ]
    with pytest.raises(ValidationError):
        validate(instance=wrong_json, schema=schema)

def test_invalid_fixed_position_object_extra_key():
    schema = load_schema()
    wrong_json = copy.deepcopy(VALID_JSON)
    # Objet contient une clé supplémentaire 'z'
    wrong_json['fixed_position'] = [
        {
            "var": "?c",
            "x": 10,
            "y": 10,
            "z": 5
        }
    ]
    with pytest.raises(ValidationError):
        validate(instance=wrong_json, schema=schema)

def test_invalid_object_types_missing_sprite():
    schema = load_schema()
    wrong_json = copy.deepcopy(VALID_JSON)
    # 'sprite' manquant pour l'objet 'rover'
    wrong_json['object_types'] = {
        "rover": {}
    }
    with pytest.raises(ValidationError):
        validate(instance=wrong_json, schema=schema)

def test_invalid_object_types_extra_property():
    schema = load_schema()
    wrong_json = copy.deepcopy(VALID_JSON)
    # Propriété supplémentaire 'color' non autorisée
    wrong_json['object_types'] = {
        "rover": {
            "sprite": "default.jpg",
            "color": "red"
        }
    }
    with pytest.raises(ValidationError):
        validate(instance=wrong_json, schema=schema)

def test_action_missing_duration():
    schema = load_schema()
    wrong_json = copy.deepcopy(VALID_JSON)
    # Supprime 'duration' de l'action 'load'
    wrong_json['actions'] = {
        "load": {
            "animations": [
                {
                    "name": "rotate",
                    "start_at": 0,
                    "end_at": 10,
                    "entity_vars": ["?x", "?y"]
                }
            ]
        }
    }
    with pytest.raises(ValidationError):
        validate(instance=wrong_json, schema=schema)

def test_action_missing_animations():
    schema = load_schema()
    wrong_json = copy.deepcopy(VALID_JSON)
    # Supprime 'animations' de l'action 'load'
    wrong_json['actions'] = {
        "load": {
            "duration": 10
        }
    }
    with pytest.raises(ValidationError):
        validate(instance=wrong_json, schema=schema)

def test_action_empty_animations_array():
    schema = load_schema()
    wrong_json = copy.deepcopy(VALID_JSON)
    # 'animations' est vide (minItems=1)
    wrong_json['actions'] = {
        "load": {
            "duration": 10,
            "animations": []
        }
    }
    with pytest.raises(ValidationError):
        validate(instance=wrong_json, schema=schema)

def test_animation_missing_entity_vars():
    schema = load_schema()
    wrong_json = copy.deepcopy(VALID_JSON)
    # Supprime 'entity_vars' d'une animation
    wrong_json['actions'] = {
        "load": {
            "duration": 10,
            "animations": [
                {
                    "name": "rotate",
                    "start_at": 0,
                    "end_at": 10
                    # 'entity_vars' manquant
                }
            ]
        }
    }
    with pytest.raises(ValidationError):
        validate(instance=wrong_json, schema=schema)

def test_animation_entity_vars_not_list():
    schema = load_schema()
    wrong_json = copy.deepcopy(VALID_JSON)
    # 'entity_vars' n'est pas une liste
    wrong_json['actions'] = {
        "load": {
            "duration": 10,
            "animations": [
                {
                    "name": "rotate",
                    "start_at": 0,
                    "end_at": 10,
                    "entity_vars": "?x"
                }
            ]
        }
    }
    with pytest.raises(ValidationError):
        validate(instance=wrong_json, schema=schema)