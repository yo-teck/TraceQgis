from .action import Action

class ActionLoad(Action):
    """
    Classe ActionLoad permet de charger une entité
    """
    def __init__(self, start_at: int, end_at: int, entity_id: str, entity_id2: str, text: str):
        """
        Initialise une instance de la classe avec les paramètres spécifiés.

        Paramètres:
        start_at (int): Position de début associée.
        end_at (int): Position de fin associée.
        entity_id (int): Identifiant de l'entité associée.
        entity_id2 (int): Identifiant secondaire de l'entité associée.
        text (str): Texte associé.
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
        - Charge l'entité uniquement à la fin de l'action.
        """
        from ..business.layer_trace_qgis import LayerTraceQGIS

        map_entity = LayerTraceQGIS.get_map_entity(self.entity_id)
        map_entity2 = LayerTraceQGIS.get_map_entity(self.entity_id2)
        if (not map_entity or not map_entity2) and not LayerTraceQGIS.is_loaded(map_entity) and not LayerTraceQGIS.is_loaded(map_entity2):
            return False

        current_tick = LayerTraceQGIS.get_current_tick()

        if current_tick == self.end_at:
            LayerTraceQGIS.static_load_entity(map_entity, map_entity2)
            map_entity2.set_need_update_label(True)

        self.add_text(map_entity)
        return True