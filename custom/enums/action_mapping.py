from enum import Enum

class ActionType(Enum):
    MOVE = (
        "move",
        "ActionMove",
        ["start_at", "end_at", "entity_id", "lat_from", "lon_from", "alti_from", "lat_to", "lon_to", "alti_to", "text"],
        {}
    )
    MOVE_TO = (
        "move_to",
        "ActionMoveTo",
        ["start_at", "end_at", "entity_id", "entity_id2", "distance", "text"],
        {
            "type": "object",
            "properties": {
                "var_object_to_move": {"type": "string"},
                "var_object_destination": {"type": "string"},
                "text": {"type": "string"},
            },
            "required": ["var_object_to_move", "var_object_destination"],
        }
    )
    TEXT = (
        "text",
        "ActionAddText",
        ["start_at", "end_at", "entity_id", "text"],
        {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "var_object": {"type": "string"},
            },
            "required": ["var_object", "text"]
        }
    )
    ARROW = (
        "arrow",
        "ActionArrow",
        ["start_at", "end_at", "entity_id", "entity_id2", "text"],
        {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "var_object_start": {"type": "string"},
                "var_object_end": {"type": "string"},
            },
            "required": ["var_object_start", "var_object_end"]
        }
    )
    AROUND = (
        "around",
        "ActionAround",
        ["start_at", "end_at", "entity_id", "entity_id2", "distance", "angle", "text"],
        {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "var_object_who_move": {"type": "string"},
                "var_object_center": {"type": "string"},
                "distance": {"type": "number"},
                "angle": {"type": "number"},
            },
            "required": ["var_object_who_move", "var_object_center", "distance", "angle"]
        }
    )
    IMAGE = (
        "image",
        "ActionChangeIcon",
        ["start_at", "end_at", "entity_id", "image", "text"],
        {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "path_image": {"type": "string"},
                "var_object": {"type": "string"}
            },
            "required": ["text", "path_image", "var_object"]
        }
    )
    BACKGROUND = (
        "background",
        "ActionBackground",
        ["start_at", "end_at", "entity_id", "image", "text"],
        {
            "type": "object",
            "properties": {
                "var_object": {"type": "string"},
                "path_image": {"type": "string"},
                "text": {"type": "string"}
            },
            "required": ["var_object", "path_image"]
        }
    )
    SIZE = (
        "size",
        "ActionChangeSize",
        ["start_at", "end_at", "entity_id", "size", "text"],
        {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "var_object": {"type": "string"},
                "size": {"type": "number"}
            },
            "required": ["var_object", "size"]
        }
    )
    OPACITY = (
        "opacity",
        "ActionOpacity",
        ["start_at", "end_at", "entity_id", "opacity", "text"],
        {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "var_object": {"type": "string"},
                "opacity": {"type": "number"}
            },
            "required": ["var_object", "opacity"]
        }
    )
    ROTATE = (
        "rotate",
        "ActionRotate",
        ["start_at", "end_at", "entity_id", "angle", "text"],
        {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "var_object": {"type": "string"},
                "angle": {"type": "number"}
            },
            "required": ["var_object", "angle"]
        }
    )
    HIGHLIGHT = (
        "highlight",
        "ActionHighlight",
        ["start_at", "end_at", "entity_id", "color", "text"],
        {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "var_object": {"type": "string"},
                "color": {"type": "string"}
            },
            "required": ["var_object", "color"]
        }
    )
    LOAD = (
        "load",
        "ActionAround",
        ["start_at", "end_at", "entity_id", "entity_id2", "text"],
        {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "var_object_who_load": {"type": "string"},
                "var_object_loaded": {"type": "string"}
            },
            "required": ["var_object_who_load", "var_object_loaded"]
        }
    )
    UNLOAD = (
        "unload",
        "ActionAround",
        ["start_at", "end_at", "entity_id", "entity_id2", "text"],
        {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "var_object_who_unload": {"type": "string"},
                "var_object_unloaded": {"type": "string"}
            },
            "required": ["var_object_who_unload", "var_object_unloaded"]
        }
    )

    def __new__(cls, value, classname, attributes, schema):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.classname = classname
        obj.attributes = attributes
        obj.schema = schema
        return obj

    def get_attributes(self):
        return self.attributes

    def get_classname(self):
        return self.classname

    def get_schema(self):
        return self.schema