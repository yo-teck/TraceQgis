import pytest
from unittest.mock import MagicMock, patch
from custom.actions.action_unload import ActionUnload

@patch("custom.business.layer_trace_qgis.iface")
@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_current_tick", return_value=5)
@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_instance")
@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.static_unload_entity")
@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.is_loaded", return_value=True)
@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_map_entity")
def test_execute_success(
    mock_get_map_entity,
    mock_is_loaded,
    mock_static_unload,
    mock_get_instance,
    mock_get_current_tick,
    mock_iface
):
    mock_canvas = MagicMock()
    mock_iface.mapCanvas.return_value = mock_canvas
    mock_canvas.extentsChanged.connect = MagicMock()

    map_entity = MagicMock()
    map_entity2 = MagicMock()
    mock_get_map_entity.side_effect = [map_entity, map_entity2]

    action = ActionUnload(1, 5, 100, 200, "test")

    result = action.execute()

    assert result is True
    map_entity2.move_to_entity.assert_called_once_with(map_entity)
    mock_static_unload.assert_called_once_with(map_entity, map_entity2)
    map_entity2.set_need_update_label.assert_called_once_with(True)

@patch("custom.business.layer_trace_qgis.iface")
@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.is_loaded", return_value=False)
@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_map_entity", return_value=None)
def test_execute_failure_missing_entities(mock_get_map_entity, mock_is_loaded, mock_iface):
    mock_canvas = MagicMock()
    mock_iface.mapCanvas.return_value = mock_canvas
    mock_canvas.extentsChanged.connect = MagicMock()

    action = ActionUnload(1, 5, 100, 200)
    result = action.execute()
    assert result is False

@patch("custom.business.layer_trace_qgis.iface")
@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_current_tick", return_value=3)
@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.is_loaded", return_value=True)
@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_map_entity")
def test_execute_no_unload_before_end(
    mock_get_map_entity,
    mock_is_loaded,
    mock_get_current_tick,
    mock_iface
):
    mock_canvas = MagicMock()
    mock_iface.mapCanvas.return_value = mock_canvas
    mock_canvas.extentsChanged.connect = MagicMock()

    map_entity = MagicMock()
    map_entity2 = MagicMock()
    mock_get_map_entity.side_effect = [map_entity, map_entity2]

    action = ActionUnload(1, 5, 100, 200, "test")

    result = action.execute()

    assert result is True
    map_entity2.move_to_entity.assert_not_called()
    map_entity2.set_need_update_label.assert_not_called()
