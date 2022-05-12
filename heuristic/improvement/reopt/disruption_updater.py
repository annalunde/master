from datetime import timedelta, datetime


class DisruptionUpdater:
    def __init__(self, new_request_updater):
        self.new_request_updater = new_request_updater

    def update_route_plan(self, current_route_plan, disruption_type, disruption_info, sim_clock):

        if disruption_type == 0:
            # adding current position for each vehicle
            vehicle_clocks, artificial_depot = self.update_vehicle_clocks(
                current_route_plan, sim_clock, disruption_type, disruption_info)

            updated_route_plan = list(map(list, current_route_plan))

            self.new_request_updater.set_parameters(disruption_info)

        elif disruption_type == 1:
            updated_route_plan = self.update_with_delay(
                current_route_plan, disruption_info)

            # adding current position for each vehicle
            vehicle_clocks, artificial_depot = self.update_vehicle_clocks(
                updated_route_plan, sim_clock, disruption_type, disruption_info)

        elif disruption_type == 2:
            # adding current position for each vehicle
            vehicle_clocks, artificial_depot = self.update_vehicle_clocks(
                current_route_plan, sim_clock, disruption_type, disruption_info)

            updated_route_plan = list(map(list, current_route_plan))

            # update capacities
            updated_vehicle_route = self.update_capacities(
                updated_route_plan[disruption_info[0]
                                   ], disruption_info[1], disruption_info[2],
                updated_route_plan[disruption_info[0]][disruption_info[1]][5])

            updated_route_plan[disruption_info[0]] = updated_vehicle_route

            if artificial_depot:
                # remove dropoff node
                del updated_route_plan[disruption_info[0]][disruption_info[2]]
            else:
                # remove dropoff node
                del updated_route_plan[disruption_info[0]][disruption_info[2]]
                # remove pickup node
                del updated_route_plan[disruption_info[0]][disruption_info[1]]

        else:
            # no show
            # adding current position for each vehicle
            vehicle_clocks, artificial_depot = self.update_vehicle_clocks(
                current_route_plan, sim_clock, disruption_type, disruption_info)

            updated_route_plan = list(map(list, current_route_plan))

            # update capacities
            updated_vehicle_route = self.update_capacities(
                updated_route_plan[disruption_info[0]
                                   ], disruption_info[1], disruption_info[2],
                updated_route_plan[disruption_info[0]][disruption_info[1]][5])

            updated_route_plan[disruption_info[0]] = updated_vehicle_route

            # remove dropoff node
            del updated_route_plan[disruption_info[0]][disruption_info[2]]

        return updated_route_plan, vehicle_clocks, artificial_depot

    def update_with_delay(self, current_route_plan, disruption_info):
        delay_duration = disruption_info[2]
        route_plan = list(map(list, current_route_plan))
        route_plan[disruption_info[0]] = route_plan[disruption_info[0]][:disruption_info[1]] + \
            [(i[0], i[1]+delay_duration, i[2]+delay_duration, i[3], i[4], i[5])
             for i in route_plan[disruption_info[0]][disruption_info[1]:]]
        return route_plan

    @ staticmethod
    def recalibrate_solution(current_route_plan, disruption_info, still_delayed_nodes):
        route_plan = list(map(list, current_route_plan))
        for node in still_delayed_nodes:
            idx = next(i for i, (node_test, *_)
                       in enumerate(route_plan[disruption_info[0]]) if node_test == node)
            node_route = route_plan[disruption_info[0]][idx]
            d = timedelta(0)
            node_route = (node_route[0], node_route[1], d,
                          node_route[3], node_route[4], node_route[5])
            route_plan[disruption_info[0]][idx] = node_route

        return route_plan

    def update_vehicle_clocks(self, current_route_plan, sim_clock, disruption_type, disruption_info):
        artificial_depot = False

        # find index for next node after sim_clock and corresponding time of service
        vehicle_clocks = []
        for vehicle_route in current_route_plan:
            if len(vehicle_route) > 1:
                if vehicle_route[0][1] <= sim_clock:
                    prev_idx = 0
                    for idx, (node, time, deviation, passenger, wheelchair, _) in enumerate(vehicle_route):
                        if time <= sim_clock:
                            prev_idx = idx

                    if prev_idx == len(vehicle_route) - 1:
                        vehicle_clocks.append(sim_clock)

                    else:
                        next_idx = prev_idx + 1
                        vehicle_clocks.append(vehicle_route[next_idx][1])

                        if disruption_type == 2:
                            # check whether next node after sim_clock is the request that is cancelled
                            if current_route_plan[disruption_info[0]][disruption_info[1]] == vehicle_route[next_idx]:
                                artificial_depot = True

                else:
                    vehicle_clocks.append(sim_clock)

            else:
                vehicle_clocks.append(sim_clock)

        return vehicle_clocks, artificial_depot

    def update_capacities(self, vehicle_route, start_id, dropoff_id, request):
        vehicle_route_temp = [(i[0], i[1], i[2], i[3]-request["Number of Passengers"],
                              i[4]-request["Wheelchair"], i[5]) for i in vehicle_route[start_id:dropoff_id]]
        vehicle_route_result = vehicle_route[:start_id] + \
            vehicle_route_temp + vehicle_route[dropoff_id:]
        return vehicle_route_result

    def filter_route_plan(self, current_route_plan, vehicle_clocks, disruption_info):
        route_plan = list(map(list, current_route_plan))
        before_filtering = len(route_plan[disruption_info[0]])
        for idx in range(len(route_plan)):
            vehicle_route = route_plan[idx]
            vehicle_clock = vehicle_clocks[idx]
            filtered_vehicle_route = [
                i for i in vehicle_route if i[1] >= vehicle_clock]
            nodes = [int(n) for n, t, d, p, w,
                     _ in filtered_vehicle_route if n > 0]
            single_nodes = [i for i in nodes if nodes.count(i) == 1]
            if single_nodes:
                if len(single_nodes) == 1:
                    el_idx = next(i for i, (node_test, *_)
                                  in enumerate(route_plan[idx]) if node_test == single_nodes[0])
                    filtered_vehicle_route.insert(0, route_plan[idx][el_idx])
                else:
                    ordered_insertion_singles = []
                    for single in single_nodes:
                        el_idx = next(i for i, (node_test, *_)
                                      in enumerate(route_plan[idx]) if node_test == single)
                        ordered_insertion_singles.append(
                            (el_idx, route_plan[idx][el_idx]))
                    ordered_insertion_singles.sort(
                        key=lambda x: x[0], reverse=True)
                    for i in ordered_insertion_singles:
                        filtered_vehicle_route.insert(0, i[1])
            route_plan[idx] = filtered_vehicle_route if len(
                filtered_vehicle_route) else [(0, vehicle_clock, None, 0, 0, None)]
            if idx == disruption_info[0]:
                after_filtering = len(route_plan[disruption_info[0]])
        return route_plan, before_filtering - after_filtering
