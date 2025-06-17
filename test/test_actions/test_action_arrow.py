import pytest
from unittest.mock import patch, MagicMock
from custom.actions.action_arrow import ActionArrow

@pytest.fixture
def action():
    return ActionArrow(1, 10, 101, 202, text="flèche")

@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_map_entity")
@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_instance")
def test_execute_success(mock_get_instance, mock_get_map_entity, action):
    # Préparation des entités simulées
    mock_entity1 = MagicMock()
    mock_entity1.id = 101
    mock_entity2 = MagicMock()
    mock_entity2.id = 202

    mock_get_map_entity.side_effect = [mock_entity1, mock_entity2]

    mock_instance = MagicMock()
    mock_get_instance.return_value = mock_instance

    # Exécution
    result = action.execute()

    # Vérifications
    assert result is True
    mock_get_map_entity.assert_any_call(101)
    mock_get_map_entity.assert_any_call(202)
    mock_instance.add_line.assert_called_once_with(101, 202)
    mock_entity1.add_text.assert_not_called()  # add_text est sur Action, pas l'entité
    # Vérifie bien l'appel de la méthode d'instance Action
    # (tu peux adapter si add_text est mockable / observable)

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
