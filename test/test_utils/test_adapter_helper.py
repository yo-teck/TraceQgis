import sys
from typing import Tuple
from unittest.mock import MagicMock, patch

from custom.business.dm_carto_configuration_model import DmCartoConfigurationModel
from custom.business.map_entity import MapEntity
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

CONFIG_DATA = {
    "object_types": {
        "truck": {"sprite": "default_sprite.png"},
        "package": {"sprite": "default_sprite.png"},
        "location": {"sprite": "default_sprite.png"},
        "city": {"sprite": "default_sprite.png"}
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
                    "name": "load",  # ActionType.LOAD
                    "start_at": 0,
                    "end_at": DEFAULT_ANIMATION_DURATION,
                    "var_object_who_load": "?truck",
                    "var_object_loaded": "?pkg",
                    "text": "Chargement"
                }
            ]
        },
        "UNLOAD-TRUCK": {
            "duration": DEFAULT_ANIMATION_DURATION,
            "animations": [
                {
                    "name": "unload",  # ActionType.UNLOAD
                    "start_at": 0,
                    "end_at": DEFAULT_ANIMATION_DURATION,
                    "var_object_who_unload": "?truck",
                    "var_object_unloaded": "?pkg",
                    "text": "Déchargement"
                }
            ]
        },
        "DRIVE-TRUCK": {
            "duration": DEFAULT_ANIMATION_DURATION,
            "animations": [
                {
                    "name": "move",  # ActionType.MOVE
                    "start_at": 0,
                    "end_at": DEFAULT_ANIMATION_DURATION,
                    "entity_id": "?truck",
                    "lat_from": 1.0,
                    "lon_from": 1.0,
                    "alti_from": 0.0,
                    "lat_to": 2.0,
                    "lon_to": 2.0,
                    "alti_to": 0.0,
                    "text": "Déplacement"
                }
            ]
        }
    },
    "fixed_position": [
        {"var": "pos1", "x": 1.0, "y": 1.0},
        {"var": "pos2", "x": 2.0, "y": 2.0}
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

class MockMapEntity:
    def __init__(self, id, name, url_icon, lat, lon, *args, **kwargs):
        self.id = id
        self.name = name
        self.url_icon = url_icon
        self.latitude = lat
        self.longitude = lon
    def get_id(self): return self.id
    def get_latitude(self): return self.latitude
    def get_longitude(self): return self.longitude


@patch("custom.utils.adapter_helper.MapEntity", new=MockMapEntity)
def test_domain_problem_to_map_entity(tmp_path):
    parser = create_parser_for_test(tmp_path)

    config = DmCartoConfigurationModel()
    config.load_from_parsed(CONFIG_DATA)
    parser.save_configuration(config)

    entities = AdapterHelper.domain_problem_to_map_entity(parser)

    ids = [e.get_id() for e in entities]
    assert "tru1" in ids
    assert "obj1" in ids
    assert "pos1" in ids


@patch("custom.utils.adapter_helper.MapEntity", new=MockMapEntity)
def test_add_predicat_position_to_map_entity_list(tmp_path):
    parser = create_parser_for_test(tmp_path)

    config_data = {
        "object_types": {
            "truck": {"sprite": "default_sprite.png"},
            "package": {"sprite": "default_sprite.png"},
            "location": {"sprite": "default_sprite.png"},
            "city": {"sprite": "default_sprite.png"}
        },
        "init_predicats": {
            "at": {
                "type": PredicatMapping.POSITION.value,
                "mobile_var": "?obj",
                "fixed_var": "?loc"
            }
        },
        "actions": {
            "TEST-ACTION": {
                "duration": 1,
                "animations": [{
                    "name": "text",
                    "start_at": 0,
                    "end_at": 1,
                    "var_object": "?fake",
                    "text": "test"
                }]
            }
        },
        "fixed_position": [
            {"var": "pos1", "x": 1.0, "y": 1.0},
            {"var": "pos2", "x": 2.0, "y": 2.0}
        ]
    }

    config = DmCartoConfigurationModel()
    config.load_from_parsed(config_data)
    parser.save_configuration(config)

    # Utilise uniquement MockMapEntity ici
    fixed_entities = [
        MockMapEntity("pos1", "pos1", "default_sprite.png", 1.0, 1.0),
        MockMapEntity("pos2", "pos2", "default_sprite.png", 2.0, 2.0),
    ]

    predicat_key = "at"
    predicat_value = config.init_predicats[predicat_key]

    AdapterHelper.add_predicat_position_to_map_entity_list(predicat_key, predicat_value, fixed_entities, parser)

    ids = [e.get_id() for e in fixed_entities]
    assert "tru1" in ids
    assert "obj1" in ids

def test_extract_var_from_action():
    assert AdapterHelper.extract_var_from_action(("?x", "object")) == "?x"

def test_adapt_predicats_reversed_order():
    predicats = {
        "at": [
            ("?loc", "location"),
            ("?obj", "object")
        ]
    }
    result = AdapterHelper.adapt_predicats(predicats)
    assert result == {
        "at": {
            "type": PredicatMapping.POSITION.value,
            "mobile_var": "?loc",  # oui, ordre respecté
            "fixed_var": "?obj",
        }
    }

import pytest

@patch("custom.utils.adapter_helper.MapEntity", new=MockMapEntity)
def test_add_predicat_position_missing_fixed_entity(tmp_path):
    parser = create_parser_for_test(tmp_path)

    config_data = {
        "object_types": {
            "truck": {"sprite": "default_sprite.png"},
            "package": {"sprite": "default_sprite.png"},
            "location": {"sprite": "default_sprite.png"},
            "city": {"sprite": "default_sprite.png"}
        },
        "init_predicats": {
            "at": {
                "type": PredicatMapping.POSITION.value,
                "mobile_var": "?obj",
                "fixed_var": "?loc"
            }
        },
        "actions": {
            "TEST-ACTION": {
                "duration": 1,
                "animations": [{
                    "name": "text",
                    "start_at": 0,
                    "end_at": 1,
                    "var_object": "?fake",
                    "text": "test"
                }]
            }
        },
        "fixed_position": []  # <--- Aucun point fixe volontairement
    }
    config = DmCartoConfigurationModel()
    config.load_from_parsed(config_data)
    parser.save_configuration(config)

    fixed_entities = []  # aucun pos1 / pos2

    with pytest.raises(ValueError, match="Pas de variable trouvé à ce nom"):
        AdapterHelper.add_predicat_position_to_map_entity_list("at", config.init_predicats["at"], fixed_entities, parser)

