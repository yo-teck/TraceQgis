from .action import Action

class ActionBackground(Action):
    """
    Classe ActionBackground représentant une action permettant de modifier l'image d'arrière-plan d'une entité sur une carte.
    """
    def __init__(self, start_at: int, end_at: int, entity_id: int, image: str, text: str = ""):
        """
        Initialise une nouvelle instance de la classe.

        Paramètres:
        start_at (int): La position de début de l'entité.
        end_at (int): La position de fin de l'entité.
        entity_id (int): L'identifiant de l'entité.
        image (str): Le chemin ou l'URL d'une image associée.
        text (str): Texte optionnel associé à l'entité. Par défaut, une chaîne vide.
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
        - Ajoute une image de font à l'entité
        """
        from ..business.layer_trace_qgis import LayerTraceQGIS

        map_entity = LayerTraceQGIS.get_map_entity(self.entity_id)
        if not map_entity:
            return False

        current_tick = LayerTraceQGIS.get_current_tick()

        map_entity.set_background_image(self.image, (current_tick == self.start_at or current_tick == self.end_at))
        self.add_text(map_entity)

        return True