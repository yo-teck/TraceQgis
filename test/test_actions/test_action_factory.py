import pytest

from custom.actions.action_factory import ActionFactory
from custom.actions.action_add_text import ActionAddText
from custom.actions.action_around import ActionAround
from custom.actions.action_background import ActionBackground
from custom.actions.action_change_size import ActionChangeSize
from custom.actions.action_highlight import ActionHighlight
from custom.actions.action_load import ActionLoad
from custom.actions.action_move import ActionMove
from custom.actions.action_move_to import ActionMoveTo
from custom.actions.action_opacity import ActionOpacity
from custom.actions.action_rotate import ActionRotate
from custom.actions.action_arrow import ActionArrow
from custom.actions.action_change_icon import ActionChangeIcon
from custom.actions.action_unload import ActionUnload


@pytest.mark.parametrize("data, expected_class", [
    (
        {"type": "move", "start_at": 1, "end_at": 2, "entity_id": 3,
         "lat_from": 4, "lon_from": 5, "alti_from": 6,
         "lat_to": 7, "lon_to": 8, "alti_to": 9, "text": "text"},
        ActionMove
    ),
    (
        {"type": "move_to", "start_at": 1, "end_at": 2, "entity_id": 3,
         "entity_id2": 4, "distance": 5, "text": "text"},
        ActionMoveTo
    ),
    (
        {"type": "text", "start_at": 1, "end_at": 2, "entity_id": 3,
         "text": "text"},
        ActionAddText
    ),
    (
        {"type": "arrow", "start_at": 1, "end_at": 2, "entity_id": 3,
         "entity_id2": 4, "text": "text"},
        ActionArrow
    ),
    (
        {"type": "around", "start_at": 1, "end_at": 2, "entity_id": 3,
         "entity_id2": 4, "distance": 5, "angle": 6, "text": "text"},
        ActionAround
    ),
    (
        {"type": "image", "start_at": 1, "end_at": 2, "entity_id": 3,
         "image": "img.png", "text": "text"},
        ActionChangeIcon
    ),
    (
        {"type": "background", "start_at": 1, "end_at": 2, "entity_id": 3,
         "image": "img.png", "text": "text"},
        ActionBackground
    ),
    (
        {"type": "size", "start_at": 1, "end_at": 2, "entity_id": 3,
         "size": 10, "text": "text"},
        ActionChangeSize
    ),
    (
        {"type": "opacity", "start_at": 1, "end_at": 2, "entity_id": 3,
         "opacity": 0.5, "text": "text"},
        ActionOpacity
    ),
    (
        {"type": "rotate", "start_at": 1, "end_at": 2, "entity_id": 3,
         "angle": 45, "text": "text"},
        ActionRotate
    ),
    (
        {"type": "highlight", "start_at": 1, "end_at": 2, "entity_id": 3,
         "color": "red", "text": "text"},
        ActionHighlight
    ),
    (
        {"type": "load", "start_at": 1, "end_at": 2, "entity_id": 3,
         "entity_id2": 4, "text": "text"},
        ActionLoad
    ),
    (
        {"type": "unload", "start_at": 1, "end_at": 2, "entity_id": 3,
         "entity_id2": 4, "text": "text"},
        ActionUnload
    ),
])
def test_action_factory_returns_correct_instance(data, expected_class):
    action = ActionFactory.action_from_dict(data)
    assert isinstance(action, expected_class)

def test_action_factory_raises_on_unknown_type():
    with pytest.raises(ValueError, match="Action inconnue"):
        ActionFactory.action_from_dict({"type": "unknown"})

def test_action_factory_raises_parametre():
    with pytest.raises(Exception, match="Paramètre invalide"):
        ActionFactory.action_from_dict({"type": "unload", "start_at": None, "end_at": 2, "entity_id": 3,
         "entity_id2": 4, "text": "text"})

def test_action_factory_raises_tick():
    with pytest.raises(Exception, match="start_at > end_at"):
        ActionFactory.action_from_dict({"type": "unload", "start_at": 10, "end_at": 2, "entity_id": 3,
         "entity_id2": 4, "text": "text"})
