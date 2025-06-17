import pytest
from unittest.mock import MagicMock, patch
from custom.actions.action_move_to import ActionMoveTo


@pytest.fixture
def mock_entities():
    map_entity = MagicMock()
    map_entity2 = MagicMock()

    geom1 = MagicMock()
    geom2 = MagicMock()
    point1 = MagicMock()
    point2 = MagicMock()

    map_entity.feature.geometry.return_value = geom1
    map_entity2.feature.geometry.return_value = geom2

    geom1.centroid.return_value = geom1
    geom2.centroid.return_value = geom2

    geom1.asPoint.return_value = point1
    geom2.asPoint.return_value = point2

    point1.x.return_value = 1.0
    point1.y.return_value = 2.0
    point2.x.return_value = 3.0
    point2.y.return_value = 4.0

    map_entity.altitude = 10
    map_entity2.altitude = 20

    return map_entity, map_entity2


@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_current_tick", return_value=2)
@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_instance")
@patch("custom.utils.utils.Utils.destination_point", return_value=(5.0, 6.0))
@patch("custom.utils.utils.Utils.calculate_azimuth", return_value=123.0)
@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_map_entity")
def test_execute_success(
    mock_get_map_entity,
    mock_azimuth,
    mock_dest_point,
    mock_get_instance,
    mock_get_current_tick,
    mock_entities
):
    map_entity, map_entity2 = mock_entities
    mock_get_map_entity.side_effect = [map_entity, map_entity2]

    mock_log = MagicMock()
    mock_get_instance.return_value = mock_log

    action = ActionMoveTo(1, 5, 100, 200, distance=100)

    result = action.execute()

    assert result is True
    map_entity.move_to.assert_called_once()
    mock_log.log_trace.assert_called_once_with(map_entity, map_entity.feature.geometry().asPoint())
    mock_azimuth.assert_called_once()
    mock_dest_point.assert_called_once()


@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_map_entity", side_effect=[None, MagicMock()])
def test_execute_failure_entity_missing(mock_get_map_entity):
    action = ActionMoveTo(1, 5, 100, 200)
    result = action.execute()
    assert result is False


@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_current_tick", return_value=10)
def test_get_next_geometry_final_position(mock_get_current_tick):
    action = ActionMoveTo(1, 5, 100, 200)
    action.lat_from = 0.0
    action.lon_from = 0.0
    action.alti_from = 0.0
    action.lat_to = 10.0
    action.lon_to = 10.0
    action.alti_to = 100.0

    lat, lon, alti = action.get_next_geometry()

    assert lat == 10.0
    assert lon == 10.0
    assert alti == 100.0


@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_current_tick", return_value=3)
def test_get_next_geometry_interpolation(mock_get_current_tick):
    action = ActionMoveTo(1, 5, 100, 200)
    action.lat_from = 0.0
    action.lon_from = 0.0
    action.alti_from = 0.0
    action.lat_to = 10.0
    action.lon_to = 10.0
    action.alti_to = 100.0

    lat, lon, alti = action.get_next_geometry()

    # Tick 3 dans un intervalle 1-5 → ratio = 0.5
    assert pytest.approx(lat) == 5.0
    assert pytest.approx(lon) == 5.0
    assert pytest.approx(alti) == 50.0
