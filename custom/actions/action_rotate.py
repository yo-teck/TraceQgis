from .action import Action
from ..utils.utils import Utils

class ActionRotate(Action):
    """
    Classe ActionRotate permet de faire tournée une entité
    """
    def __init__(self, start_at: int, end_at: int, entity_id: str, angle: float, text: str = ""):
        """
        Initialise une instance de la classe avec les paramètres spécifiés.

        Paramètres:
        start_at (int): Position de départ.
        end_at (int): Position de fin.
        entity_id (int): Identifiant de l'entité associée.
        angle (float): Valeur de l'angle à utiliser.
        text (str): Texte facultatif lié à l'instance. Par défaut, une chaîne vide est utilisée.
        """
        super().__init__(start_at, end_at, entity_id, text)

        self.start_angle = angle
        self.end_angle = angle

    def execute(self) -> bool:
        """
        Retourne :
            bool : True si l'opération réussit, sinon False.

        Logique :
        - Récupère la(es) entité(s) de carte correspondantes à partir des identifiants spécifiés.
        - Vérifie la(es) entité(s)
        - Calcule de la rotation intermediaire
        - Mise à jour de la rotation
        """
        from ..business.layer_trace_qgis import LayerTraceQGIS

        map_entity = LayerTraceQGIS.get_map_entity(self.entity_id)
        if not map_entity:
            return False

        current_tick = LayerTraceQGIS.get_current_tick()

        if current_tick == self.start_at:
            self.start_angle = float(map_entity.angle)

        new_value = Utils.get_intermediare_value(
            self.start_at,
            self.end_at,
            current_tick,
            self.start_angle,
            self.end_angle)

        map_entity.set_angle(new_value)
        self.add_text(map_entity)
        return True