from ..utils.utils import Utils

from .action import Action

class ActionAround(Action):
    """
    Classe ActionAround permet de déplacer une entité est déplacé autour d'un autre

    """
    def __init__(self, start_at: int, end_at: int, entity_id: int, entity_id2: int, distance: float = 100, angle: float = 360, text: str = ""):
        """
        Initialise une instance de la classe avec les paramètres donnés.

        Paramètres:
        start_at (int): Position de départ.
        end_at (int): Position de fin.
        entity_id (int): Identifiant de l'entité de base.
        entity_id2 (int): Identifiant secondaire de l'entité.
        distance (float): Distance associée, valeur par défaut 100.
        angle (float): Angle associé, valeur par défaut 360.
        text (str): Texte optionnel associé, valeur par défaut chaîne vide.

        Attributs définis:
        entity_id2 (int): Stocke l'identifiant secondaire de l'entité.
        distance (float): Stocke la distance associée.
        angle (float): Stocke l'angle associé.
        init (bool): Indique si une initialisation supplémentaire est terminée, par défaut False.
        center_lat (float ou None): Latitude centrale, initialisée à None.
        center_lon (float ou None): Longitude centrale, initialisée à None.
        origin_angle (float ou None): Angle d'origine, initialisé à None.
        """
        super().__init__(start_at, end_at, entity_id, text)

        self.entity_id2 = entity_id2
        self.distance = distance
        self.angle = angle
        self.init = False
        self.center_lat = None
        self.center_lon = None
        self.origin_angle = None

    def execute(self) -> bool:
        """
        Retourne :
            bool : True si l'opération réussit, sinon False.

        Logique :
        - Récupère les entités de carte correspondantes à partir des identifiants spécifiés.
        - Vérifie les entités
        - A la première execution récupére la position de l'entité cible et l'angle d'origine.
        - Calcule des positions intermediaire l'entité.
        - Déplace l'entité sur la carte selon les coordonnées calculées et un angle progressif.
        - Conserve dans les journaux la trace du mouvement depuis la position précédente.
        """
        from ..business.layer_trace_qgis import LayerTraceQGIS

        map_entity = LayerTraceQGIS.get_map_entity(self.entity_id)
        map_entity2 = LayerTraceQGIS.get_map_entity(self.entity_id2)

        if (not map_entity or not map_entity2) or map_entity.id == map_entity2.id:
            return False

        if not self.init:
            point1 = map_entity.feature.geometry().centroid().asPoint()
            point2 = map_entity2.feature.geometry().centroid().asPoint()
            self.center_lat = point2.y()
            self.center_lon = point2.x()
            self.origin_angle = Utils.calculate_azimuth(self.center_lat, self.center_lon, point1.y(), point1.x())
            self.angle += self.origin_angle
            self.init = True

        current_tick = LayerTraceQGIS.get_current_tick()

        old_position = map_entity.feature.geometry().asPoint()

        angle = Utils.get_intermediare_value(self.start_at, self.end_at, current_tick, self.origin_angle, self.angle)
        lat, lon = Utils.destination_point(self.center_lat, self.center_lon, angle, self.distance)

        map_entity.move_to(lat, lon, map_entity.altitude)

        LayerTraceQGIS.get_instance().log_trace(map_entity, old_position)

        self.add_text(map_entity)

        return True
