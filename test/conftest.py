import sys
import pytest

@pytest.fixture(autouse=True)
def mock_qgis_modules(mocker):
    # Mock des modules QGIS
    qgis_mock = mocker.MagicMock()
    qgis_core_mock = mocker.MagicMock()
    qgis_qtcore_mock = mocker.MagicMock()

    # Exemple : mock de QgsVectorLayer
    qgis_core_mock.QgsVectorLayer.return_value = mocker.MagicMock()

    mocker.patch.dict(sys.modules, {
        "qgis": qgis_mock,
        "qgis.core": qgis_core_mock,
        "qgis.PyQt.QtCore": qgis_qtcore_mock,
        "qgis.utils": mocker.MagicMock(),
    })