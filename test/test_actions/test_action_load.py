import pytest
from unittest.mock import patch, MagicMock
from custom.actions.action_load import ActionLoad


@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_map_entity")
@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.is_loaded")
@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_current_tick")
@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.static_load_entity")
def test_execute(mock_static_load, mock_get_current_tick, mock_is_loaded, mock_get_map_entity):
    mock_entity1 = MagicMock()
    mock_entity2 = MagicMock()

    def get_map_entity_side_effect(entity_id):
        if entity_id == 101:
            return mock_entity1
        elif entity_id == 202:
            return mock_entity2
        return None

    mock_get_map_entity.side_effect = get_map_entity_side_effect
    mock_is_loaded.side_effect = [True, True]

    # Tick avant la fin, static_load_entity ne doit pas être appelé
    mock_get_current_tick.return_value = 4
    action = ActionLoad(1, 5, 101, 202, "texte")
    result = action.execute()
    assert result is True
    mock_static_load.assert_not_called()
    mock_entity2.set_need_update_label.assert_not_called()

    # Tick à la fin, static_load_entity doit être appelé
    mock_get_current_tick.return_value = 5
    result = action.execute()
    assert result is True
    mock_static_load.assert_called_once_with(mock_entity1, mock_entity2)
    mock_entity2.set_need_update_label.assert_called_once_with(True)



@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_map_entity")
@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.is_loaded")
def test_execute_fail_if_entities_missing_and_not_loaded(mock_is_loaded, mock_get_map_entity):
    # Entités absentes
    mock_get_map_entity.side_effect = [None, None]
    # Entités non chargées
    mock_is_loaded.side_effect = [False, False]

    action = ActionLoad(1, 5, 101, 202, "texte")
    result = action.execute()
    assert result is False
