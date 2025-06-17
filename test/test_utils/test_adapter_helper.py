from typing import Tuple

from custom.constants.pddl_yaml import DEFAULT_ANIMATION_DURATION
from custom.enums.predicat_mapping import PredicatMapping
from custom.utils.adapter_helper import AdapterHelper
from test.common.pddl_constants import create_parser_for_test

OBJECT_TYPES: dict[str, str] = {
    "r1": "Robot",
    "r2": "Robot",
    "s3": "Serpent"
}

ACTIONS: dict[str, list[Tuple[str,str]]] = {
    "MOVE": [
        ("?obj", "object"),
        ("?loc", "location"),
    ],
    "LOAD": [
        ("?obj", "object"),
        ("?loc", "location"),
    ],
    "ROTATE": [
        ("?obj1", "object"),
        ("?obj2", "object"),
    ]
}

PREDICATES_WITH_AT_CORRECT: dict[str, list[tuple[str,str]]] = {
    'at': [
        ("?obj", "object"),
        ("?loc", "location"),
    ],
    'visible': [
        ("?obj", "object"),
        ("?obj", "object"),
    ]
}

PREDICATES_WITH_AT_INCORRECT: dict[str, list[tuple[str,str]]] = {
    'at': [
        ("?obj", "object"),
    ],
    'visible': [
        ("?obj", "object"),
        ("?obj", "object"),
    ]
}

PREDICATES_WITHOUT_AT: dict[str, list[tuple[str,str]]] = {
    'visible': [
        ("?obj", "object"),
        ("?obj", "object"),
    ]
}

def test_adapt_object_type():
    res = AdapterHelper.adapt_object_type(OBJECT_TYPES)
    assert res == {'Robot': {'sprite': 'default_sprite.png'}, 'Serpent': {'sprite': 'default_sprite.png'}}

def test_adapt_actions():
    res = AdapterHelper.adapt_actions(ACTIONS)
    assert res == {
        'MOVE': {
            "duration": DEFAULT_ANIMATION_DURATION,
            'animations': [ {
                "name": "",
                "start_at": 0,
                "end_at": DEFAULT_ANIMATION_DURATION,
                "entity_vars": ["?obj", "?loc"],
            } ]
        },
        'LOAD': {
            "duration": DEFAULT_ANIMATION_DURATION,
            'animations': [ {
                "name": "",
                "start_at": 0,
                "end_at": DEFAULT_ANIMATION_DURATION,
                "entity_vars": ["?obj", "?loc"],
            } ]
        },
        'ROTATE': {
            "duration": DEFAULT_ANIMATION_DURATION,
            'animations': [ {
                "name": "",
                "start_at": 0,
                "end_at": DEFAULT_ANIMATION_DURATION,
                "entity_vars": ["?obj1", "?obj2"],
            } ]
        }
    }

def test_adapt_predicats_with_at_incorrect():
    res = AdapterHelper.adapt_predicats(PREDICATES_WITH_AT_INCORRECT)
    assert res == {}

def test_adapt_predicats_without_at():
    res = AdapterHelper.adapt_predicats(PREDICATES_WITHOUT_AT)
    assert res == {}

def test_adapt_predicates_with_at_correct():
    res = AdapterHelper.adapt_predicats(PREDICATES_WITH_AT_CORRECT)
    assert res == {
        "at" : {
            "type": PredicatMapping.POSITION.value,
            "mobile_var": "?obj",
            "fixed_var": "?loc",
        }
    }

def test_problem_to_yaml_data_config(tmp_path):
    parser = create_parser_for_test(tmp_path)
    assert AdapterHelper.domain_problem_to_yaml_data_config(parser) == {
          "object_types": {
            "location": {
              "sprite": "default_sprite.png"
            },
            "truck": {
              "sprite": "default_sprite.png"
            },
            "package": {
              "sprite": "default_sprite.png"
            },
            "city": {
              "sprite": "default_sprite.png"
            }
          },
          "init_predicats": {
            "at": {
              "type": PredicatMapping.POSITION.value,
              "mobile_var": "?obj",
              "fixed_var": "?loc"
            }
          },
          "actions": {
            "LOAD-TRUCK": {
              "duration": DEFAULT_ANIMATION_DURATION,
              "animations": [
                {
                  "name": "",
                  "start_at": 0,
                  "end_at": DEFAULT_ANIMATION_DURATION,
                  "entity_vars": ["?pkg","?truck", "?loc"],
                }
              ]
            },
            "UNLOAD-TRUCK": {
              "duration": DEFAULT_ANIMATION_DURATION,
              "animations": [
                {
                  "name": "",
                  "start_at": 0,
                  "end_at": DEFAULT_ANIMATION_DURATION,
                  "entity_vars": ["?pkg", "?truck", "?loc"],
                }
              ]
            },
            "DRIVE-TRUCK": {
              "duration": DEFAULT_ANIMATION_DURATION,
              "animations": [
                {
                  "name": "",
                  "start_at": 0,
                  "end_at": DEFAULT_ANIMATION_DURATION,
                  "entity_vars": ["?truck", "?from", "?to", "?city"],
                }
              ]
            }
          },
          "fixed_position": []
        }


def test_domain_problem_to_map_entity(tmp_path):
    parser = create_parser_for_test(tmp_path)
    configuration = parser.get_configuration()

    configuration.fixed_position = [
        parser.FixedPositionVar(var="?loc", x=10.0, y=20.0)
    ]
    configuration.init_predicats = {
        "at": parser.Predicate(type=PredicatMapping.POSITION.value, mobile_var="?obj", fixed_var="?loc")
    }
    parser.initial_state = [
        ("at", "package_1", "city_1", "truck_1", "?loc")
    ]
    parser.get_configuration = lambda: configuration  # forcer méthode simulée

    entities = AdapterHelper.domain_problem_to_map_entity(parser)

    assert isinstance(entities, list)
    assert any(e.id == "?loc" for e in entities)
    assert any(e.id == "package_1" for e in entities)

    fixed_entity = next(e for e in entities if e.id == "?loc")
    mobile_entity = next(e for e in entities if e.id == "package_1")

    assert fixed_entity.get_latitude() == 20.0
    assert fixed_entity.get_longitude() == 10.0
    assert mobile_entity.get_latitude() == 20.0
    assert mobile_entity.get_longitude() == 10.0
