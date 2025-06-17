import pytest
from custom.business.dm_carto_configuration_model import (
    DmCartoConfigurationModel,
    ObjectType,
    Predicate,
    Action,
    Animation,
    FixedPositionVar
)
from custom.enums.action_mapping import ActionType


def test_object_type_creation():
    obj = ObjectType(sprite="hero.png")
    assert obj.sprite == "hero.png"


def test_predicate_creation():
    pred = Predicate(type="position", mobile_var="?hero", fixed_var="?castle")
    assert pred.type == "position"
    assert pred.mobile_var == "?hero"
    assert pred.fixed_var == "?castle"


def test_fixed_position_var_creation():
    pos = FixedPositionVar(var="castle", x=1.0, y=2.0)
    assert pos.var == "castle"
    assert pos.x == 1.0
    assert pos.y == 2.0


def test_animation_valid_creation():
    anim = Animation(
        action_type=ActionType.MOVE_TO,
        start_at=0,
        end_at=10,
        attributes={
            "var_object_to_move": "hero",
            "var_object_destination": "castle",
            "text": "Go!"
        }
    )
    assert anim.start_at == 0
    assert anim.attributes["var_object_to_move"] == "hero"


def test_animation_missing_required_field():
    with pytest.raises(ValueError, match="Attributes missing for MOVE_TO"):
        Animation(
            action_type=ActionType.MOVE_TO,
            start_at=0,
            end_at=10,
            attributes={"var_object_to_move": "hero"}  # manque destination
        )


def test_action_valid_creation():
    anim = Animation(
        action_type=ActionType.MOVE_TO,
        start_at=0,
        end_at=10,
        attributes={
            "var_object_to_move": "hero",
            "var_object_destination": "castle",
            "text": "Go!"
        }
    )
    action = Action(duration=10, animations=[anim])
    assert action.duration == 10
    assert len(action.animations) == 1


def test_action_no_animations_error():
    with pytest.raises(ValueError, match="'animations' must contain at least one Animation instance"):
        Action(duration=5, animations=[])


def test_model_validation_success():
    model = DmCartoConfigurationModel(
        object_types={"hero": ObjectType(sprite="hero.png")},
        init_predicats={"p1": Predicate(type="position", mobile_var="?hero", fixed_var="?castle")},
        actions={
            "a1": Action(duration=10, animations=[
                Animation(
                    action_type=ActionType.MOVE_TO,
                    start_at=0,
                    end_at=10,
                    attributes={
                        "var_object_to_move": "hero",
                        "var_object_destination": "castle",
                        "text": "Go!"
                    }
                )
            ])
        },
        fixed_position=[FixedPositionVar(var="castle", x=1.0, y=2.0)]
    )
    model.validate()  # ne lève pas d'erreur


def test_model_validation_error_missing_fields():
    model = DmCartoConfigurationModel()
    with pytest.raises(ValueError, match="'object_types' must have at least one entry"):
        model.validate()


def test_model_load_from_parsed_valid():
    data = {
        "object_types": {
            "hero": {"sprite": "hero.png"}
        },
        "init_predicats": {
            "at": {"type": "position", "mobile_var": "?hero", "fixed_var": "?castle"}
        },
        "actions": {
            "a1": {
                "duration": 10,
                "animations": [
                    {
                        "name": "move_to",
                        "start_at": 0,
                        "end_at": 10,
                        "var_object_to_move": "hero",
                        "var_object_destination": "castle",
                        "text": "Go!"
                    }
                ]
            }
        },
        "fixed_position": [
            {"var": "castle", "x": 1.0, "y": 2.0}
        ]
    }

    model = DmCartoConfigurationModel()
    model.load_from_parsed(data)

    assert "hero" in model.object_types
    assert "at" in model.init_predicats
    assert "a1" in model.actions
    assert isinstance(model.fixed_position[0], FixedPositionVar)


def test_get_sprite_url_by_object_type():
    model = DmCartoConfigurationModel(
        object_types={"robot": ObjectType(sprite="robot.png")}
    )
    assert model.get_sprite_url_by_object_type("robot") == "robot.png"
