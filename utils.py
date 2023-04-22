import copy
import math

from matplotlib import pyplot as plt


class Node:

    def __init__(self, x=0, y=0, ddl=0, power=1000, target=10800):
        self.x = x
        self.y = y
        self.ddl = ddl
        self.power = power
        self.target = target
        self.ouput_power = 0.5  #W(瓦)
        self.speed = 0.5  #m/s
        self.free_time = 0

    def __repr__(self) -> str:
        return '(' + str(self.x) + ',' + str(self.y) + ')'

    def getX(self):
        return self.x

    def getY(self):
        return self.y

    def getNS(self, Staions):
        temp, ret = 100000000, None
        for staion in Staions:
            relative_x = self.x - staion.x
            relative_y = self.y - staion.y
            len = math.sqrt(relative_x * relative_x + relative_y * relative_y)
            if len < temp:
                temp = len
                ret = staion
        return ret


class Plan:

    def __init__(self, node: Node, move_time, charge_time):
        self.node = node
        self.move_time = move_time
        self.charge_time = charge_time
        self.total = move_time + charge_time
        self.origin_wait = 0
        self.station_wait = 0
        self.dif_time = 0

    def __repr__(self) -> str:
        return str(self.node)


class Base_Staion:

    def __init__(self, x=0, y=0, nodes=None):
        self.x = x
        self.y = y
        self.node_set: list[Node] = nodes or []
        self.schedule_set: list[Plan] = []
        self.schedule_set_nodes: list[Node] = []
        self.overlap_set = []
        self.start_time = float('inf')
        self.end_time = 0
        self.base_node = None
        self.charging_power = 5

    def __repr__(self) -> str:
        return '(Asis:' + str((self.x, self.y)) + ',ST:' + str(
            self.start_time) + ',ET:' + str(self.end_time) + ')'

    def getLen(self, p: Node):
        relative_x = self.x - p.getX()
        relative_y = self.y - p.getY()
        return math.sqrt(relative_x * relative_x + relative_y * relative_y)

    def initSchedule(self, Nodes: list[Node]):
        self.schedule_set = []
        self.schedule_set_nodes = []
        unChargedNodes = []
        node_set = copy.deepcopy(Nodes)
        for node in node_set:
            node.free_time = node.power / node.ouput_power - self.getLen(
                node) / node.speed
            if node.free_time >= 0:
                plan = Plan(node,
                            self.getLen(node) / node.speed,
                            (node.target - node.power) / self.charging_power)
                if plan.move_time < self.start_time:
                    self.start_time = plan.move_time
                if plan.total > self.end_time:
                    self.base_node = {'info': node, 'plan': plan}
                    self.end_time = plan.total
                self.schedule_set.append(plan)
                self.schedule_set_nodes.append(node)
            else:
                unChargedNodes.append(node)
        # if len(unChargedNodes): print("Exist uncharged nodes:", unChargedNodes)

    def getOverlapTime(self, plan: Plan) -> int:
        if plan.total < self.base_node['plan'].move_time:
            return 0

        return round(
            plan.total - self.base_node['plan'].move_time
            if plan.move_time < self.base_node['plan'].move_time else
            plan.charge_time, 2)

    def getOverlapSet(self):
        for plan in self.schedule_set:
            self.overlap_set.append(self.getOverlapTime(plan))

        return self.overlap_set

    def waitAtOrigin(self):
        schedule_set: list[Plan] = copy.deepcopy(self.schedule_set)
        for plan in schedule_set:
            for t in range(1, plan.node.ddl):
                if plan.total + (self.charging_power / plan.node.ouput_power +
                                 1) * t <= self.end_time:
                    plan.origin_wait = t
            plan.charge_time += plan.origin_wait
            plan.move_time += plan.origin_wait * 10
            plan.total = plan.charge_time + plan.move_time

        st = 100000
        for plan in schedule_set:
            st = plan.move_time if plan.move_time < st else st
        print('schedule_set after wait at origin:\nStart Time:', st,
              '& End Time:', self.end_time)
        print(
            'Optimized ratio:',
            round((st - self.start_time) / (self.end_time - self.start_time) *
                  100, 2), '%')
        print('----------------------------------------------')
        return schedule_set
        # return [self.getOverlapTime(p) for p in schedule_set]

    def waitAtStation(self):
        schedule_set: list[Plan] = copy.deepcopy(self.schedule_set)
        for plan in schedule_set:
            for t in range(1, plan.node.ddl):
                if plan.total + t <= self.end_time:
                    plan.station_wait = t
            plan.move_time += plan.station_wait
            plan.total = plan.charge_time + plan.move_time

        st = 100000
        for plan in schedule_set:
            st = plan.move_time if plan.move_time < st else st
        print('schedule_set after wait at station:\nStart Time:', st,
              '& End Time:', self.end_time)
        print(
            'Optimized ratio:',
            round((st - self.start_time) / (self.end_time - self.start_time) *
                  100, 2), '%')
        print('----------------------------------------------')
        return schedule_set
        # return [self.getOverlapTime(p) for p in schedule_set]

    def optSchedule(self):
        schedule_set: list[Plan] = copy.deepcopy(self.schedule_set)
        for plan in schedule_set:
            plan.dif_time = self.end_time - plan.total
            D = self.charging_power / plan.node.ouput_power
            if plan.node.free_time < plan.node.ddl * D:
                plan.node.ddl = plan.node.free_time / D
            # situation 1: All wait at origin
            # plan.origin_wait + extra_charge_time <= △T
            if (D + 1) * plan.node.ddl <= plan.dif_time:
                plan.origin_wait = D * plan.node.ddl
                plan.charge_time += plan.node.ddl
                plan.total = plan.origin_wait + plan.move_time + plan.charge_time

            # situation 2: Origin wait + Station wait
            # ddl≤ △T < charging_power / node.ouput_power * ddl
            elif plan.dif_time >= plan.node.ddl and plan.dif_time < (
                    D + 1) * plan.node.ddl:
                plan.origin_wait = plan.dif_time - plan.node.ddl
                plan.charge_time += plan.origin_wait / (self.charging_power /
                                                        plan.node.ouput_power)
                plan.station_wait = plan.node.ddl - plan.origin_wait / D
                plan.total = plan.origin_wait + plan.move_time + plan.station_wait + plan.charge_time

            # situation 3: All wait at station
            # ddl > △T
            elif plan.node.ddl > plan.dif_time:
                plan.station_wait = plan.dif_time
                plan.total += plan.station_wait

        st = 100000
        for plan in schedule_set:
            st = (plan.origin_wait + plan.move_time +
                  plan.station_wait) if (plan.origin_wait + plan.move_time +
                                         plan.station_wait) < st else st
        # print('----------------------------------------------')
        # print('Final Schedule:\nStart Time:', st, '& End Time:', self.end_time)
        # print(
        #     'Optimized ratio:',
        #     round((st - self.start_time) / (self.end_time - self.start_time) *
        #           100, 2), '%')
        # print('----------------------------------------------')
        self.schedule_set = schedule_set
        return schedule_set

    def draw(self, schedule: list[Plan]=[]):
        if len(schedule) == 0:
            self.initSchedule(self.node_set)
            schedule = self.optSchedule()
        x = [str(i) for i in schedule]
        y1 = [float(i.origin_wait) for i in schedule]
        y2 = [float(i.move_time) for i in schedule]
        y3 = [float(i.station_wait) for i in schedule]
        y4 = [float(i.charge_time) for i in schedule]
        plt.barh(x, y1, label='origin_wait')
        plt.barh(x, y2, left=y1, label='move_time')
        plt.barh(x,
                 y3,
                 left=[y1[i] + y2[i] for i in range(len(y1))],
                 label='station_wait')
        plt.barh(x,
                 y4,
                 left=[y1[i] + y2[i] + y3[i] for i in range(len(y1))],
                 label='charge_time')
        plt.legend()
        plt.show()


