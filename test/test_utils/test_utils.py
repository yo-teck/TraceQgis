import math
import pytest
from custom.utils.utils import Utils
from custom.actions.action_load import ActionLoad
from custom.actions.action_unload import ActionUnload

def test_get_intermediare_value():
    # Avant la période, on obtient start_value
    assert Utils.get_intermediare_value(0, 10, 0, 5.0, 15.0) == 5.0
    # Après la période, on obtient end_value
    assert Utils.get_intermediare_value(0, 10, 11, 5.0, 15.0) == 15.0
    # Milieu de la période: interpolation linéaire
    val = Utils.get_intermediare_value(0, 10, 5, 0.0, 10.0)
    assert pytest.approx(val, 0.0001) == 5.0

def test_calculate_azimuth():
    # azimuth du point vers lui-même = 0
    assert Utils.calculate_azimuth(0, 0, 0, 0) == 0
    # azimuth nord -> est
    az = Utils.calculate_azimuth(0, 0, 0, 1)
    assert pytest.approx(az, 0.1) == 90
    # azimuth sud -> nord
    az = Utils.calculate_azimuth(10, 0, 0, 0)
    # on sait que c'est dans [0,360], on peut juste vérifier que ça tourne bien
    assert 0 <= az <= 360

def test_rotating_position():
    # Au start_tick, azimuth = 0
    lat1, lon1 = Utils.rotating_position(0, 10, 0, 0, 0, 1000)
    lat2, lon2 = Utils.destination_point(0, 0, 0, 1000)
    assert pytest.approx(lat1, 0.0001) == lat2
    assert pytest.approx(lon1, 0.0001) == lon2

    # Au end_tick, azimuth = total_angle_deg (par défaut 360)
    lat1, lon1 = Utils.rotating_position(0, 10, 10, 0, 0, 1000)
    lat2, lon2 = Utils.destination_point(0, 0, 360, 1000)
    # 360° correspond à un tour complet => position très proche du point de départ
    assert abs(lat1) < 0.01
    assert abs(lon1) < 0.01

    # Milieu: azimuth interpolé
    lat1, lon1 = Utils.rotating_position(0, 10, 5, 0, 0, 1000)
    lat2, lon2 = Utils.destination_point(0, 0, 180, 1000)  # milieu, azimuth = 180°
    # Latitudes proches (sud du point de départ)
    assert abs(lat1 - lat2) < 0.01

def test_sort_action_func_and_sort_actions(mocker):
    load_action = mocker.Mock(spec=ActionLoad)
    unload_action = mocker.Mock(spec=ActionUnload)
    other_action = mocker.Mock()

    # Forcer le __class__ pour que isinstance fonctionne
    load_action.__class__ = ActionLoad
    unload_action.__class__ = ActionUnload

    assert Utils.sort_action_func(load_action) == 0
    assert Utils.sort_action_func(unload_action) == 6
    assert Utils.sort_action_func(other_action) == 3

    actions = [other_action, unload_action, load_action]
    sorted_actions = Utils.sort_actions(actions)
    assert sorted_actions == [load_action, other_action, unload_action]
