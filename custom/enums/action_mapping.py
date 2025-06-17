from enum import Enum

class ActionType(Enum):
    MOVE = (
        "move",
        "ActionMove",
        ["start_at", "end_at", "entity_id", "lat_from", "lon_from", "alti_from", "lat_to", "lon_to", "alti_to", "text"],
        {},
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
        },
        {
            "var_object_to_move": "entity_id",
            "var_object_destination": "entity_id2",
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
        },
        {
            "var_object": "entity_id",
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
        },
        {
            "var_object_start": "entity_id",
            "var_object_end": "entity_id2",
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
        },
        {
            "var_object_who_move": "entity_id",
            "var_object_center": "entity_id2",
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
        },
        {
            "var_object": "entity_id",
            "path_image": "image",
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
        },
        {
            "var_object": "entity_id",
            "path_image": "image",
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
        },
        {
            "var_object": "entity_id",
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
        },
        {
            "var_object": "entity_id",
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
        },
        {
            "var_object": "entity_id",
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
        },
        {
            "var_object": "entity_id",
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
        },
        {
            "var_object_who_load": "entity_id",
            "var_object_loaded": "entity_id2",
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
        },
        {
            "var_object_who_unload": "entity_id",
            "var_object_unloaded": "entity_id2",
        }
    )

    def __new__(cls, value, classname, attributes, schema, map_properties):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.classname = classname
        obj.attributes = attributes
        obj.schema = schema
        obj.map_properties = map_properties
        return obj

    def get_type_name(self):
        return self.value

    def get_attributes(self):
        return self.attributes

    def get_classname(self):
        return self.classname

    def get_schema(self):
        return self.schema

    def get_map_properties(self):
        return self.map_properties

    @classmethod
    def from_str(cls, type_str: str):
        for member in cls:
            if member.value == type_str:
                return member
        raise ValueError(f"Unknown ActionType: {type_str}")

    def get_mapping_value(self, attribute: str):
        return self.get_map_properties().get(attribute, attribute)