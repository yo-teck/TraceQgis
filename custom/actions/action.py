from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

class Action(ABC):

    def __init__(self, start_at: int, end_at: int, entity_id: int, text: str = ""):
        if start_at is None or end_at is None or entity_id is None:
            raise Exception("Paramètre invalide")
        elif start_at > end_at:
            raise Exception("start_at > end_at")

        self.start_at = start_at
        self.end_at = end_at
        self.entity_id = entity_id

        self.text = text

    def is_active_at(self, tick: int) -> bool:
        return self.start_at <= tick <= self.end_at

    def add_text(self, map_entity: "MapEntity"):
        if self.text:
            map_entity.append_text(self.text)

    @abstractmethod
    def execute(self) -> bool:
        pass

    def __str__(self):
        from ..business.layer_trace_qgis import LayerTraceQGIS

        text = self.__class__.__name__ + ":"
        text += " current_tick=" + str(LayerTraceQGIS.get_current_tick())
        for nom_attr, valeur in self.__dict__.items():
            text += f", {nom_attr}={str(valeur)}"

        return text