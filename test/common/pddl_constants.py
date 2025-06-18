from custom.business.domain_problem_model import DomainProblemModel

LOGISTICS_DOMAIN = """
(define (domain logistics)
  (:requirements :strips :typing)
  (:types truck airplane - vehicle
          package
          vehicle - physobj
          airport
          location - place
          city
          place
          physobj - object)
  (:predicates
    (in-city ?loc - place ?city - city)
    (at ?obj - physobj ?loc - place)
    (in ?pkg - package ?veh - vehicle))
  (:action LOAD-TRUCK
    :parameters (?pkg - package ?truck - truck ?loc - place)
    :precondition (and (at ?truck ?loc) (at ?pkg ?loc))
    :effect (and (not (at ?pkg ?loc)) (in ?pkg ?truck)))
  (:action UNLOAD-TRUCK
    :parameters (?pkg - package ?truck - truck ?loc - place)
    :precondition (and (at ?truck ?loc) (in ?pkg ?truck))
    :effect (and (not (in ?pkg ?truck)) (at ?pkg ?loc)))
  (:action DRIVE-TRUCK
    :parameters (?truck - truck ?from - place ?to - place ?city - city)
    :precondition (and (at ?truck ?from) (in-city ?from ?city) (in-city ?to ?city))
    :effect (and (not (at ?truck ?from)) (at ?truck ?to)))
)
"""

LOGISTICS_PROBLEM = """
(define (problem logistics-problem)
  (:domain logistics)
  (:objects
    tru1 - truck
    pos1 pos2 - location
    cit1 cit2 - city
    obj1 - package)
  (:init
    (at tru1 pos1)
    (at obj1 pos1)
    (in-city pos1 cit1)
    (in-city pos2 cit1))
  (:goal (and (at obj1 pos2)))
)
"""

PLAN_CONTENT = """
0: (LOAD-TRUCK obj1 tru1 pos1)
1: (DRIVE-TRUCK tru1 pos1 pos2 cit1)
2: (UNLOAD-TRUCK obj1 tru1 pos2)
"""

def create_parser_for_test(tmp_path):
    domain_path = tmp_path / "domain.pddl"
    problem_path = tmp_path / "problem.pddl"

    domain_path.write_text(LOGISTICS_DOMAIN)
    problem_path.write_text(LOGISTICS_PROBLEM)

    # NOTE : le plan est passé directement en contenu (string)
    return DomainProblemModel(str(domain_path), str(problem_path), PLAN_CONTENT.strip())
