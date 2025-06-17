import pytest
from pytest_mock import MockerFixture
from unittest.mock import MagicMock, patch
from custom.actions.action_opacity import ActionOpacity


@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_current_tick", return_value=3)
@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_instance")
@patch("custom.utils.utils.Utils.get_intermediare_value", return_value=0.5)
@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_map_entity")
def test_execute_success(
    mock_get_map_entity,
    mock_get_intermediare_value,
    mock_get_instance,
    mock_get_current_tick,
    mocker: MockerFixture
):
    # Prépare un mock d'entité
    map_entity = MagicMock()
    map_entity.opacity = 0.8
    mock_get_map_entity.return_value = map_entity

    mock_get_instance.return_value = MagicMock()

    action = ActionOpacity(1, 5, 100, 1.0, 'test')
    mock_add_text = mocker.patch.object(action, "add_text")

    result = action.execute()

    assert result is True
    mock_get_map_entity.assert_called_once_with(100)
    mock_get_intermediare_value.assert_called_once_with(1, 5, 3, action.start_opacity, action.end_opacity)
    map_entity.set_opacity.assert_called_once_with(0.5)
    mock_add_text.assert_called_once_with(map_entity)


@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_map_entity", return_value=None)
def test_execute_failure_entity_missing(mock_get_map_entity):
    action = ActionOpacity(1, 5, 100, 1.0)
    result = action.execute()
    assert result is False


@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_current_tick", return_value=1)
@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_map_entity")
def test_execute_updates_start_opacity(mock_get_map_entity, mock_get_current_tick):
    map_entity = MagicMock()
    map_entity.opacity = 0.3
    mock_get_map_entity.return_value = map_entity

    action = ActionOpacity(1, 5, 100, 0.7)
    action.execute()

    # Vérifie que la start_opacity a bien été mise à jour
    assert action.start_opacity == 0.3
