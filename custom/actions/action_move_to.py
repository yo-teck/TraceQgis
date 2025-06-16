import math
from typing import Tuple
from typing import TYPE_CHECKING

from ..utils.utils import Utils

if TYPE_CHECKING:
    pass

from .action import Action

class ActionMoveTo(Action):
    def __init__(self, start_at: int, end_at: int, entity_id: int, entity_id2: int, distance: float = 100, text: str = ""):
        super().__init__(start_at, end_at, entity_id, text)

        self.entity_id2 = entity_id2
        self.distance = distance
        self.init = False
        self.lat_from = None
        self.lon_from = None
        self.lat_to = None
        self.lon_to = None
        self.alti_from = None
        self.alti_to = None

    def execute(self) -> bool:
        from ..business.layer_trace_qgis import LayerTraceQGIS

        map_entity = LayerTraceQGIS.get_map_entity(self.entity_id)
        map_entity2 = LayerTraceQGIS.get_map_entity(self.entity_id2)
        if not map_entity or not map_entity2:
            return False

        if not self.init:
            point = map_entity.feature.geometry().centroid().asPoint()
            self.lat_from = point.y()
            self.lon_from = point.x()
            self.alti_from = map_entity.altitude
            point = map_entity2.feature.geometry().centroid().asPoint()
            self.alti_to = map_entity2.altitude
            if self.distance is None:
                self.lat_to = point.y()
                self.lon_to = point.x()
            else:
                angle = Utils.calculate_azimuth(point.y(), point.x(), self.lat_from, self.lon_from)
                self.lat_to, self.lon_to = Utils.destination_point(point.y(), point.x(), angle, self.distance)
            self.init = True

        old_position = map_entity.feature.geometry().asPoint()

        lat, lon, alti = self.get_next_geometry()
        map_entity.move_to(lat, lon, alti)

        LayerTraceQGIS.get_instance().log_trace(map_entity, old_position)

        self.add_text(map_entity)
        return True

    def get_next_geometry(self) -> Tuple[float, float, float]:
        from ..business.layer_trace_qgis import LayerTraceQGIS

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

