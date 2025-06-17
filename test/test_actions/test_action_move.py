import math
from unittest.mock import MagicMock, patch
import pytest
from custom.actions.action_move import ActionMove

@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_map_entity")
@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_current_tick")
@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_instance")
def test_execute_success(mock_get_instance, mock_get_current_tick, mock_get_map_entity):
    mock_map_entity = MagicMock()
    mock_feature = MagicMock()
    mock_geometry = MagicMock()
    mock_point = MagicMock()

    mock_map_entity.feature = mock_feature
    mock_feature.geometry.return_value = mock_geometry
    mock_geometry.asPoint.return_value = mock_point
    mock_geometry.centroid.return_value = mock_geometry
    mock_point.x.return_value = 1.0
    mock_point.y.return_value = 2.0
    mock_map_entity.altitude = 100.0

    mock_get_map_entity.return_value = mock_map_entity
    mock_get_current_tick.return_value = 3
    mock_layer_instance = MagicMock()
    mock_get_instance.return_value = mock_layer_instance

    action = ActionMove(
        start_at=1,
        end_at=5,
        entity_id=42,
        lat_from=None,
        lon_from=None,
        alti_from=None,
        lat_to=10.0,
        lon_to=20.0,
        alti_to=200.0,
        text="Déplacement OK"
    )

    result = action.execute()

    assert result is True
    assert mock_geometry.asPoint.call_count == 2
    mock_map_entity.move_to.assert_called_once()
    mock_layer_instance.log_trace.assert_called_once_with(mock_map_entity, mock_point)

@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_map_entity")
def test_execute_failure_entity_none(mock_get_map_entity):
    # Pas d'entité trouvée
    mock_get_map_entity.return_value = None

    action = ActionMove(1, 5, 42, None, None, None, 10.0, 20.0, 200.0)
    result = action.execute()
    assert result is False

@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_current_tick")
def test_get_next_geometry_various_cases(mock_get_current_tick):
    # Setup action avec coordonnées de départ/arrivée
    action = ActionMove(1, 5, 42, 2.0, 3.0, 100.0, 10.0, 20.0, 200.0)

    # Cas : tick avant start => retourne coordonnées départ
    mock_get_current_tick.return_value = 0
    lat, lon, alti = action.get_next_geometry(MagicMock())
    assert lat == 2.0 and lon == 3.0 and alti == 100.0

    # Cas : tick == start => coordonnées départ
    mock_get_current_tick.return_value = 1
    lat, lon, alti = action.get_next_geometry(MagicMock())
    assert lat == 2.0 and lon == 3.0 and alti == 100.0

    # Cas : tick au milieu => interpolation
    mock_get_current_tick.return_value = 3
    lat, lon, alti = action.get_next_geometry(MagicMock())
    ratio = (3 - 1) / (5 - 1)
    expected_lat = 2.0 + (10.0 - 2.0) * ratio
    expected_lon = 3.0 + (20.0 - 3.0) * ratio
    expected_alti = 100.0 + (200.0 - 100.0) * ratio
    assert math.isclose(lat, expected_lat, rel_tol=1e-6)
    assert math.isclose(lon, expected_lon, rel_tol=1e-6)
    assert math.isclose(alti, expected_alti, rel_tol=1e-6)

    # Cas : tick == end => coordonnées fin
    mock_get_current_tick.return_value = 5
    lat, lon, alti = action.get_next_geometry(MagicMock())
    assert lat == 10.0 and lon == 20.0 and alti == 200.0

    # Cas : tick après end => coordonnées fin
    mock_get_current_tick.return_value = 10
    lat, lon, alti = action.get_next_geometry(MagicMock())
    assert lat == 10.0 and lon == 20.0 and alti == 200.0

@pytest.mark.parametrize("lat_from, lon_from, alti_from, alti_to", [
    (None, None, None, None),
    (None, None, 50.0, None),
    (None, None, None, 60.0),
])
@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_current_tick", return_value=2)
def test_get_next_geometry_handles_none_values(mock_get_current_tick, lat_from, lon_from, alti_from, alti_to):
    mock_map_entity = MagicMock()
    mock_geometry = MagicMock()
    mock_point = MagicMock()

    mock_map_entity.feature.geometry.return_value.centroid.return_value = mock_geometry
    mock_geometry.asPoint.return_value = mock_point
    mock_point.x.return_value = 1.0
    mock_point.y.return_value = 2.0
    mock_map_entity.altitude = 100.0

    action = ActionMove(1, 5, 42, lat_from, lon_from, alti_from, 10.0, 20.0, alti_to)

    lat, lon, alti = action.get_next_geometry(mock_map_entity)

    # Quand lat_from/lon_from None, ils doivent être remplacés par centroid
    assert lat is not None and lon is not None
    # Altitudes doivent être numériques
    assert isinstance(alti, float)
