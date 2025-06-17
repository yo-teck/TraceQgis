# test_layer_trace_qgis.py

import pytest
from qgis.core import QgsFeature, QgsGeometry, QgsPointXY, QgsRendererCategory,QgsMarkerSymbol

from custom.business.layer_trace_qgis import LayerTraceQGIS


@pytest.fixture
def mock_map_entity(mocker):
    ent = mocker.MagicMock()
    ent.get_id.return_value = "e1"
    ent.get_name.return_value = "Name1"

    category = QgsRendererCategory("e1", QgsMarkerSymbol(), "Name1")
    ent.get_category.return_value = category  # Simuler QgsRendererCategory
    ent.get_need_refresh_category.return_value = False
    ent.get_need_update_label.return_value = False

    feature = QgsFeature()
    feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(1, 1)))
    ent.feature = feature

    ent.reset_icon = mocker.Mock()
    return ent

@pytest.fixture
def mock_map_entity2(mocker):
    ent = mocker.MagicMock()
    ent.get_id.return_value = "e2"
    ent.get_name.return_value = "Name2"

    category = QgsRendererCategory("e2", QgsMarkerSymbol(), "Name2")
    ent.get_category.return_value = category  # Simuler QgsRendererCategory
    ent.get_need_refresh_category.return_value = True
    ent.get_need_update_label.return_value = True

    feature = QgsFeature()
    feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(2, 2)))
    ent.feature = feature

    ent.reset_icon = mocker.Mock()
    return ent

def test_init_layer(mocker):
    mock_iface = mocker.patch("custom.business.layer_trace_qgis.iface")
    mock_iface.mapCanvas.return_value.extentsChanged.connect = mocker.Mock()

    instance = LayerTraceQGIS([], [])
    mock_project = mocker.patch("custom.business.layer_trace_qgis.QgsProject.instance")

    intance_project = mocker.MagicMock()
    root = mocker.MagicMock()

    mock_project.return_value = intance_project
    mock_project.return_value.layerTreeRoot.return_value = root


    root.findGroup.return_value = None

    instance.init_layer()

    root.addGroup.assert_called_with("Trace QGIS")
    assert intance_project.addMapLayer.call_count == 3

def test_reset_method(mocker, mock_map_entity, mock_map_entity2):
    mocker.patch("custom.business.layer_trace_qgis.iface")

    instance = LayerTraceQGIS([mock_map_entity], [])

    # Pré-remplir pour vérifier que tout est bien réinitialisé
    instance.interval = 500
    instance.focus = 99
    instance.tick = 999
    instance.lines = [[1, 2], [3, 4]]
    instance.entities_loaded = {"e1": ["e2"]}

    # On mocke les fonctions internes appelées
    m_set_map_entities = mocker.patch.object(instance, "set_map_entities")
    m_set_actions = mocker.patch.object(instance, "set_actions")
    m_start_timer = mocker.patch.object(instance, "start_timer")
    m_unload = mock_map_entity.unload

    instance.map_entities = {"e1": mock_map_entity, "e2": mock_map_entity2}

    instance.reset([mock_map_entity], ["action1", "action2"])

    assert instance.interval == 1000
    assert instance.focus == 0
    assert instance.tick == 0
    assert instance.lines == []
    assert instance.entities_loaded == {}

    # Vérifie les appels internes
    m_unload.assert_called_once()
    m_set_map_entities.assert_called_once_with([mock_map_entity])
    m_set_actions.assert_called_once_with(["action1", "action2"])
    m_start_timer.assert_called_once()

