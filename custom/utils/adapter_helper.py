from typing import Tuple

from ..business.domain_problem_model import DomainProblemModel
from ..constants.pddl_yaml import DEFAULT_ANIMATION_DURATION
from ..enums.predicat_mapping import PredicatMapping


class AdapterHelper:

    @staticmethod
    def adapt_object_type(data: dict) -> dict:
        data_parsed = {}
        for key, value in data.items():
            data_parsed[value] = {
                "sprite": "default_sprite.png",
            }
        return data_parsed

    @staticmethod
    def adapt_actions(data: dict[str, list[Tuple[str,str]]]) -> dict:
        data_parsed = {}
        for action in data:
            data_parsed[action] = {
                "duration": DEFAULT_ANIMATION_DURATION,
                "animations": [
                    {
                        "name": "",
                        "start_at": 0,
                        "end_at": DEFAULT_ANIMATION_DURATION,
                        "entity_vars": list(map(AdapterHelper.extract_var_from_action, data[action]))
                    }
                ],
            }
        return data_parsed

    @staticmethod
    def extract_var_from_action(val: Tuple[str,str]):
        return val[0]

    @staticmethod
    def adapt_predicats(data: dict[str, list[tuple[str,str]]]) -> dict:
        data_parsed = {}
        at_predicats = data.get("at")
        if at_predicats and len(at_predicats) > 1:
            data_parsed["at"] = {
                "type": PredicatMapping.POSITION.value,
                "mobile_var": at_predicats[0][0],
                "fixed_var": at_predicats[1][0],
            }
        return data_parsed


    @staticmethod
    def domain_problem_to_yaml_data_config(domain_problem_model: DomainProblemModel) -> object:
        data = {
            "object_types": AdapterHelper.adapt_object_type(domain_problem_model.get_objects()),
            "init_predicats": AdapterHelper.adapt_predicats(domain_problem_model.get_predicates()),
            "actions": AdapterHelper.adapt_actions(domain_problem_model.get_action_parameters()),
            "fixed_position": []
        }
        return data