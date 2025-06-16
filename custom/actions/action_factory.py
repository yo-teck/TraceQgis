from .action_add_text import ActionAddText
from .action_around import ActionAround
from .action_background import ActionBackground
from .action_change_size import ActionChangeSize
from .action_highlight import ActionHighlight
from .action_load import ActionLoad
from .action_move import ActionMove
from .action_move_to import ActionMoveTo
from .action_opacity import ActionOpacity
from .action_rotate import ActionRotate
from .action_arrow import ActionArrow
from .action_change_icon import ActionChangeIcon
from .action_unload import ActionUnload


class ActionFactory:
    @staticmethod
    def action_from_dict(data: dict):
        """
        Crée une instance d'action à partir d'un dictionnaire de données.

        :param data: dictionnaire contenant au moins une clé 'type'
        :return: instance de BaseAction
        :raises ValueError: si le type d'action est inconnu
        """
        t = data.get("type")

        match t:
            case "move":
                return ActionMove(data.get("start_at"), data.get("end_at"), data.get("entity_id"), data.get("lat_from"), data.get("lon_from"), data.get("alti_from"), data["lat_to"], data["lon_to"], data.get("alti_to"), data.get("text"))
            case "move_to":
                return ActionMoveTo(data.get("start_at"), data.get("end_at"), data.get("entity_id"), data.get("entity_id2"), data.get("distance"), data.get("text"))
            case "text":
                return ActionAddText(data.get("start_at"), data.get("end_at"), data.get("entity_id"), data.get("text"))
            case "arrow":
                return ActionArrow(data.get("start_at"), data.get("end_at"), data.get("entity_id"), data.get("entity_id2"), data.get("text"))
            case "around":
                return ActionAround(data.get("start_at"), data.get("end_at"), data.get("entity_id"), data.get("entity_id2"), data["distance"], data.get("angle"), data.get("text"))
            case "image":
                return ActionChangeIcon(data.get("start_at"), data.get("end_at"), data.get("entity_id"), data.get("image"), data.get("text"))
            case "background":
                return ActionBackground(data.get("start_at"), data.get("end_at"), data.get("entity_id"), data.get("image"), data.get("text"))
            case "size":
                return ActionChangeSize(data.get("start_at"), data.get("end_at"), data.get("entity_id"), data.get("size"), data.get("text"))
            case "opacity":
                return ActionOpacity(data.get("start_at"), data.get("end_at"), data.get("entity_id"), data.get("opacity"), data.get("text"))
            case "rotate":
                return ActionRotate(data.get("start_at"), data.get("end_at"), data.get("entity_id"), data.get("angle"), data.get("text"))
            case "highlight":
                return ActionHighlight(data.get("start_at"), data.get("end_at"), data.get("entity_id"), data.get("color"), data.get("text"))
            case "load":
                return ActionLoad(data.get("start_at"), data.get("end_at"), data.get("entity_id"), data.get("entity_id2"), data.get("text"))
            case "unload":
                return ActionUnload(data.get("start_at"), data.get("end_at"), data.get("entity_id"), data.get("entity_id2"), data.get("text"))
            case _:
                raise ValueError(f"Action inconnue : {t}")