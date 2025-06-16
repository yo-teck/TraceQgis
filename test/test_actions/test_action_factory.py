import pytest

from custom.actions.action_arrow import ActionArrow
from custom.actions.action_change_icon import ActionChangeIcon
from custom.actions.action_factory import ActionFactory
from custom.actions.action_move import ActionMove


def test_action_move() -> None:
    data = {
        "type": "move",
        "start_at": 0,
        "end_at": 10,
        "entity_id": 1,
        "lat_from": 45.0,
        "lon_from": 5.0,
        "lat_to": 46.0,
        "lon_to": 6.0
    }
    action = ActionFactory.action_from_dict(data)
    assert isinstance(action, ActionMove)
    assert action.entity_id == 1
    assert action.lat_from == 45.0
    assert action.lat_to == 46.0

def test_action_communicate() -> None:
    data = {
        "type": "communicate",
        "start_at": 0,
        "end_at": 5,
        "entity_id": 1,
        "entity_id2": 2
    }
    action = ActionFactory.action_from_dict(data)
    assert isinstance(action, ActionArrow)
    assert action.entity_id == 1
    assert action.entity_id2 == 2

def test_action_change_icon() -> None:
    data = {
        "type": "image",
        "start_at": 0,
        "end_at": 5,
        "entity_id": 3,
        "url_icon": "http://example.com/icon.png"
    }
    action = ActionFactory.action_from_dict(data)
    assert isinstance(action, ActionChangeIcon)
    assert action.entity_id == 3
    assert action.url_icon == "http://example.com/icon.png"

def test_action_type_inconnu() -> None:
    data = {
        "type": "explode",
        "start_at": 0,
        "end_at": 5,
        "entity_id": 99
    }
    with pytest.raises(ValueError, match="Action inconnue"):
        ActionFactory.action_from_dict(data)

def test_action_sans_type() -> None:
    data = {
        "start_at": 0,
        "end_at": 5,
        "entity_id": 1
    }
    with pytest.raises(ValueError, match="Action inconnue"):
        ActionFactory.action_from_dict(data)
