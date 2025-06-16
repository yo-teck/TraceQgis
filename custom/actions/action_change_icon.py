from .action import Action

class ActionChangeIcon(Action):
    """
        Cette classe représente une action pour changer l'icône d'une entité
    """
    def __init__(self, start_at: int, end_at: int, entity_id: int, image: str, text: str = ""):
        """
        Initialise une instance de la classe avec des informations spécifiques.

        Paramètres:
        start_at (int): Le point de départ de l'entité.
        end_at (int): Le point de fin de l'entité.
        entity_id (int): L'identifiant unique de l'entité.
        image (str): Le chemin ou l'URL de l'image associée à l'entité.
        text (str, optionnel): Le texte descriptif ou supplémentaire. Par défaut, une chaîne vide.
        """
        super().__init__(start_at, end_at, entity_id, text)

        self.image = image

    def execute(self) -> bool:
        """
        Retourne :
            bool : True si l'opération réussit, sinon False.

        Logique :
        - Récupère la(es) entité(s) de carte correspondantes à partir des identifiants spécifiés.
        - Vérifie la(es) entité(s)
        - Met à jour l'icône de l'entité en fonction
        """
        from ..business.layer_trace_qgis import LayerTraceQGIS

        map_entity = LayerTraceQGIS.get_map_entity(self.entity_id)
        if not map_entity:
            return False

        current_tick = LayerTraceQGIS.get_current_tick()

        map_entity.set_url_icon(self.image, (current_tick == self.start_at or current_tick == self.end_at))
        self.add_text(map_entity)
        return True