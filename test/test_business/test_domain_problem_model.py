import pytest
from test.common.pddl_constants import create_parser_for_test


def test_get_objects(tmp_path):
    parser = create_parser_for_test(tmp_path)
    objs = parser.get_objects()

    assert objs["tru1"] == "truck"
    assert objs["obj1"] == "package"
    assert objs["pos2"] == "location"


def test_get_initial_state(tmp_path):
    parser = create_parser_for_test(tmp_path)
    init = set(parser.get_initial_state())
    assert ('at', 'tru1', 'pos1') in init
    assert ('at', 'obj1', 'pos1') in init


def test_get_goal_state(tmp_path):
    parser = create_parser_for_test(tmp_path)
    goal = set(parser.get_goal_state())
    assert ('at', 'obj1', 'pos2') in goal


def test_get_actions_and_parameters(tmp_path):
    parser = create_parser_for_test(tmp_path)

    actions = parser.get_actions()
    assert set(actions) == {"LOAD-TRUCK", "UNLOAD-TRUCK", "DRIVE-TRUCK"}

    action_params = parser.get_action_parameters()
    assert action_params["LOAD-TRUCK"] == [
        ("?pkg", "package"), ("?truck", "truck"), ("?loc", "place")
    ]
    assert action_params["DRIVE-TRUCK"] == [
        ("?truck", "truck"), ("?from", "place"), ("?to", "place"), ("?city", "city")
    ]


def test_get_object_type(tmp_path):
    parser = create_parser_for_test(tmp_path)
    assert parser.get_object_type("tru1") == "truck"
    assert parser.get_object_type("obj1") == "package"
    assert parser.get_object_type("unknown") is None


def test_execution_sequence_loading(tmp_path):
    parser = create_parser_for_test(tmp_path)

    expected = [
        {"action": "LOAD-TRUCK", "args": ["obj1", "tru1", "pos1"]},
        {"action": "DRIVE-TRUCK", "args": ["tru1", "pos1", "pos2", "cit1"]},
        {"action": "UNLOAD-TRUCK", "args": ["obj1", "tru1", "pos2"]}
    ]
    assert parser.get_execution_sequence() == expected


def test_get_predicates(tmp_path):
    parser = create_parser_for_test(tmp_path)
    preds = parser.get_predicates()

    assert "at" in preds
    assert preds["at"] == [('?obj', 'physobj'), ('?loc', 'place')]

    assert "in-city" in preds
    assert preds["in-city"] == [('?loc', 'place'), ('?city', 'city')]
