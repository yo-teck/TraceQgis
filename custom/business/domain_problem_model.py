from pddlpy import DomainProblem
import re
from typing import Dict, List, Tuple

from .dm_carto_configuration_model import DmCartoConfigurationModel


class DomainProblemModel:
    configuration: DmCartoConfigurationModel | None = None

    def __init__(self, domain_path: str, problem_path: str, plan_path: str = None):
        self.domain_path = domain_path
        self.dp = DomainProblem(domain_path, problem_path)
        self._plan: List[Dict] = []

        # 1) Objects / types
        self.objects: Dict[str,str] = self.dp.worldobjects()

        # 2) States
        self.initial_state = [tuple(f.predicate) for f in self.dp.initialstate()]
        self.goal_state    = [tuple(g.predicate) for g in self.dp.goals()]

        # 3) Predicates
        self.predicates: Dict[str, List[Tuple[str,str]]] = self._parse_predicates()

        # 4) Actions and their parameters parsed from domain file
        self.action_parameters: Dict[str, List[Tuple[str,str]]] = self._parse_actions()

        # 5) Action names
        self.actions = list(self.action_parameters.keys())

        # 6) Load plan if provided
        if plan_path:
            self.load_plan(plan_path)

    def _parse_predicates(self) -> Dict[str, List[Tuple[str,str]]]:
        text = open(self.domain_path, encoding="utf-8").read()
        # Isoler la section :predicates jusqu'au début du premier :action
        try:
            start = text.index(':predicates') + len(':predicates')
            end = text.index('(:action', start)
            section = text[start:end]
        except ValueError:
            return {}
        preds: Dict[str, List[Tuple[str,str]]] = {}
        # Chaque prédicat est défini par (name params)
        for match in re.finditer(r"\(\s*([\w-]+)\s+([^\)]+)\)", section):
            name = match.group(1)
            params_str = match.group(2)
            vars_types: list[tuple[str,str]] = []
            # Parser chaque variable '-'
            for var_match in re.finditer(r"(\?[\w-]+)\s*-\s*([\w-]+)", params_str):
                var = var_match.group(1)
                typ = var_match.group(2)
                vars_types.append((var, typ))
            preds[name] = vars_types
        return preds

    def _parse_actions(self) -> dict[str, list[tuple[str,str]]]:
        text = open(self.domain_path, encoding="utf-8").read()
        pattern = re.compile(r"\(:action\s+([^\s]+).*?:parameters\s*\(([^\)]*)\)", re.S)
        actions: dict[str, list[tuple[str,str]]] = {}
        for name, params in pattern.findall(text):

            actions[name] = DomainProblemModel._parse_data_from_line(params)
        return actions

    @staticmethod
    def _parse_data_from_line(params) ->  list[tuple[str,str]]:
        vars_types: list[tuple[str, str]] = []
        parts = params.split("?")[1:]
        for part in parts:
            var, _, rest = part.partition("-")
            var = "?" + var.strip()
            typ = rest.strip().split()[0]
            vars_types.append((var, typ))
        return vars_types


    # Public getters
    def get_objects(self) -> Dict[str,str]: return self.objects
    def get_object_type(self,o:str) -> str: return self.objects.get(o)
    def get_initial_state(self) -> list[Tuple]: return self.initial_state
    def get_goal_state(self) -> list[tuple]: return self.goal_state
    def get_predicates(self) -> dict[str, list[tuple[str,str]]]: return self.predicates
    def get_action_parameters(self) -> dict[str, list[Tuple[str,str]]]: return self.action_parameters
    def get_actions(self) -> list[str]: return self.actions

    def load_plan(self, plan_content: str) -> None:
        self._plan.clear()
        pat = re.compile(r"^\s*\d+:\s*\(\s*([^\s()]+)((?:\s+[^\s()]+)*)\s*\)\s*(?:\[\d+\])?$")

        for line in plan_content.splitlines():
            line = line.strip()
            if not line:
                continue
            mo = pat.match(line)
            if not mo:
                print(f"⚠️ Ligne ignorée (non reconnue) : {line}")
                continue

            action = mo.group(1)
            args = mo.group(2).strip().split()
            self._plan.append({"action": action, "args": args})

    def get_execution_sequence(self) -> List[Dict]: return self._plan

    def save_configuration(self, data: DmCartoConfigurationModel) -> None:
        self.configuration = data

    def get_configuration(self) -> DmCartoConfigurationModel:
        return self.configuration

    def get_sprite_url_by_var(self, var: str) -> str:
        if self.configuration is None:
            raise ValueError("Pas de configuration chargée")

        return self.configuration.get_sprite_url_by_object_type(self.get_object_type(var))