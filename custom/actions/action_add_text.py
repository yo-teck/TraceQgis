from .action import Action

class ActionAddText(Action):
    """
        Cette classe représente une action pour ajouter du texte à une entité dans une carte.
    """
    def __init__(self, start_at: int, end_at: int, entity_id: str, text: str):
        """
        Initialise une instance de la classe avec des valeurs pour les attributs.

        Paramètres:
        start_at (int): Position de début associée à l'entité.
        end_at (int): Position de fin associée à l'entité.
        entity_id (int): Identifiant unique de l'entité.
        text (str): Texte associé à l'entité.
        """
        super().__init__(start_at, end_at, entity_id, text)

    def execute(self) -> bool:
        """
        Retourne :
            bool : True si l'opération réussit, sinon False.

        Logique :
            - Ajoute du texte à une entitée
        """
        from ..business.layer_trace_qgis import LayerTraceQGIS

        map_entity = LayerTraceQGIS.get_map_entity(self.entity_id)
        if not map_entity:
            return False

        self.add_text(map_entity)
        return True