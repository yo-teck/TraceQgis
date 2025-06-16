from .action import Action

class ActionHighlight(Action):
    def __init__(self, start_at: int, end_at: int, entity_id: int, color: str = "yellow", text: str = ""):
        super().__init__(start_at, end_at, entity_id, text)

        if color not in ["yellow", "green", "blue", "red"]:
            self.highlight = "yellow"
        else:
            self.highlight = color


    def execute(self) -> bool:
        from ..business.layer_trace_qgis import LayerTraceQGIS

        map_entity = LayerTraceQGIS.get_map_entity(self.entity_id)
        if not map_entity:
            return False

        current_tick = LayerTraceQGIS.get_current_tick()

        map_entity.set_highlight(self.highlight, (current_tick == self.start_at or current_tick == self.end_at))
        self.add_text(map_entity)
        return True