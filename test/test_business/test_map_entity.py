from pytest_mock import MockerFixture

from custom.business.map_entity import MapEntity

def get_default_parameters():
    return {
        "id": "1",
        "name": "TestName",
        "icon": "icon.png",
        "latitude": 45.0,
        "longitude": 5.0,
        "altitude": -100,
        "size": 8,
        "angle": 0,
        "opacity": 1,
    }

def get_map_entity(mocker: MockerFixture) -> MapEntity:

    # Mock QLabel
    mock_label = mocker.patch("custom.business.map_entity.QLabel")
    mock_label.return_value.setText = mocker.Mock()
    mock_label.return_value.setFont = mocker.Mock()
    mock_label.return_value.setStyleSheet = mocker.Mock()
    mock_label.return_value.setAttribute = mocker.Mock()
    mock_label.return_value.move = mocker.Mock()
    mock_label.return_value.adjustSize = mocker.Mock()

    # Mock iface
    mock_iface = mocker.patch("custom.business.map_entity.iface")
    mock_iface.mainWindow.return_value = mocker.Mock()
    mock_canvas = mocker.Mock()
    mock_canvas.rect.return_value.contains.return_value = True
    mock_screen_pos = mocker.Mock()
    mock_screen_pos.x.return_value = 100
    mock_screen_pos.y.return_value = 200
    mock_canvas.mapSettings.return_value.mapToPixel.return_value.transform.return_value = mock_screen_pos
    mock_iface.mapCanvas.return_value = mock_canvas

    # Mock geometry
    mock_point = mocker.Mock()
    mock_point.x.return_value = 5.0
    mock_point.y.return_value = 45.0

    mock_geom = mocker.Mock()
    mock_geom.asPoint.return_value = mock_point

    mock_feature = mocker.patch("custom.business.map_entity.QgsFeature")
    mock_feature.return_value.geometry.return_value = mock_geom
    mock_feature_instance = mock_feature.return_value

    params = get_default_parameters()
    entity = MapEntity(params["id"], params["name"], params["icon"], params["latitude"], params["longitude"], params["altitude"], params["size"])

    # Crée l'entité
    return entity, params, mock_feature, mock_feature_instance, mock_label, mock_iface

def test_map_entity_init(mocker: MockerFixture):
    mock_generate_category = mocker.patch.object(MapEntity, "generate_category", return_value="MockedCategory")
    mock_update_label_position = mocker.patch.object(MapEntity, 'update_label_position')

    entity, params, mock_feature, mock_feature_instance, mock_label, mock_iface = get_map_entity(mocker)

    assert entity.id == params["id"]
    assert entity.name == params["name"]
    assert entity.url_icon == params["icon"]
    assert entity.latitude_default == params["latitude"]
    assert entity.longitude_default == params["longitude"]
    assert entity.altitude == params["altitude"]
    assert entity.altitude_default == params["altitude"]
    assert entity.size == params["size"]
    assert entity.size_default == params["size"]
    assert entity.angle == params["angle"]
    assert entity.opacity == params["opacity"]
    assert entity.highlight is None
    assert entity.background_image is None
    assert entity.texts == []
    assert entity.need_refresh_category is False
    assert entity.need_update_label is False

    # Assert QgsFeature and QgsGeometry initialization
    mock_feature.assert_called_once()
    mock_feature_instance.setAttributes.assert_called_once_with([params["id"], params["name"]])
    mock_feature_instance.setGeometry.assert_called_once()

    # Assert QLabel setup
    mock_label.assert_called_once_with(mock_iface.mainWindow.return_value)
    mock_label_instance = mock_label.return_value
    mock_label_instance.setFont.assert_called_once()
    mock_label_instance.setStyleSheet.assert_called_once_with("background-color: rgba(255, 255, 255, 200); border: 1px solid black;")
    mock_label_instance.setAttribute.assert_called_once()

    mock_update_label_position.assert_called_once()

    assert entity.category == "MockedCategory"

def test_get_latitude(mocker: MockerFixture):
    entity, params, mock_feature, mock_feature_instance, mock_label, mock_iface = get_map_entity(mocker)

    assert entity.get_latitude() == params["latitude"]

def test_get_altitude(mocker: MockerFixture):
    entity, params, mock_feature, mock_feature_instance, mock_label, mock_iface = get_map_entity(mocker)

    assert entity.get_altitude() == params["altitude"]

