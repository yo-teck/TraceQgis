import pytest
from unittest.mock import patch, MagicMock
from custom.actions.action_change_size import ActionChangeSize

@pytest.fixture
def action():
    return ActionChangeSize(10, 20, 505, 15.0, text="resize")

@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_map_entity")
@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_current_tick")
@patch("custom.utils.utils.Utils.get_intermediare_value")
def test_execute_success_start_tick(mock_get_intermediare_value, mock_get_current_tick, mock_get_map_entity, action):
    mock_entity = MagicMock()
    mock_entity.id = 505
    mock_entity.size = 8.0  # taille initiale pour start_at

    mock_get_map_entity.return_value = mock_entity
    mock_get_current_tick.return_value = 10  # start_at
    mock_get_intermediare_value.return_value = 12.5

    result = action.execute()

    assert result is True
    assert action.start_size == 8.0
    mock_get_intermediare_value.assert_called_once_with(10, 20, 10, 8.0, 15.0)
    mock_entity.set_size.assert_called_once_with(12.5)

@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_map_entity")
@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_current_tick")
@patch("custom.utils.utils.Utils.get_intermediare_value")
def test_execute_success_intermediate_tick(mock_get_intermediare_value, mock_get_current_tick, mock_get_map_entity, action):
    mock_entity = MagicMock()
    mock_entity.id = 505
    mock_entity.size = 8.0

    mock_get_map_entity.return_value = mock_entity
    mock_get_current_tick.return_value = 15
    mock_get_intermediare_value.return_value = 13.0

    # simulate that start_size has been set previously
    action.start_size = 10.0

    result = action.execute()

    assert result is True
    mock_get_intermediare_value.assert_called_once_with(10, 20, 15, 10.0, 15.0)
    mock_entity.set_size.assert_called_once_with(13.0)

@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_map_entity")
def test_execute_failure_no_entity(mock_get_map_entity, action):
    mock_get_map_entity.return_value = None

    result = action.execute()

    assert result is False
    mock_get_map_entity.assert_called_once_with(505)
