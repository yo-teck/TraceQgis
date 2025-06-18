from typing import Tuple

from ..business.dm_carto_configuration_model import Predicate, Action, Animation
from ..business.domain_problem_model import DomainProblemModel
from ..business.map_entity import MapEntity
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

    @staticmethod
    def domain_problem_to_map_entity(dp: DomainProblemModel) -> list[MapEntity]:
        if dp.get_configuration() is None:
            raise ValueError("Pas de configuration d'importer")
        configuration = dp.get_configuration()
        list_entities = []
        for fixed_var in configuration.fixed_position:
            if fixed_var is not str:
                list_entities.append(MapEntity(fixed_var.var, fixed_var.var, dp.get_sprite_url_by_var(fixed_var.var), fixed_var.y, fixed_var.x))
            #todo: Ajouter un traitement pour les string

        for init_predicat_key in configuration.init_predicats.keys(): #at: Object
            init_predicat_value = configuration.init_predicats[init_predicat_key]
            if init_predicat_value.type == PredicatMapping.POSITION.value:
                AdapterHelper.add_predicat_position_to_map_entity_list(init_predicat_key, init_predicat_value, list_entities, dp)

        return list_entities

    @staticmethod
    def add_predicat_position_to_map_entity_list(init_predicat_key: str, init_predicat_value: Predicate, list_entities: list[MapEntity] ,dp: DomainProblemModel) -> None:
        all_init_predicat = [init for init in dp.initial_state if init[0] == init_predicat_key]  # ('at', 'var1', 'pos1')
        params_predicat = dp.get_predicates()[init_predicat_key]  # preds["at"] == [('?obj', 'physobj'), ('?loc', 'place')]
        index_fixed_var = next((i for i, t in enumerate(params_predicat) if t[0] == init_predicat_value.fixed_var),-1) + 1
        index_mobile_var = next((i for i, t in enumerate(params_predicat) if t[0] == init_predicat_value.mobile_var),-1) + 1

        for init_predicat in all_init_predicat:
            # Récupération de la fixed_var
            var_name_fixed = init_predicat[index_fixed_var]
            fixed_entity = next((x for x in list_entities if x.id == var_name_fixed), None)
            if fixed_entity is None:
                raise ValueError("Pas de variable trouvé à ce nom")
            var_name_mobile = init_predicat[index_mobile_var]
            list_entities.append(MapEntity(var_name_mobile, var_name_mobile, dp.get_sprite_url_by_var(var_name_mobile), fixed_entity.get_latitude(), fixed_entity.get_longitude()))

    @staticmethod
    def domain_problem_to_actions(domain_problem_model: DomainProblemModel) -> list[Action]:
        execution_sequences = domain_problem_model.get_execution_sequence()
        configuration = domain_problem_model.get_configuration()
        actions = []
        time = 0 #Init
        for an_exec in execution_sequences:
            current_action = configuration.actions.get(an_exec["action"])
            if current_action is None:
                continue
            for animation in current_action.animations:
                actions.append(AdapterHelper.animation_to_action(an_exec, animation, time, domain_problem_model))
            time += current_action.duration
        return actions


    @staticmethod
    def animation_to_action(an_exec: dict, animation: Animation, start_time: int, domain_problem: DomainProblemModel )-> dict:
        action = {
            "type": animation.action_type.get_type_name(),
            "start_at": start_time + animation.start_at,
            "end_at": start_time + animation.end_at,
        }

        for attribute in animation.attributes:
            value_attribute = animation.attributes[attribute]
            if attribute.startswith("var_"):
                action_dp = domain_problem.get_action_parameters().get(an_exec["action"])
                if action_dp is None:
                    raise ValueError("Action " + an_exec["action"] + " non trouvé dans le domain problem")
                index_var = next((i for i, t in enumerate(action_dp) if t[0] == value_attribute), -1)
                value_attribute = an_exec["args"][index_var]

            action[animation.action_type.get_mapping_value(attribute)] = value_attribute

        return action