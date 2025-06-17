import pytest
from unittest.mock import patch, MagicMock
from custom.actions.action_highlight import ActionHighlight

@pytest.mark.parametrize("color,expected", [
    ("yellow", "yellow"),
    ("green", "green"),
    ("blue", "blue"),
    ("red", "red"),
    ("invalid", "yellow"),  # test de fallback
])
def test_init_color_validation(color, expected):
    action = ActionHighlight(1, 5, 101, color=color)
    assert action.highlight == expected

@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_map_entity")
@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_current_tick")
def test_execute_success_start_or_end_tick(mock_get_current_tick, mock_get_map_entity):
    mock_entity = MagicMock()
    mock_entity.id = 101

    mock_get_map_entity.return_value = mock_entity
    mock_get_current_tick.return_value = 1  # start_at tick

    action = ActionHighlight(1, 5, 101, color="green")
    result = action.execute()

    assert result is True
    mock_entity.set_highlight.assert_called_once_with("green", True)

@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_map_entity")
@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_current_tick")
def test_execute_success_other_tick(mock_get_current_tick, mock_get_map_entity):
    mock_entity = MagicMock()
    mock_entity.id = 101

    mock_get_map_entity.return_value = mock_entity
    mock_get_current_tick.return_value = 3  # tick entre start_at et end_at

    action = ActionHighlight(1, 5, 101, color="blue")
    result = action.execute()

    assert result is True
    mock_entity.set_highlight.assert_called_once_with("blue", False)

@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_map_entity")
def test_execute_failure_no_entity(mock_get_map_entity):
    mock_get_map_entity.return_value = None

    action = ActionHighlight(1, 5, 101, color="red")
    result = action.execute()

    assert result is False
    mock_get_map_entity.assert_called_once_with(101)
