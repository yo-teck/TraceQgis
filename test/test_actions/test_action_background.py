import pytest
from unittest.mock import patch, MagicMock
from custom.actions.action_background import ActionBackground

@pytest.fixture
def action():
    return ActionBackground(5, 15, 303, "path/to/image.png", text="fond")

@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_map_entity")
@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_current_tick")
def test_execute_success(mock_get_current_tick, mock_get_map_entity, action):
    # Mock des retours
    mock_entity = MagicMock()
    mock_entity.id = 303

    mock_get_map_entity.return_value = mock_entity
    mock_get_current_tick.return_value = 5  # Cas où tick == start_at

    # Exécution
    result = action.execute()

    # Vérifications
    assert result is True
    mock_get_map_entity.assert_called_once_with(303)
    mock_get_current_tick.assert_called_once()
    mock_entity.set_background_image.assert_called_once_with("path/to/image.png", True)

@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_map_entity")
@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_current_tick")
def test_execute_success_with_non_matching_tick(mock_get_current_tick, mock_get_map_entity, action):
    mock_entity = MagicMock()
    mock_entity.id = 303

    mock_get_map_entity.return_value = mock_entity
    mock_get_current_tick.return_value = 8  # Cas où tick != start_at ou end_at

    result = action.execute()

    assert result is True
    mock_entity.set_background_image.assert_called_once_with("path/to/image.png", False)

@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_map_entity")
def test_execute_failure_no_entity(mock_get_map_entity, action):
    mock_get_map_entity.return_value = None

    result = action.execute()

    assert result is False
    mock_get_map_entity.assert_called_once_with(303)
