from .action import Action

class ActionArrow(Action):
    """
    Classe ActionArrow représente une action permettant de tracer une flèche entre deux entités.
    """

    def __init__(self, start_at: int, end_at: int, entity_id: int, entity_id2: int, text: str = ""):
        """
        Initialise une instance de la classe avec des détails spécifiques sur les entités.

        Paramètres:
        start_at (int): Position de départ dans le texte.
        end_at (int): Position de fin dans le texte.
        entity_id (int): Identifiant de la première entité.
        entity_id2 (int): Identifiant de la deuxième entité.
        text (str): Texte associé à l'entité (facultatif).
        """
        super().__init__(start_at, end_at, entity_id, text)

        self.entity_id2 = entity_id2

    def execute(self) -> bool:
        """
        Retourne :
            bool : True si l'opération réussit, sinon False.

        Logique :
        - Récupère les entités de carte correspondantes à partir des identifiants spécifiés.
        - Vérifie les entités
        - Ajoute un ligne entre les deux entitées
        """
        from ..business.layer_trace_qgis import LayerTraceQGIS

        map_entity = LayerTraceQGIS.get_map_entity(self.entity_id)
        map_entity2 = LayerTraceQGIS.get_map_entity(self.entity_id2)

        if (not map_entity or not map_entity2) or map_entity.id == map_entity2.id:
            return False

        LayerTraceQGIS.get_instance().add_line(map_entity.id, map_entity2.id)
        self.add_text(map_entity)

        return True
