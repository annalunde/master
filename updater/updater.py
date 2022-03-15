import copy
import pandas as pd
from decouple import config
from heuristic.construction.construction import ConstructionHeuristic
from heuristic.construction.heuristic_config import *
from simulation.simulator import Simulator


class Updater:
    def __init__(self):
        pass

    def update_route_plan(self, current_route_plan, disruption_type, disruption_info):
        updated_route_plan = copy.deepcopy(current_route_plan)

        if disruption_type == 'delay':
            pass
        elif disruption_type == 'cancel':
            # remove dropoff node
            del updated_route_plan[disruption_info[0]][disruption_info[2]]
            # remove pickup node
            del updated_route_plan[disruption_info[0]][disruption_info[1]]
        else:
            # remove dropoff node
            del updated_route_plan[disruption_info[0]][disruption_info[2]]

        return updated_route_plan


def main():
    updater = None

    try:
        # CONSTRUCTION OF INITIAL SOLUTION
        df = pd.read_csv(config("test_data_construction"))
        constructor = ConstructionHeuristic(requests=df.head(20), vehicles=V)
        print("Constructing initial solution")
        current_route_plan, initial_objective, infeasible_set = constructor.construct_initial()

        # SIMULATION
        sim_clock = datetime.strptime("2021-05-10 10:00:00", "%Y-%m-%d %H:%M:%S")
        # første runde av simulator må kjøre med new requests fra data_processed_path for å få fullstendig antall
        # requests første runde, deretter skal rundene kjøre med data_simulator_path for å få updated data
        simulator = Simulator(sim_clock)
        disruption_type, disruption_time, disruption_info = simulator.get_disruption(current_route_plan,
                                                                                     config("data_processed_path"))

        print(disruption_type)
        print(disruption_info)
        # UPDATE ROUTE PLAN
        updater = Updater()
        updated_route_plan = updater.update_route_plan(current_route_plan, disruption_type, disruption_info)

    except Exception as e:
        print("ERROR:", e)


if __name__ == "__main__":
    main()