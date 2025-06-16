from .action import Action


class ActionArrow(Action):
    def __init__(self, start_at: int, end_at: int, entity_id: int, entity_id2: int, text: str = ""):
        super().__init__(start_at, end_at, entity_id, text)

        self.entity_id2 = entity_id2

    def execute(self) -> bool:
        from ..business.layer_trace_qgis import LayerTraceQGIS

        map_entity = LayerTraceQGIS.get_map_entity(self.entity_id)
        map_entity2 = LayerTraceQGIS.get_map_entity(self.entity_id2)

        if (not map_entity or not map_entity2) or map_entity.id == map_entity2.id:
            return False

        LayerTraceQGIS.get_instance().add_line(map_entity.id, map_entity2.id)
        self.add_text(map_entity)

        return True
