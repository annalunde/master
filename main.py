import pandas as pd
from decouple import config
import sys
import numpy.random as rnd
import traceback
import cProfile
from profiling.profiler import Profile
from heuristic.construction.construction import ConstructionHeuristic
from heuristic.improvement.alns import ALNS
from config.main_config import *
from heuristic.improvement.initial.initial_operators import Operators
from heuristic.improvement.reopt.reopt_operators import ReOptOperators
from heuristic.improvement.simulated_annealing import SimulatedAnnealing
from simulation.simulator import Simulator
from heuristic.improvement.reopt.disruption_updater import DisruptionUpdater
from heuristic.improvement.reopt.new_request_updater import NewRequestUpdater


def main():
    constructor, simulator = None, None

    try:

        # CONSTRUCTION OF INITIAL SOLUTION
        df = pd.read_csv(config("test_data_construction"))
        constructor = ConstructionHeuristic(requests=df.head(R), vehicles=V)
        print("Constructing initial solution")
        initial_route_plan, initial_objective, initial_infeasible_set = constructor.construct_initial()
        constructor.print_new_objective(
            initial_route_plan, initial_infeasible_set)

        # IMPROVEMENT OF INITIAL SOLUTION
        random_state = rnd.RandomState()

        criterion = SimulatedAnnealing(
            start_temperature, end_temperature, cooling_rate)

        alns = ALNS(weights, reaction_factor, initial_route_plan, initial_objective, initial_infeasible_set, criterion,
                    destruction_degree, constructor, rnd_state=rnd.RandomState())

        operators = Operators(alns)

        alns.set_operators(operators)

        # Run ALNS
        delayed = (False, None, None)

        current_route_plan, current_objective, current_infeasible_set, _ = alns.iterate(
            iterations, None, None, None, delayed)

        if current_infeasible_set:
            print(
                "Error: The service cannot serve the number of initial requests required")
            current_infeasible_set = []

        constructor.print_new_objective(
            current_route_plan, current_infeasible_set)

        # Recalibrate current solution
        current_route_plan = constructor.recalibrate_solution(
            current_route_plan)

        delta_dev_objective = constructor.get_delta_objective(
            current_route_plan, [], current_objective)

        print("Change in objective based on recalibration of deviation",
              delta_dev_objective)

        # SIMULATION
        print("Start simulation")
        sim_clock = datetime.strptime(
            "2021-05-10 10:00:00", "%Y-%m-%d %H:%M:%S")
        simulator = Simulator(sim_clock)
        new_request_updater = NewRequestUpdater(
            constructor)
        disruption_updater = DisruptionUpdater(new_request_updater)
        first_iteration, rejected = True, []
        print("Length of disruption stack", len(simulator.disruptions_stack))
        while len(simulator.disruptions_stack) > 0:
            prev_inf_len = len(current_infeasible_set)
            delayed, delay_deltas = (False, None, None), []
            i = 0
            prev_objective = current_objective

            # use correct data path
            if not first_iteration:
                disruption_type, disruption_time, disruption_info = simulator.get_disruption(
                    current_route_plan, config("data_simulator_path"), first_iteration)
            else:
                disruption_type, disruption_time, disruption_info = simulator.get_disruption(
                    current_route_plan, config("data_processed_path"), first_iteration)
                first_iteration = False

            print("Disruption type", disruption_type)
            print("Disruption time:", disruption_time)
            print()
            # updates before heuristic
            disrupt = (False, None)
            if disruption_type == 4:  # No disruption
                continue
            elif disruption_type == 0:  # Disruption: new request
                current_route_plan, vehicle_clocks = disruption_updater.update_route_plan(
                    current_route_plan, disruption_type, disruption_info, disruption_time)
                current_route_plan = disruption_updater.filter_route_plan(
                    current_route_plan, vehicle_clocks)  # Filter route plan
                current_route_plan, current_objective, current_infeasible_set, vehicle_clocks, rejection, rid = new_request_updater.\
                    greedy_insertion_new_request(
                        current_route_plan, current_infeasible_set, disruption_info, disruption_time, vehicle_clocks, i)
                if rejection:
                    rejected.append(rid)
                    current_objective = prev_objective
                    for i in range(1, N_R+1):
                        current_route_plan, current_objective, current_infeasible_set, vehicle_clocks, rejection, rid = new_request_updater.\
                            greedy_insertion_new_request(
                                current_route_plan, current_infeasible_set, disruption_info, disruption_time, vehicle_clocks, i)
                        if not rejection:
                            rejected.remove(rid)
                            break

            else:
                current_route_plan, vehicle_clocks = disruption_updater.update_route_plan(
                    current_route_plan, disruption_type, disruption_info, disruption_time)
                current_route_plan = disruption_updater.filter_route_plan(
                    current_route_plan, vehicle_clocks)  # Filter route plan
                current_objective = new_request_updater.new_objective(
                    current_route_plan, current_infeasible_set)
                if disruption_type == 2 or disruption_type == 3:  # Disruption: cancel or no show
                    index_removed = [(disruption_info[3], disruption_info[0], disruption_info[1]),
                                     (disruption_info[4], disruption_info[0], disruption_info[2])]
                    disrupt = (True, index_removed)
                elif disruption_type == 1:  # Disruption: delay
                    delayed = (True, disruption_info[0], disruption_info[1])
                    delay_deltas.append(current_objective)

            # Heuristic
            alns = ALNS(weights, reaction_factor, current_route_plan, current_objective, current_infeasible_set,
                        criterion,
                        destruction_degree, new_request_updater, random_state)

            operators = ReOptOperators(alns, disruption_time, vehicle_clocks)

            alns.set_operators(operators)

            # Run ALNS
            current_route_plan, current_objective, current_infeasible_set, still_delayed_nodes = alns.iterate(
                iterations, disrupt[0], disrupt[1], disruption_time, delayed)
            if delayed[0]:
                delay_deltas[-1] = delay_deltas[-1] - current_objective
                print("Reduction in objective of delay: ", delay_deltas[-1])
                current_route_plan = disruption_updater.recalibrate_solution(
                    current_route_plan, disruption_info, still_delayed_nodes)

            if disruption_type == 0 and not(len(current_infeasible_set) > prev_inf_len):
                print("New request inserted")

            new_request_updater.print_new_objective(
                current_route_plan, current_infeasible_set)

        print("End simulation")
        print("Rejected rids", rejected)

    except Exception as e:
        print("ERROR:", e)
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        full_traceback = traceback.format_exc()
        print("FULL TRACEBACK: ", full_traceback)

        print("Exception type: ", exception_type)
        print("File name: ", filename)
        print("Line number: ", line_number)


if __name__ == "__main__":
    profile = Profile()
    cProfile.run('main()', 'profiling/restats')
    profile.display()
    main()
