import pytest
from unittest.mock import patch, MagicMock
from custom.actions.action_add_text import ActionAddText

@pytest.fixture
def action():
    return ActionAddText(1, 10, 42, "Mon texte")

@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_map_entity")
def test_execute_success(mock_get_map_entity, action):
    # Arrange : on simule un map_entity avec une méthode append_text
    fake_map_entity = MagicMock()
    mock_get_map_entity.return_value = fake_map_entity

    # Act
    result = action.execute()

    # Assert
    mock_get_map_entity.assert_called_once_with(42)
    fake_map_entity.append_text.assert_called_once_with("Mon texte")
    assert result is True

@patch("custom.business.layer_trace_qgis.LayerTraceQGIS.get_map_entity")
def test_execute_failure_when_no_entity(mock_get_map_entity, action):
    # Arrange : aucun map_entity trouvé
    mock_get_map_entity.return_value = None

    # Act
    result = action.execute()

    # Assert
    mock_get_map_entity.assert_called_once_with(42)
    assert result is False