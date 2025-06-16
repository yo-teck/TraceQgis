from datetime import datetime
import os
import yaml
from typing import Any, Dict
from jsonschema import validate, ValidationError

from ..business.domain_problem_model import DomainProblemModel
from ..enums.action_mapping import ActionType
from ..utils.adapter_helper import AdapterHelper


class YamlHelper:

    @staticmethod
    def read_file(file_path: str, schema_path: str) -> Dict[str, Any]:
        """
        Lit et valide un fichier YAML avec un schéma JSON (en YAML ou JSON).

        :param file_path: Chemin du fichier YAML.
        :param schema_path: Chemin du fichier de schéma JSON/YAML.
        :return: Données YAML validées.
        :raises ValueError: Si extension, lecture ou validation échouent.
        """
        # 1. Vérifier l'extension
        if not file_path.lower().endswith(('.yaml', '.yml')):
            raise ValueError("Le fichier doit avoir une extension .yaml ou .yml")

        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"Fichier introuvable : {file_path}")

        # 2. Charger le fichier YAML
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                data = yaml.safe_load(f)
            except yaml.YAMLError as e:
                raise ValueError(f"Erreur de lecture YAML : {e}")

        # 3. Charger le schéma JSON (YAML ou JSON)
        if not os.path.isfile(schema_path):
            raise FileNotFoundError(f"Fichier de schéma introuvable : {schema_path}")

        with open(schema_path, 'r', encoding='utf-8') as f:
            try:
                schema = yaml.safe_load(f)  # fonctionne aussi avec JSON
            except yaml.YAMLError as e:
                raise ValueError(f"Erreur de lecture du schéma : {e}")

        # 4. Validation avec jsonschema
        try:
            validate(instance=data, schema=schema)
        except ValidationError as e:
            raise ValueError(f"Validation échouée : {e.message}")

        # 5. Validation des actions
        try:
            YamlHelper.validate_actions(data)
        except ValidationError as e:
            raise ValueError(f"Validation échouée : {e.message}")

        return data

    @staticmethod
    def validate_actions(data):
        for action in data['actions']:
            for animation in action['animations']:
                YamlHelper.validate_animation(animation)

    @staticmethod
    def validate_animation(animation):
        action_enum = YamlHelper.get_action_type_by_value(animation['name'])
        if action_enum is None:
            raise ValueError(f"Action type {animation['name']} n'est pas valide.")
        try:
            validate(instance=animation, schema=action_enum.schema)
        except ValidationError as e:
            raise ValueError(f"Validation échouée : {e.message}")

    @staticmethod
    def generate_template(domain_problem_model: DomainProblemModel, dir_path:str):
        now = datetime.now()
        path = os.path.join(dir_path, f"config-{now.timestamp()}.yml")
        with open(path, "w", encoding="utf-8") as f:
            yaml.safe_dump(
                AdapterHelper.domain_problem_to_yaml_data_config(domain_problem_model),
                f,
                default_flow_style=False,  # plus lisible, style indenté
                sort_keys=False  # conserve l'ordre des clés
            )


    @staticmethod
    def get_action_type_by_value(value: str) -> ActionType | None:
        for action in ActionType:
            if action.value == value:
                return action
        return None

