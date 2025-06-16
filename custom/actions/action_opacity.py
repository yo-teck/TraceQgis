from .action import Action
from ..utils.utils import Utils

class ActionOpacity(Action):
    """
    Classe ActionOpacity permet de modifier l'opacité d'une entité
    """
    def __init__(self, start_at: int, end_at: int, entity_id: int, opacity: float, text: str = ""):
        """
        Initialise une instance de la classe avec les valeurs spécifiées.

        Paramètres:
        start_at (int): Position de départ pour l'entité.
        end_at (int): Position de fin pour l'entité.
        entity_id (int): Identifiant unique de l'entité.
        opacity (float): Opacité initiale et finale de l'entité.
        text (str, optionnel): Texte associé à l'entité. Par défaut, il est vide.
        """
        super().__init__(start_at, end_at, entity_id, text)

        self.start_opacity = opacity
        self.end_opacity = opacity

    def execute(self) -> bool:
        """
        Retourne :
            bool : True si l'opération réussit, sinon False.

        Logique :
        - Récupère la(es) entité(s) de carte correspondantes à partir des identifiants spécifiés.
        - Vérifie la(es) entité(s).
        - Calcule de l'opacité intermediaire
        - Mise à jour de l'opacité
        """
        from ..business.layer_trace_qgis import LayerTraceQGIS

        map_entity = LayerTraceQGIS.get_map_entity(self.entity_id)
        if not map_entity:
            return False

        current_tick = LayerTraceQGIS.get_current_tick()

        if current_tick == self.start_at:
            self.start_opacity = float(map_entity.opacity)

        new_value = Utils.get_intermediare_value(
            self.start_at,
            self.end_at,
            current_tick,
            self.start_opacity,
            self.end_opacity)

        map_entity.set_opacity(new_value)
        self.add_text(map_entity)
        return True