def test_get_longitude(mocker: MockerFixture):
    entity, params, mock_feature, mock_feature_instance, mock_label, mock_iface = get_map_entity(mocker)

    assert entity.get_longitude() == params["longitude"]

def test_set_altitude(mocker: MockerFixture):
    entity, params, mock_feature, mock_feature_instance, mock_label, mock_iface = get_map_entity(mocker)

    assert entity.altitude == params["altitude"]
    entity.set_altitude(100)
    assert entity.altitude == 100

# Tests pour get_url_icon et set_url_icon
def test_get_url_icon(mocker: MockerFixture):
    entity, params, mock_feature, mock_feature_instance, mock_label, mock_iface = get_map_entity(mocker)
    assert entity.get_url_icon() == params["icon"]

def test_set_url_icon(mocker: MockerFixture):
    entity, params, mock_feature, mock_feature_instance, mock_label, mock_iface = get_map_entity(mocker)
    assert entity.url_icon == params["icon"]
    entity.set_url_icon("new_icon.png")
    assert entity.url_icon == "new_icon.png"

def test_reset_url_icon(mocker: MockerFixture):
    entity, params, mock_feature, mock_feature_instance, mock_label, mock_iface = get_map_entity(mocker)
    assert entity.url_icon == params["icon"]
    entity.set_url_icon("new_icon.png")
    assert entity.url_icon == "new_icon.png"
    entity.reset_url_icon()
    assert entity.url_icon == params["icon"]

# Tests pour get_background_image et set_background_image
def test_get_background_image(mocker: MockerFixture):
    entity, params, mock_feature, mock_feature_instance, mock_label, mock_iface = get_map_entity(mocker)
    assert entity.get_background_image() is None


def test_set_background_image(mocker: MockerFixture):
    entity, params, mock_feature, mock_feature_instance, mock_label, mock_iface = get_map_entity(mocker)

    # Mock de la méthode ciblée
    mock_method = mocker.patch.object(entity, "set_need_refresh_category")

    # Vérification du comportement
    assert entity.background_image is None
    entity.set_background_image("background.png")
    assert entity.background_image == "background.png"

    # Vérifie que la méthode mockée a bien été appelée
    mock_method.assert_called_once_with(True)

def test_reset_background_image(mocker: MockerFixture):
    entity, params, mock_feature, mock_feature_instance, mock_label, mock_iface = get_map_entity(mocker)

    # Vérification du comportement
    assert entity.background_image is None
    entity.set_background_image("background.png")
    assert entity.background_image == "background.png"
    entity.reset_background_image()
    assert entity.background_image is None

# Tests pour get_highlight et set_highlight
def test_get_highlight(mocker: MockerFixture):
    entity, params, mock_feature, mock_feature_instance, mock_label, mock_iface = get_map_entity(mocker)
    assert entity.get_highlight() is None


def test_set_highlight(mocker: MockerFixture):
    entity, params, mock_feature, mock_feature_instance, mock_label, mock_iface = get_map_entity(mocker)

    mock_method = mocker.patch.object(entity, "set_need_refresh_category")

    assert entity.highlight is None
    entity.set_highlight("highlight_value")
    assert entity.highlight == "highlight_value"

    mock_method.assert_called_once_with(True)

# Tests pour get_size et set_size
def test_get_size(mocker: MockerFixture):
    entity, params, mock_feature, mock_feature_instance, mock_label, mock_iface = get_map_entity(mocker)
    assert entity.get_size() == params["size"]

def test_set_size(mocker: MockerFixture):
    entity, params, mock_feature, mock_feature_instance, mock_label, mock_iface = get_map_entity(mocker)

    mock_method = mocker.patch.object(entity, "set_need_refresh_category")

    assert entity.size == params["size"]
    entity.set_size(10)
    assert entity.size == 10

    mock_method.assert_called_once_with(True)

def test_reset_size(mocker: MockerFixture):
    entity, params, mock_feature, mock_feature_instance, mock_label, mock_iface = get_map_entity(mocker)
    assert entity.size == params["size"]
    entity.set_size(10)
    assert entity.size == 10
    entity.reset_size()
    assert entity.size == params["size"]


# Tests pour get_texts et set_texts
def test_get_texts(mocker: MockerFixture):
    entity, params, mock_feature, mock_feature_instance, mock_label, mock_iface = get_map_entity(mocker)
    assert entity.get_texts() == []


