import pytest
from unittest.mock import MagicMock, patch

from custom.actions.action import Action


# Sous-classe concrète pour pouvoir instancier Action
class DummyAction(Action):
    def execute(self):
        return True


def test_init_valid_params():
    action = DummyAction(1, 5, 42, "hello")
    assert action.start_at == 1
    assert action.end_at == 5
    assert action.entity_id == 42
    assert action.text == "hello"


@pytest.mark.parametrize("start_at, end_at, entity_id", [
    (None, 5, 1),
    (1, None, 1),
    (1, 5, None)
])
def test_init_invalid_params_none(start_at, end_at, entity_id):
    with pytest.raises(Exception, match="Paramètre invalide"):
        DummyAction(start_at, end_at, entity_id)


def test_init_start_greater_than_end():
    with pytest.raises(Exception, match="start_at > end_at"):
        DummyAction(10, 5, 1)


@pytest.mark.parametrize("tick, expected", [
    (1, True),
    (5, True),
    (3, True),
    (0, False),
    (6, False),
])
def test_is_active_at(tick, expected):
    action = DummyAction(1, 5, 1)
    assert action.is_active_at(tick) == expected


def test_add_text_with_text():
    action = DummyAction(1, 5, 1, text="test")
    map_entity = MagicMock()
    action.add_text(map_entity)
    map_entity.append_text.assert_called_once_with("test")


def test_add_text_without_text():
    action = DummyAction(1, 5, 1, text="")
    map_entity = MagicMock()
    action.add_text(map_entity)
    map_entity.append_text.assert_not_called()


@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_current_tick", return_value=123)
def test_str_includes_expected_parts(mock_get_tick):
    action = DummyAction(1, 5, 42, "test")
    result = str(action)
    assert "DummyAction:" in result
    assert "current_tick=123" in result
    assert "start_at=1" in result
    assert "end_at=5" in result
    assert "entity_id=42" in result
    assert "text=test" in result
