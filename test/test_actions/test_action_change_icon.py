import pytest
from unittest.mock import patch, MagicMock
from custom.actions.action_change_icon import ActionChangeIcon

@pytest.fixture
def action():
    return ActionChangeIcon(10, 20, 404, "icons/my_icon.png", text="icone")

@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_map_entity")
@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_current_tick")
def test_execute_success_matching_tick(mock_get_current_tick, mock_get_map_entity, action):
    # Mocks
    mock_entity = MagicMock()
    mock_entity.id = 404

    mock_get_map_entity.return_value = mock_entity
    mock_get_current_tick.return_value = 10  # start_at

    result = action.execute()

    assert result is True
    mock_get_map_entity.assert_called_once_with(404)
    mock_get_current_tick.assert_called_once()
    mock_entity.set_url_icon.assert_called_once_with("icons/my_icon.png", True)

@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_map_entity")
@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_current_tick")
def test_execute_success_non_matching_tick(mock_get_current_tick, mock_get_map_entity, action):
    mock_entity = MagicMock()
    mock_entity.id = 404

    mock_get_map_entity.return_value = mock_entity
    mock_get_current_tick.return_value = 15  # Entre start_at et end_at, pas aux bornes

    result = action.execute()

    assert result is True
    mock_entity.set_url_icon.assert_called_once_with("icons/my_icon.png", False)

@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_map_entity")
def test_execute_failure_no_entity(mock_get_map_entity, action):
    mock_get_map_entity.return_value = None

    result = action.execute()

    assert result is False
    mock_get_map_entity.assert_called_once_with(404)