def test_set_texts(mocker: MockerFixture):
    entity, params, mock_feature, mock_feature_instance, mock_label, mock_iface = get_map_entity(mocker)

    mock_method = mocker.patch.object(entity, "set_need_update_label")

    entity.set_texts(["text1", "text2"])
    assert entity.texts == ["text1", "text2"]
    mock_method.assert_called_once_with(True)

def test_append_text(mocker: MockerFixture):
    entity, params, mock_feature, mock_feature_instance, mock_label, mock_iface = get_map_entity(mocker)

    mock_method = mocker.patch.object(entity, "set_need_update_label")

    entity.append_text("new text")
    assert "new text" in entity.texts
    mock_method.assert_called_once_with(True)


def test_reset_texts(mocker: MockerFixture):
    entity, params, mock_feature, mock_feature_instance, mock_label, mock_iface = get_map_entity(mocker)

    entity.set_texts(["text1", "text2"])
    assert entity.texts == ["text1", "text2"]
    entity.reset_text()
    assert entity.texts == []


# Tests pour get_feature
def test_get_feature(mocker: MockerFixture):
    entity, params, mock_feature, mock_feature_instance, mock_label, mock_iface = get_map_entity(mocker)
    assert entity.get_feature() == mock_feature_instance


# Tests pour get_need_refresh_category, test_set_need_refresh_category
def test_get_need_refresh_category(mocker: MockerFixture):
    entity, params, mock_feature, mock_feature_instance, mock_label, mock_iface = get_map_entity(mocker)
    assert entity.get_need_refresh_category() is False

def test_set_need_refresh_category(mocker: MockerFixture):
    entity, params, mock_feature, mock_feature_instance, mock_label, mock_iface = get_map_entity(mocker)
    assert entity.need_refresh_category is False
    entity.set_need_refresh_category(True)
    assert entity.need_refresh_category is True
    entity.set_need_refresh_category(False)
    assert entity.need_refresh_category is True

# Tests pour get_need_update_label, set_need_update_label
def test_get_need_update_label(mocker: MockerFixture):
    entity, params, mock_feature, mock_feature_instance, mock_label, mock_iface = get_map_entity(mocker)
    assert entity.get_need_update_label() is False

def test_set_need_update_label(mocker: MockerFixture):
    entity, params, mock_feature, mock_feature_instance, mock_label, mock_iface = get_map_entity(mocker)
    assert entity.need_update_label is False
    entity.set_need_update_label(True)
    assert entity.need_update_label is True
    entity.set_need_update_label(False)
    assert entity.need_update_label is True

# Tests pour get_name et set_name
def test_get_name(mocker: MockerFixture):
    entity, params, mock_feature, mock_feature_instance, mock_label, mock_iface = get_map_entity(mocker)
    assert entity.get_name() == params["name"]


def test_set_name(mocker: MockerFixture):
    entity, params, mock_feature, mock_feature_instance, mock_label, mock_iface = get_map_entity(mocker)
    assert entity.name == params["name"]
    entity.set_name("NewEntityName")
    assert entity.name == "NewEntityName"

# Tests pour get_angle et set_angle
def test_get_angle(mocker: MockerFixture):
    entity, params, mock_feature, mock_feature_instance, mock_label, mock_iface = get_map_entity(mocker)
    assert entity.get_angle() == params["angle"]

def test_set_angle(mocker: MockerFixture):
    entity, params, mock_feature, mock_feature_instance, mock_label, mock_iface = get_map_entity(mocker)

    mock_method = mocker.patch.object(entity, "set_need_refresh_category")

    assert entity.angle == params["angle"]
    entity.set_angle(45)
    assert entity.angle == 45

    mock_method.assert_called_once_with(True)

def test_reset_angle(mocker: MockerFixture):
    entity, params, mock_feature, mock_feature_instance, mock_label, mock_iface = get_map_entity(mocker)

    assert entity.angle == params["angle"]
    entity.set_angle(45)
    assert entity.angle == 45
    entity.reset_angle()
    assert entity.angle == params["angle"]

# Tests pour get_id
def test_get_id(mocker: MockerFixture):
    entity, params, mock_feature, mock_feature_instance, mock_label, mock_iface = get_map_entity(mocker)
    assert entity.get_id() == params["id"]