def test_set_map_entities(mocker, mock_map_entity, mock_map_entity2):
    mocker.patch("custom.business.layer_trace_qgis.iface")

    # Créer une instance
    instance = LayerTraceQGIS([], [])

    # Mock de la méthode apply_renderer
    apply_renderer_mock = mocker.patch.object(instance, "apply_renderer")
    apply_trace_renderer_mock = mocker.patch.object(instance, "apply_trace_renderer")

    # Mock de dataProvider().truncate() et addFeature()
    dp_mock = mocker.Mock()
    instance.layer = mocker.Mock()
    instance.layer.dataProvider.return_value = dp_mock

    dp_mock_2 = mocker.Mock()
    instance.layer_trace = mocker.Mock()
    instance.layer_trace.dataProvider.return_value = dp_mock_2

    signal_mock = mocker.Mock()
    instance.signal_entities_updated = signal_mock

    instance.set_map_entities([mock_map_entity, mock_map_entity2])

    # Vérifie que le truncate a bien été appelé
    dp_mock.truncate.assert_called_once()
    dp_mock_2.truncate.assert_called_once()

    # Vérifie que les features ont été ajoutées
    dp_mock.addFeature.assert_any_call(mock_map_entity.feature)
    dp_mock.addFeature.assert_any_call(mock_map_entity2.feature)

    # Vérifie que les entités sont bien dans le dictionnaire
    assert instance.map_entities == {
        mock_map_entity.get_id(): mock_map_entity,
        mock_map_entity2.get_id(): mock_map_entity2
    }

    # Vérifie que apply_renderer a été appelé
    apply_renderer_mock.assert_called_once()
    apply_trace_renderer_mock.assert_called_once()

    signal_mock.emit.assert_called_once_with([('e1', 'Name1'), ('e2', 'Name2')])

def test_set_map_entities_empty(mocker):
    mocker.patch("custom.business.layer_trace_qgis.iface")
    instance = LayerTraceQGIS([], [])
    instance.map_entities = {"some_id": "some_entity"}

    signal_mock = mocker.Mock()
    instance.signal_entities_updated = signal_mock

    instance.set_map_entities([])

    assert instance.map_entities == {}
    signal_mock.emit.assert_called_once_with([])

def test_set_actions(mocker):
    mocker.patch("custom.business.layer_trace_qgis.iface")
    instance = LayerTraceQGIS([], [])

    signal_tick_reset_mock = mocker.Mock()
    emit_mock = mocker.patch.object(signal_tick_reset_mock, "emit")
    instance.signal_tick_reset = signal_tick_reset_mock

    mock1 = {"type": "move", "entity_id": "1", "end_at": 10}
    mock2 = {"type": "change_icon", "entity_id": "2", "end_at": 20}
    a1 = mocker.MagicMock(end_at=10)
    a2 = mocker.MagicMock(end_at=20)
    mocker.patch("custom.actions.action_factory.ActionFactory.action_from_dict", side_effect=[a1, a2])

    instance.set_actions([mock1, mock2])
    assert len(instance.actions) == 2
    assert instance.tick_end == 20
    emit_mock.assert_called_once()


def test_set_actions_empty(mocker):
    mocker.patch("custom.business.layer_trace_qgis.iface")
    instance = LayerTraceQGIS([], [])
    instance.actions = ["some"]
    instance.set_actions([])
    assert instance.actions == []
    assert instance.tick_end == 0

def test_get_active_actions(mocker):
    mocker.patch("custom.business.layer_trace_qgis.iface")
    instance = LayerTraceQGIS([], [])

    actions = []

    test_action_highlight = {
        "type": "highlight",
        "start_at": 0,
        "end_at": 10,
        "entity_id": 6,
        "color": "yellow",
        "text": "Emission d'appel"
    }
    actions.append(test_action_highlight)

    test_action_move_to = {
        "type": "move_to",
        "start_at": 5,
        "end_at": 20,
        "entity_id": 1,
        "entity_id2": 6,
        "distance": 300,
        "text": "Approche de la balise"
    }
    actions.append(test_action_move_to)

    test_action_around = {
        "type": "around",
        "start_at": 21,
        "end_at": 40,
        "entity_id": 1,
        "entity_id2": 6,
        "angle": 360,
        "distance": 300
    }
    actions.append(test_action_around)

    instance.set_actions(actions)
    instance.tick = 6

    assert len(instance.get_active_actions()) == 2

    instance.tick = 25
    assert len(instance.get_active_actions()) == 1

def test_need_refresh_categories(mocker, mock_map_entity, mock_map_entity2):
    mocker.patch("custom.business.layer_trace_qgis.iface")

    instance = LayerTraceQGIS([mock_map_entity], [])

    instance.map_entities = {"e1": mock_map_entity, "e2": mock_map_entity2}

    assert instance.need_refresh_categories() == True
    mock_map_entity2.get_need_refresh_category.return_value = False
    assert instance.need_refresh_categories() == False

