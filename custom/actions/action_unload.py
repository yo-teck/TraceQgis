from .action import Action

class ActionUnload(Action):
    """
    Classe ActionUnload permet de décharger une entitée
    """
    def __init__(self, start_at: int, end_at: int, entity_id: int, entity_id2: int, text: str = ""):
        """
        Initialise une instance de la classe avec les paramètres donnés.

        Paramètres:
        start_at (int): Position de départ de l'entité.
        end_at (int): Position de fin de l'entité.
        entity_id (int): Identifiant de l'entité.
        entity_id2 (int): Deuxième identifiant de l'entité.
        text (str): Texte associé à l'entité.
        """
        super().__init__(start_at, end_at, entity_id, text)

        self.entity_id2 = entity_id2

    def execute(self) -> bool:
        """
        Retourne :
            bool : True si l'opération réussit, sinon False.

        Logique :
        - Récupère la(es) entité(s) de carte correspondantes à partir des identifiants spécifiés.
        - Vérifie la(es) entité(s).
        - Décharge l'entité uniquement à la fin de l'action.
        """
        from ..business.layer_trace_qgis import LayerTraceQGIS

        map_entity = LayerTraceQGIS.get_map_entity(self.entity_id)
        map_entity2 = LayerTraceQGIS.get_map_entity(self.entity_id2)
        if not map_entity or not map_entity2 or not LayerTraceQGIS.static_is_loaded(map_entity2, map_entity):
            return False

        current_tick = LayerTraceQGIS.get_current_tick()

        if current_tick == self.end_at:
            map_entity2.move_to_entity(map_entity)
            LayerTraceQGIS.static_unload_entity(map_entity, map_entity2)
            map_entity2.set_need_update_label(True)

        self.add_text(map_entity)

        return True