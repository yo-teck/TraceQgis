import math
from typing import Tuple
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..business.map_entity import MapEntity

from .action import Action

class ActionMove(Action):
    """
        Classe ActionMove permet de mettre à jour la position d'une entité en fonction du temps
    """
    def __init__(self, start_at: int, end_at: int, entity_id: int, lat_from: float|None, lon_from: float|None, alti_from: float|None, lat_to: float, lon_to: float, alti_to: float|None, text: str = ""):
        """
        Initialise une instance de la classe avec les paramètres spécifiés.

        Arguments:
        start_at (int): Moment de début de l'intervalle ou de l'événement.
        end_at (int): Moment de fin de l'intervalle ou de l'événement"""
        super().__init__(start_at, end_at, entity_id, text)

        self.lat_from = lat_from
        self.lon_from = lon_from
        self.lat_to = lat_to
        self.lon_to = lon_to
        self.alti_from = alti_from
        self.alti_to = alti_to

    def execute(self) -> bool:
        """
        Retourne :
            bool : True si l'opération réussit, sinon False.

        Logique :
        - Récupère la(es) entité(s) de carte correspondantes à partir des identifiants spécifiés.
        - Vérifie la(es) entité(s).
        - Calcule des positions intermediaire l'entité.
        - Déplace l'entité sur la carte selon les coordonnées calculées
        - Conserve dans les journaux la trace du mouvement depuis la position précédente
        """
        from ..business.layer_trace_qgis import LayerTraceQGIS

        map_entity = LayerTraceQGIS.get_map_entity(self.entity_id)
        if not map_entity:
            return False

        old_position = map_entity.feature.geometry().asPoint()

        lat, lon, alti = self.get_next_geometry(map_entity)
        map_entity.move_to(lat, lon, alti)


        LayerTraceQGIS.get_instance().log_trace(map_entity, old_position)

        self.add_text(map_entity)
        return True

    def get_next_geometry(self, map_entity: 'MapEntity') -> Tuple[float, float, float]:
        """
        Calcule et renvoie les coordonnées géographiques suivantes (latitude, longitude et altitude) en fonction de la progression temporelle et de la distance réelle entre des points de départ et d'arrivée.

        Arguments:
        map_entity (MapEntity): Instance de MapEntity contenant des informations géographiques et d'altitude.

        Retourne:
        Tuple[float, float, float]: Un tuple contenant les coordonnées interpolées (latitude, longitude, altitude).
        """
        from ..business.layer_trace_qgis import LayerTraceQGIS

        if self.lat_from is None or self.lon_from is None:
            point = map_entity.feature.geometry().centroid().asPoint()
            self.lat_from = point.y()
            self.lon_from = point.x()

        if self.alti_from is None:
            self.alti_from = map_entity.altitude

        if self.alti_to is None:
            self.alti_to = map_entity.altitude

        current_tick = LayerTraceQGIS.get_current_tick()

        # Rayon de la Terre en mètres
        R = 6371000

        # Convertir en radians
        phi1 = math.radians(self.lat_from)
        phi2 = math.radians(self.lat_to)
        lambda1 = math.radians(self.lon_from)
        lambda2 = math.radians(self.lon_to)

        dphi = phi2 - phi1
        dlambda = lambda2 - lambda1

        # Formule de Haversine pour la distance réelle
        a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        d = R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))  # en mètres

        # Progression temporelle
        if self.end_at == self.start_at or d == 0 or current_tick >= self.end_at:
            return self.lat_to, self.lon_to, self.alti_to

        ratio = min(max((current_tick - self.start_at) / (self.end_at - self.start_at), 0), 1)

        # Interpolation linéaire de position (lat/lon)
        lat = self.lat_from + (self.lat_to - self.lat_from) * ratio
        lon = self.lon_from + (self.lon_to - self.lon_from) * ratio
        alti = self.alti_from + (self.alti_to - self.alti_from) * ratio

        return lat, lon, alti
