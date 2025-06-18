from .action import Action
from ..utils.utils import Utils

class ActionChangeSize(Action):
    """
    Classe ActionChangeSize permet de modifier la taille d'une entité au cours du temps.
    """
    def __init__(self, start_at: int, end_at: int, entity_id: str, size: float, text: str = ""):
        """
        Initialise une instance de la classe.

        Paramètres:
        start_at (int): Position de début de l'entité.
        end_at (int): Position de fin de l'entité.
        entity_id (int): Identifiant unique de l'entité.
        size (float): Taille associée à l'entité.
        text (str, optionnel): Texte associé à l'entité. Par défaut, chaîne vide.
        """
        super().__init__(start_at, end_at, entity_id, text)

        self.start_size = size
        self.end_size = size

    def execute(self) -> bool:
        """
        Retourne :
            bool : True si l'opération réussit, sinon False.

        Logique :
        - Récupère la(es) entité(s) de carte correspondantes à partir des identifiants spécifiés.
        - Vérifie la(es) entité(s)
        - Calcule de la taille intermediaire
        - Mise à jour de la taille
        """
        from ..business.layer_trace_qgis import LayerTraceQGIS

        map_entity = LayerTraceQGIS.get_map_entity(self.entity_id)
        if not map_entity:
            return False

        current_tick = LayerTraceQGIS.get_current_tick()

        if current_tick == self.start_at:
            self.start_size = float(map_entity.size)

        new_value = Utils.get_intermediare_value(
            self.start_at,
            self.end_at,
            current_tick,
            self.start_size,
            self.end_size)

        self.add_text(map_entity)
        map_entity.set_size(new_value)
        return True