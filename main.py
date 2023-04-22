import copy
from utils import *
import itertools
import random

random_list = list(itertools.product(range(1, 1000), range(1, 1000)))
asis_set1 = random.sample(random_list, 20)
asis_set2 = random.sample(random_list, 3)

Node_set = []
Station_set = []
for asis in asis_set1:
    Node_set.append(
        Node(asis[0], asis[1], random.randint(10, 300),
             random.randint(500, 2000)))
for asis in asis_set2:
    Station_set.append(Base_Staion(asis[0], asis[1]))
# print('Node_set:', Node_set)
print('Station_set:', Station_set)


def CSCO(Stations: list[Base_Staion], Nodes: list[Node]):
    while len(Nodes):
        print('Node_set:', Nodes, len(Nodes))
        temp_set = []
        for station in Stations:
            if len(station.node_set):
                station.initSchedule(station.node_set + Nodes)
                MMCS = min_margin_cost_schedule(station.optSchedule(),
                                                station.start_time,
                                                station.end_time)
                MMCS.append(station)
                temp_set.append(MMCS)
            else:
                station.initSchedule(Nodes)
                MMCS = min_margin_cost_schedule(station.optSchedule())
                MMCS.append(station)
                temp_set.append(MMCS)
        # print('temp_set:', temp_set)
        min_idx = get_min_radio_index(temp_set)
        min_ratio, min_idx_time_slot, min_idx_node_set, min_idx_station = temp_set[
            min_idx]
        min_idx_station.start_time = min_idx_time_slot[0]
        min_idx_station.end_time = min_idx_time_slot[1]
        station.node_set.extend(min_idx_node_set)
        # 剔除已指派的节点
        left_nodes = []
        for node in Nodes:
            if [node.x, node.y] not in [[n.x, n.y] for n in min_idx_node_set]:
                left_nodes.append(node)
        Nodes = left_nodes

    for station in Stations:
        print(len(station.node_set))
        # print(station.node_set)
        station.draw()

    return getTST(Stations)


def NCSA(Stations: list[Base_Staion], Nodes: list[Node]):
    for node in Nodes:
        s = node.getNS(Stations)
        s.node_set.append(node)

    for station in Stations:
        station.initSchedule(station.node_set)
        station.optSchedule()
        station.draw(station.schedule_set)

    return getTST(Stations)


def SOA(Stations: list[Base_Staion], Nodes: list[Node]):

    return


station = Base_Staion(asis_set2[0][0], asis_set2[0][1], Node_set)
station.initSchedule(station.node_set)
optScheduel = station.optSchedule()
# print('Initial Plan:\nBase Node:', station.base_node['plan'].move_time,
#       'Start Time:', station.start_time, '& End Time:', station.end_time)
# print('----------------------------------------------')
# WAO = station.waitAtOrigin()
# station.waitAtStation()
# station.draw(station.waitAtStation())

min_margin_cost_schedule(optScheduel)
station.draw(optScheduel)

# print("NCSA Algorithm Total Service time:",
#       NCSA(copy.deepcopy(Station_set), copy.deepcopy(Node_set)), "s")
# print("CSCO Algorithm Total Service time:",
#       CSCO(copy.deepcopy(Station_set), copy.deepcopy(Node_set)), "s")