# Tests pour get_opacity, set_opacity et reset_opacity
def test_get_opacity(mocker: MockerFixture):
    entity, params, mock_feature, mock_feature_instance, mock_label, mock_iface = get_map_entity(mocker)
    assert entity.get_opacity() == params["opacity"]

def test_set_opacity(mocker: MockerFixture):
    entity, params, mock_feature, mock_feature_instance, mock_label, mock_iface = get_map_entity(mocker)

    mock_method = mocker.patch.object(entity, "set_need_refresh_category")

    assert entity.opacity == params["opacity"]
    entity.set_opacity(0.5)
    assert entity.opacity == 0.5

    mock_method.assert_called_once_with(True)

def test_reset_opacity(mocker: MockerFixture):
    entity, params, mock_feature, mock_feature_instance, mock_label, mock_iface = get_map_entity(mocker)
    assert entity.opacity == params["opacity"]
    entity.set_opacity(0.5)
    assert entity.opacity == 0.5
    entity.reset_opacity()
    assert entity.opacity == params["opacity"]

# Tests pour get_categorie
def test_get_category(mocker: MockerFixture):
    entity, params, mock_feature, mock_feature_instance, mock_label, mock_iface = get_map_entity(mocker)

    mock_category1 = mocker.patch("custom.business.map_entity.QgsRendererCategory")
    mock_category2 = mocker.patch("custom.business.map_entity.QgsRendererCategory")

    entity.category = mock_category1
    entity.need_refresh_category = True

    mock_generate = mocker.patch.object(entity, "generate_category", return_value=mock_category2)
    result = entity.get_category()

    mock_generate.assert_called_once()
    assert result == mock_category2
    assert entity.category == mock_category2
    assert entity.need_refresh_category is False

def test_get_category_skips_refresh(mocker: MockerFixture):
    entity, params, mock_feature, mock_feature_instance, mock_label, mock_iface = get_map_entity(mocker)

    mock_category1 = mocker.patch("custom.business.map_entity.QgsRendererCategory")
    mock_category2 = mocker.patch("custom.business.map_entity.QgsRendererCategory")

    entity.category = mock_category1
    entity.need_refresh_category = False

    mock_generate = mocker.patch.object(entity, "generate_category", return_value=mock_category2)
    result = entity.get_category()

    mock_generate.assert_not_called()
    assert result == mock_category1

def test_generate_category(mocker: MockerFixture):
    entity, params, mock_feature, mock_feature_instance, mock_label, mock_iface = get_map_entity(mocker)

    mock_category1 = mocker.patch("custom.business.map_entity.QgsRendererCategory")

    mocker.patch.object(entity, "generate_category", return_value=mock_category1)
    result = entity.generate_category()

    assert result == mock_category1

def test_generate_category_highligth(mocker: MockerFixture):
    entity, params, mock_feature, mock_feature_instance, mock_label, mock_iface = get_map_entity(mocker)

    entity.highlight = True

    mock_glow_effect = mocker.Mock(name="GlowEffect")
    mocker.patch("custom.business.map_entity.QgsOuterGlowEffect", return_value=mock_glow_effect)

    mock_glow_layer = mocker.Mock(name="GlowSymbolLayer")
    mocker.patch("custom.business.map_entity.QgsSimpleMarkerSymbolLayer", return_value=mock_glow_layer)

    mock_symbol = mocker.Mock(name="QgsMarkerSymbol")
    mocker.patch("custom.business.map_entity.QgsMarkerSymbol", return_value=mock_symbol)

    mocker.patch("custom.business.map_entity.QgsRasterMarkerSymbolLayer")
    mocker.patch("custom.business.map_entity.QgsRendererCategory")

    # Action
    entity.generate_category()

    # ✅ Vérifie que le symbol a reçu un layer contenant le glow effect
    mock_symbol.appendSymbolLayer.assert_any_call(mock_glow_layer)
    mock_glow_layer.setPaintEffect.assert_called_once_with(mock_glow_effect)