def test_map_entities_need_refresh_labels(mocker, mock_map_entity, mock_map_entity2):
    mocker.patch("custom.business.layer_trace_qgis.iface")

    instance = LayerTraceQGIS([mock_map_entity], [])

    instance.map_entities = {"e1": mock_map_entity, "e2": mock_map_entity2}

    assert instance.map_entities_need_refresh_labels() == [mock_map_entity2]
    mock_map_entity2.get_need_update_label.return_value = False
    assert instance.map_entities_need_refresh_labels() == []


def test_apply_renderer(mocker, mock_map_entity, mock_map_entity2):
    mocker.patch("custom.business.layer_trace_qgis.iface")
    instance = LayerTraceQGIS([], [])
    instance.map_entities = {"e1": mock_map_entity, "e2": mock_map_entity2}

    mock_generate_category = mocker.patch.object(instance.layer, "setRenderer")

    instance.apply_renderer()
    mock_generate_category.assert_called_once()

def test_apply_trace_renderer(mocker, mock_map_entity, mock_map_entity2):
    mocker.patch("custom.business.layer_trace_qgis.iface")
    instance = LayerTraceQGIS([], [])
    instance.map_entities = {"e1": mock_map_entity, "e2": mock_map_entity2}

    mock_generate_category = mocker.patch.object(instance.layer_trace, "setRenderer")

    instance.apply_renderer()
    mock_generate_category.assert_called_once()

def test_reset_before_refresh(mocker, mock_map_entity):
    mocker.patch("custom.business.layer_trace_qgis.iface")
    instance = LayerTraceQGIS([], [])
    instance.map_entities = {"e1": mock_map_entity}
    instance.lines = [[1, 2]]
    mocker.patch.object(instance, 'has_need_refresh_categories_after', return_value=True)

    instance.reset_before_refresh()
    mock_map_entity.reset_icon.assert_called_once()

def test_draw_line_between(mocker, mock_map_entity, mock_map_entity2):
    mocker.patch("custom.business.layer_trace_qgis.iface")

    # Mock des géométries
    mock_geom1 = mocker.MagicMock()
    mock_geom1.isGeosValid.return_value = True
    mock_geom1.isEmpty.return_value = False
    mock_geom1.asPoint.return_value = QgsPointXY(1, 1)

    mock_geom2 = mocker.MagicMock()
    mock_geom2.isGeosValid.return_value = True
    mock_geom2.isEmpty.return_value = False
    mock_geom2.asPoint.return_value = QgsPointXY(2, 2)

    # Mock des features
    mock_feature1 = mocker.Mock()
    mock_feature1.geometry.return_value = mock_geom1
    mock_map_entity.feature = mock_feature1

    mock_feature2 = mocker.Mock()
    mock_feature2.geometry.return_value = mock_geom2
    mock_map_entity2.feature = mock_feature2

    # Instance et test
    instance = LayerTraceQGIS([], [])
    instance.map_entities = {"entity1": mock_map_entity, "entity2": mock_map_entity2}

    mocker.patch("qgis.core.QgsGeometry.fromPolylineXY")
    mocker.patch("qgis.core.QgsFeature")

    instance.draw_line_between("entity1", "entity2")

def test_unload(mocker, mock_map_entity):
    iface = mocker.patch("custom.business.layer_trace_qgis.iface")
    iface.mapCanvas.return_value.extentsChanged.disconnect = mocker.Mock()

    timer_mock = mocker.Mock()
    timer_mock.timeout.disconnect = mocker.Mock()
    instance = LayerTraceQGIS([], [])
    instance.timer = timer_mock
    instance.map_entities = {"e1": mock_map_entity}

    project = mocker.patch("custom.business.layer_trace_qgis.QgsProject.instance")
    root = mocker.MagicMock()
    project.return_value.layerTreeRoot.return_value = root
    root.findGroup.return_value = mocker.Mock()

    instance.stop_timer = mocker.Mock()
    instance.unload()
    instance.stop_timer.assert_called_once()

def test_static_methods(mocker, mock_map_entity, mock_map_entity2):
    mocker.patch("custom.business.layer_trace_qgis.iface")

    instance = LayerTraceQGIS.get_instance([mock_map_entity, mock_map_entity2], [])
    mocker.patch.object(instance, "apply_renderer")

    assert LayerTraceQGIS.get_instance().get_map_entity("e1") == mock_map_entity
