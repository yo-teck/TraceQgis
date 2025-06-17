import pytest
from unittest.mock import MagicMock, patch
from custom.actions.action_rotate import ActionRotate


@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_current_tick", return_value=3)
@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_instance")
@patch("custom.utils.utils.Utils.get_intermediare_value", return_value=45.0)
@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_map_entity")
def test_execute_success(
    mock_get_map_entity,
    mock_get_intermediare_value,
    mock_get_instance,
    mock_get_current_tick
):
    # Mock de l'entité
    map_entity = MagicMock()
    map_entity.angle = 30.0
    mock_get_map_entity.return_value = map_entity

    mock_get_instance.return_value = MagicMock()

    action = ActionRotate(1, 5, 200, 90.0)

    result = action.execute()

    assert result is True
    mock_get_map_entity.assert_called_once_with(200)
    mock_get_intermediare_value.assert_called_once_with(1, 5, 3, action.start_angle, action.end_angle)
    map_entity.set_angle.assert_called_once_with(45.0)


@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_map_entity", return_value=None)
def test_execute_failure_entity_missing(mock_get_map_entity):
    action = ActionRotate(1, 5, 200, 90.0)
    result = action.execute()
    assert result is False


@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_current_tick", return_value=1)
@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_map_entity")
def test_execute_updates_start_angle(mock_get_map_entity, mock_get_current_tick):
    map_entity = MagicMock()
    map_entity.angle = 15.0
    mock_get_map_entity.return_value = map_entity

    action = ActionRotate(1, 5, 200, 60.0)
    action.execute()

    assert action.start_angle == 15.0