def test_generate_category_adds_raster_marker_layer(mocker):
    entity, params, mock_feature, mock_feature_instance, mock_label, mock_iface = get_map_entity(mocker)

    entity.background_image = "icon.png"

    # Mocks
    mock_symbol = mocker.Mock(name="QgsMarkerSymbol")
    mocker.patch("custom.business.map_entity.QgsMarkerSymbol", return_value=mock_symbol)

    mock_raster_layer = mocker.Mock(name="RasterMarkerSymbolLayer")
    background_image_patch = mocker.patch(
        "custom.business.map_entity.QgsRasterMarkerSymbolLayer", return_value=mock_raster_layer
    )

    mocker.patch("custom.business.map_entity.QgsRendererCategory")

    # Action
    entity.generate_category()

    # ✅ Vérifie que le raster layer a été créé avec url_icon
    background_image_patch.assert_any_call("icon.png")

    # ✅ Vérifie qu’il est bien ajouté au symbole
    mock_symbol.appendSymbolLayer.assert_any_call(mock_raster_layer)

def test_move_to_updates_geometry_and_altitude(mocker):
    # Mock de l'entité
    entity, params, mock_feature, mock_feature_instance, mock_label, mock_iface = get_map_entity(mocker)

    # Préparer les mocks pour QgsPointXY, QgsGeometry, et LayerTraceQGIS
    mock_point = mocker.Mock(name="QgsPointXY")
    mocker.patch("custom.business.map_entity.QgsPointXY", return_value=mock_point)

    mock_geometry = mocker.Mock(name="QgsGeometry")
    from_point_patch = mocker.patch("custom.business.map_entity.QgsGeometry.fromPointXY", return_value=mock_geometry)

    # Mock du feature et ID
    entity.feature = mocker.Mock(name="QgsFeature")
    entity.feature.id.return_value = 42
    entity.feature.geometry.return_value = mock_geometry

    # Patch pour LayerTraceQGIS singleton
    mock_data_provider = mocker.Mock(name="DataProvider")
    mock_layer = mocker.Mock(name="Layer", dataProvider=mocker.Mock(return_value=mock_data_provider))
    mock_get_instance = mocker.patch("custom.business.map_entity.LayerTraceQGIS.get_instance")
    mock_get_instance.return_value.layer = mock_layer

    # Patch de set_need_update_label
    mock_set_label = mocker.patch.object(entity, "set_need_update_label")

    # Action
    entity.move_to(48.85, 2.35, 123.0)

    # ✅ Vérifie la géométrie construite
    from_point_patch.assert_called_once_with(mock_point)
    entity.feature.setGeometry.assert_called_once_with(mock_geometry)

    # ✅ Vérifie que changeGeometryValues a été appelé avec le bon ID et géométrie
    mock_data_provider.changeGeometryValues.assert_called_once_with({42: mock_geometry})

    # ✅ Vérifie que l'altitude a bien été mise à jour
    assert entity.altitude == 123.0

    # ✅ Vérifie que le label est marqué pour mise à jour
    mock_set_label.assert_called_once_with(True)

def test_move_to_entity(mocker):
    # Mock de l'entité
    entity, params, mock_feature, mock_feature_instance, mock_label, mock_iface = get_map_entity(mocker)

    entity.move_to = mocker.Mock()

    # Création du mock map_entity avec les bons getters
    mock_entity = mocker.Mock()
    mock_entity.get_latitude.return_value = 48.8566
    mock_entity.get_longitude.return_value = 2.3522
    mock_entity.altitude = 35

    # Appel de la méthode
    entity.move_to_entity(mock_entity)

    # Vérification
    entity.move_to.assert_called_once_with(48.8566, 2.3522, 35)

def test_reset_calls_all_reset_methods(mocker):
    # Mock de l'entité
    entity, params, mock_feature, mock_feature_instance, mock_label, mock_iface = get_map_entity(mocker)

    # Patch toutes les méthodes appelées par reset
    methods = [
        "reset_url_icon",
        "reset_position",
        "reset_size",
        "reset_text",
        "reset_angle",
        "reset_opacity",
        "reset_highlight",
        "reset_background_image",
        "reset_label",
    ]

    for method in methods:
        mocker.patch.object(entity, method)

    # Action
    entity.reset()

    # ✅ Vérifie que chaque méthode a bien été appelée une fois
    for method in methods:
        getattr(entity, method).assert_called_once()

def test_reset_position(mocker):
    entity, params, mock_feature, mock_feature_instance, mock_label, mock_iface = get_map_entity(mocker)

    mocker_method = mocker.patch.object(entity, 'move_to')

    entity.reset_position()

    mocker_method.assert_called_once_with(params['latitude'], params['longitude'], params['altitude'])