def getTST(Stations: list[Base_Staion]):
    ret = 0
    for s in Stations:
        if len(s.node_set) and s.end_time > 0:
            ret = ret + s.end_time - s.start_time
    return ret


def min_margin_cost_schedule(schedule: list[Plan],
                             base_start=float('inf'),
                             base_end=0):
    S = []
    for plan in schedule:
        if (plan.total -
                plan.charge_time) < base_start or plan.total > base_end:
            S.append((int(plan.total - plan.charge_time),
                      math.ceil(plan.total), plan.node))
    # print("S: ", S)
    min_ratio, node_set, time_slot = float('inf'), [], ()
    for start in list(set(s[0] for s in S)):
        for end in list(set(e[1] for e in S)):
            if end - start <= 0:
                pass
            else:
                temp, ratio = [], float('inf')
                for t in S:
                    if start <= t[0] and t[1] <= end:
                        temp.append(t[2])
                if base_end != 0:
                    ratio = ((end - base_end) + (base_start - start)
                             ) / len(temp) if len(temp) > 0 else float('inf')
                else:
                    ratio = (end - start) / len(temp) if len(
                        temp) > 0 else float('inf')

                if ratio < min_ratio:
                    min_ratio = ratio
                    node_set = temp
                    time_slot = (start, end)
    # print("min_ratio:", min_ratio, len(node_set))
    # print("return:", node_set, "\ntime slot:", time_slot)
    return [min_ratio, time_slot, node_set]


def get_min_radio_index(set):
    radio_set = [p[0] for p in set]
    min_radio = min(radio_set)
    return radio_set.index(min_radio)
