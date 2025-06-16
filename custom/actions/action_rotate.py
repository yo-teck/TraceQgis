from .action import Action
from ..utils.utils import Utils


class ActionRotate(Action):
    def __init__(self, start_at: int, end_at: int, entity_id: int, angle: float, text: str = ""):
        super().__init__(start_at, end_at, entity_id, text)

        self.start_angle = angle
        self.end_angle = angle

    def execute(self) -> bool:
        from ..business.layer_trace_qgis import LayerTraceQGIS

        map_entity = LayerTraceQGIS.get_map_entity(self.entity_id)
        if not map_entity:
            return False

        current_tick = LayerTraceQGIS.get_current_tick()

        if current_tick == self.start_at:
            self.start_angle = float(map_entity.angle)

        new_value = Utils.get_intermediare_value(
            self.start_at,
            self.end_at,
            current_tick,
            self.start_angle,
            self.end_angle)

        map_entity.set_angle(new_value)
        self.add_text(map_entity)
        return True