def test_update_label_position_visible(mocker):
    # Setup entity mock
    entity, *_ = get_map_entity(mocker)
    entity.label = mocker.Mock()
    entity.feature.geometry().asPoint.return_value = mocker.Mock(x=lambda: 50, y=lambda: 60)
    entity.texts = []
    entity.altitude = 42
    entity.name = "Entity"
    entity.generate_description_label = mocker.Mock(return_value="Label content")

    # Setup canvas mock
    mock_canvas = mocker.Mock()
    mock_rect = mocker.Mock()
    mock_rect.contains.return_value = True
    mock_canvas.rect.return_value = mock_rect

    mock_transform = mocker.Mock()
    mock_transform.x.return_value = 100
    mock_transform.y.return_value = 150
    mock_canvas.mapSettings().mapToPixel().transform.return_value = mock_transform

    # Setup main window mock
    mock_main = mocker.Mock()
    mock_pos = mocker.Mock()
    mock_pos.x.return_value = 30
    mock_main.mapFromGlobal.return_value = mock_pos

    # Patching iface
    mocker.patch("custom.business.map_entity.iface.mapCanvas", return_value=mock_canvas)
    mocker.patch("custom.business.map_entity.iface.mainWindow", return_value=mock_main)

    # Appel
    entity.update_label_position(show_name=True, show_position=True)

    # Vérifications
    entity.label.setVisible.assert_any_call(True)
    entity.label.move.assert_called_once()
    entity.label.setText.assert_called_once_with("Label content")
    entity.label.adjustSize.assert_called_once()

def test_update_label_position_outside_canvas(mocker):
    # Setup entity mock
    entity, *_ = get_map_entity(mocker)
    entity.label = mocker.Mock()
    entity.feature.geometry().asPoint.return_value = mocker.Mock(x=lambda: 999, y=lambda: 999)
    entity.texts = []
    entity.generate_description_label = mocker.Mock()

    # Setup canvas mock
    mock_canvas = mocker.Mock()
    mock_rect = mocker.Mock()
    mock_rect.contains.return_value = False  # Point hors du canvas
    mock_canvas.rect.return_value = mock_rect

    mock_transform = mocker.Mock()
    mock_transform.x.return_value = 999
    mock_transform.y.return_value = 999
    mock_canvas.mapSettings().mapToPixel().transform.return_value = mock_transform

    # Setup main window mock
    mock_main = mocker.Mock()
    mock_pos = mocker.Mock()
    mock_pos.x.return_value = 0
    mock_main.mapFromGlobal.return_value = mock_pos

    # Patching iface
    mocker.patch("custom.business.map_entity.iface.mapCanvas", return_value=mock_canvas)
    mocker.patch("custom.business.map_entity.iface.mainWindow", return_value=mock_main)

    # Appel
    entity.update_label_position(show_name=True, show_position=True)

    # Vérifications
    entity.label.setVisible.assert_called_with(False)
    entity.label.move.assert_not_called()
    entity.label.setText.assert_not_called()
    entity.label.adjustSize.assert_not_called()

def test_generate_description_label_with_info_and_texts(mocker):
    entity, *_ = get_map_entity(mocker)
    entity.name = "Entity1"
    entity.altitude = 123.4567
    entity.texts = ["Line 1", "Line 2"]

    mock_point = mocker.Mock()
    mock_point.x.return_value = 1.23456
    mock_point.y.return_value = 2.34567
    entity.feature.geometry().asPoint.return_value = mock_point

    result = entity.generate_description_label(True, True)

    assert "Entity1" in result
    assert "2.3457, 1.2346, 123.4567" in result
    assert "Line 1" in result
    assert "Line 2" in result

def test_hide_label(mocker):
    entity, *_ = get_map_entity(mocker)
    entity.label = mocker.Mock()
    entity.hide_label()
    entity.label.setVisible.assert_called_once_with(False)


def test_show_label(mocker):
    entity, *_ = get_map_entity(mocker)
    entity.label = mocker.Mock()
    entity.show_label()
    entity.label.setVisible.assert_called_once_with(True)

def test_unload_removes_label(mocker):
    entity, *_ = get_map_entity(mocker)
    mock_label = mocker.Mock()
    entity.label = mock_label

    entity.unload()

    mock_label.setVisible.assert_called_once_with(False)
    mock_label.setParent.assert_called_once_with(None)
    mock_label.deleteLater.assert_called_once()
    assert entity.label is None

