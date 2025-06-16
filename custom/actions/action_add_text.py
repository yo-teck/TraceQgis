from .action import Action

class ActionAddText(Action):
    def __init__(self, start_at: int, end_at: int, entity_id: int, text: str):
        super().__init__(start_at, end_at, entity_id, text)

    def execute(self) -> bool:
        from ..business.layer_trace_qgis import LayerTraceQGIS

        map_entity = LayerTraceQGIS.get_map_entity(self.entity_id)
        if not map_entity:
            return False

        self.add_text(map_entity)
        return True