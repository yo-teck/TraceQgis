import math
import random

from qgis.PyQt.QtGui import QColor

class Utils:

    @staticmethod
    def get_intermediare_value(tick_start: int, tick_end: int, current_tick: int, start_value: float, end_value: float) -> float:

        if current_tick >= tick_end:
            return end_value
        elif current_tick == tick_start:
            return start_value

        # Calculer la fraction de progression entre start_at et end_at
        total_duration = tick_end - tick_start
        elapsed = current_tick - tick_start
        t = elapsed / total_duration

        # Interpolation linéaire entre start_size et end_size
        return start_value + t * (end_value - start_value)

    @staticmethod
    def calculate_azimuth(lat1: float, lon1: float, lat2: float, lon2: float):
        """
        Calcule l'azimuth (en degrés) entre deux points GPS.
        Entrées en degrés.
        Sortie en degrés.
        """
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_lambda = math.radians(lon2 - lon1)

        x = math.sin(delta_lambda) * math.cos(phi2)
        y = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(delta_lambda)

        azimuth = math.degrees(math.atan2(x, y))
        return (azimuth + 360) % 360

    @staticmethod
    def point_at_distance(lat: float, lon: float, azimuth_deg: float, distance_m: float):
        """
        Calcule un point GPS à une certaine distance (en mètres)
        et azimut (en degrés) à partir d'un point origine.
        """
        R = 6371000  # Rayon de la Terre en mètres

        phi1 = math.radians(lat)
        lambda1 = math.radians(lon)
        theta = math.radians(azimuth_deg)

        phi2 = math.asin(math.sin(phi1) * math.cos(distance_m / R) +
                         math.cos(phi1) * math.sin(distance_m / R) * math.cos(theta))
        lambda2 = lambda1 + math.atan2(math.sin(theta) * math.sin(distance_m / R) * math.cos(phi1),
                                       math.cos(distance_m / R) - math.sin(phi1) * math.sin(phi2))

        return math.degrees(phi2), math.degrees(lambda2)

    @staticmethod
    def destination_point(lat_deg: float, lon_deg: float, azimuth_deg: float, distance_m: float) -> tuple[float, float]:
        """
        Calcule la position GPS (lat, lon) à partir d'un point GPS, d'un azimut et d'une distance (en mètres).

        Args:
            lat_deg (float): latitude du point de départ en degrés
            lon_deg (float): longitude du point de départ en degrés
            azimuth_deg (float): angle de direction (azimut) en degrés (0 = nord, 90 = est, ...)
            distance_m (float): distance à parcourir en mètres

        Returns:
            (lat, lon) (Tuple[float, float]): nouvelle position GPS en degrés
        """
        R = 6371000  # Rayon de la Terre en mètres
        lat1 = math.radians(lat_deg)
        lon1 = math.radians(lon_deg)
        azimuth = math.radians(azimuth_deg)

        lat2 = math.asin(math.sin(lat1) * math.cos(distance_m / R) +
                         math.cos(lat1) * math.sin(distance_m / R) * math.cos(azimuth))

        lon2 = lon1 + math.atan2(math.sin(azimuth) * math.sin(distance_m / R) * math.cos(lat1),
                                 math.cos(distance_m / R) - math.sin(lat1) * math.sin(lat2))

        return math.degrees(lat2), math.degrees(lon2)

    @staticmethod
    def rotating_position(start_tick: int, end_tick: int, current_tick: int, center_lat: float, center_lon: float, radius_m: float, total_angle_deg: float = 360.0) -> tuple[float, float]:
        """
        Calcule la position GPS d'un point tournant autour d'un point central à un rayon donné.

        Args:
            center_lat (float): latitude du point central (en degrés)
            center_lon (float): longitude du point central (en degrés)
            radius_m (float): rayon du cercle de rotation (en mètres)
            start_tick (int): tick de début de la rotation
            end_tick (int): tick de fin de la rotation
            current_tick (int): tick courant pour lequel on calcule la position
            total_angle_deg (float): angle total parcouru pendant la rotation (ex : 360 pour un tour complet)

        Returns:
            (lat, lon) (Tuple[float, float]): nouvelle position GPS sur le cercle
        """
        if current_tick <= start_tick:
            azimuth = 0
        elif current_tick >= end_tick:
            azimuth = total_angle_deg
        else:
            ratio = (current_tick - start_tick) / (end_tick - start_tick)
            azimuth = ratio * total_angle_deg

        return Utils.destination_point(center_lat, center_lon, azimuth, radius_m)

    @staticmethod
    def sort_action_func(action):
        from ..actions.action_load import ActionLoad
        from ..actions.action_unload import ActionUnload

        if isinstance(action, ActionLoad):
            return 0
        elif isinstance(action, ActionUnload):
            return 6
        else:
            return 3

    @staticmethod
    def sort_actions(actions):
        return sorted(actions, key=Utils.sort_action_func)

    @staticmethod
    def generate_random_color(entity_id: str):
        random.seed(entity_id)  # str accepté
        r = random.randint(50, 255)
        g = random.randint(50, 255)
        b = random.randint(50, 255)
        return QColor(r, g, b)