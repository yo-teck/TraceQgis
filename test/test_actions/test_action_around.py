import pytest
from unittest.mock import patch, MagicMock
from custom.actions.action_around import ActionAround

@pytest.fixture
def action():
    return ActionAround(1, 10, 101, 202, distance=50, angle=90, text="autour")

@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_map_entity")
@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_current_tick", return_value=5)
@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_instance")
@patch("custom.utils.utils.Utils.destination_point", return_value=(48.0, 2.0))
@patch("custom.utils.utils.Utils.get_intermediare_value", return_value=45.0)
@patch("custom.utils.utils.Utils.calculate_azimuth", return_value=30.0)
def test_execute_success(
    mock_calc_azimuth,
    mock_get_inter_value,
    mock_dest_point,
    mock_get_instance,
    mock_get_tick,
    mock_get_map_entity,
    action
):
    # Préparation des entités simulées
    mock_entity = MagicMock()
    mock_entity.id = 101
    mock_entity.altitude = 100
    mock_entity.feature.geometry().centroid().asPoint.side_effect = [
        MagicMock(x=lambda: 1.0, y=lambda: 2.0),
        MagicMock(x=lambda: 3.0, y=lambda: 4.0)
    ]
    mock_entity.feature.geometry().asPoint.return_value = MagicMock()
    mock_entity2 = MagicMock()
    mock_entity2.id = 202
    mock_entity2.feature.geometry().centroid().asPoint.return_value = MagicMock(x=lambda: 3.0, y=lambda: 4.0)

    mock_get_map_entity.side_effect = [mock_entity, mock_entity2]

    mock_logger = MagicMock()
    mock_get_instance.return_value = mock_logger

    # Exécution
    result = action.execute()

    # Vérifications
    assert result is True
    mock_get_map_entity.assert_any_call(101)
    mock_get_map_entity.assert_any_call(202)
    mock_calc_azimuth.assert_called_once()
    mock_get_inter_value.assert_called_once()
    mock_dest_point.assert_called_once()
    mock_entity.move_to.assert_called_once_with(48.0, 2.0, 100)
    mock_logger.log_trace.assert_called_once_with(mock_entity, mock_entity.feature.geometry().asPoint.return_value)

@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_map_entity")
def test_execute_failure_entity_not_found(mock_get_map_entity, action):
    mock_get_map_entity.side_effect = [None, None]

    result = action.execute()

    assert result is False
    mock_get_map_entity.assert_any_call(101)
    mock_get_map_entity.assert_any_call(202)

@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_map_entity")
def test_execute_failure_same_entity(mock_get_map_entity, action):
    mock_entity = MagicMock()
    mock_entity.id = 101
    mock_get_map_entity.side_effect = [mock_entity, mock_entity]

    result = action.execute()

    assert result is False
    mock_get_map_entity.assert_any_call(101)
    mock_get_map_entity.assert_any_call(202)
