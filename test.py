import copy
import itertools
import math
import random


class Node:

    def __init__(self, x=0, y=0, power=1000, target=10800):
        self.x = x
        self.y = y
        self.ddl = random.randint(10, 1200)
        self.power = power
        self.target = target
        self.ouput_power = 0.5
        self.speed = 0.5

    def __repr__(self) -> str:
        return '(' + str(self.x) + ',' + str(self.y) + ')'

    def getX(self):
        return self.x

    def getY(self):
        return self.y


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
        return '<OW:' + str(self.origin_wait) + '|SW:' + str(
            self.station_wait) + '|Tol:' + str(self.total) + '>'


class Base_Staion:

    def __init__(self, x=0, y=0, nodes=None):
        self.x = x
        self.y = y
        self.node_set: list[Node] = nodes or []
        self.schedule_set = []
        self.overlap_set = []
        self.start_time = 1000000
        self.end_time = 0
        self.base_node = None
        self.charging_power = 5

    def getLen(self, p: Node):
        relative_x = self.x - p.getX()
        relative_y = self.y - p.getY()
        return math.sqrt(relative_x * relative_x + relative_y * relative_y)

    def initSchedule(self):
        for node in self.node_set:
            plan = Plan(node,
                        self.getLen(node) / node.speed,
                        (node.target - node.power) / self.charging_power)

            if plan.move_time < self.start_time:
                self.start_time = plan.move_time
            if plan.total > self.end_time:
                self.base_node = {'info': node, 'plan': plan}
                self.end_time = plan.total

            self.schedule_set.append(plan)

        return self.base_node

    def optSchedule(self):
        schedule_set: list[Plan] = copy.deepcopy(self.schedule_set)
        for plan in schedule_set:
            plan.dif_time = self.end_time - plan.total
            D = self.charging_power / plan.node.ouput_power

            # situation 1: charging_power / node.ouput_power * ddl <= △T
            if (D + 1) * plan.node.ddl <= plan.dif_time:
                plan.origin_wait = D * plan.node.ddl
                plan.charge_time += plan.node.ddl
                plan.total = plan.origin_wait + plan.move_time + plan.charge_time

            # situation 2: ddl≤ △T < charging_power / node.ouput_power * ddl
            elif plan.dif_time >= plan.node.ddl and plan.dif_time < (
                    D + 1) * plan.node.ddl:
                plan.origin_wait = plan.dif_time - plan.node.ddl
                plan.charge_time += plan.origin_wait / (self.charging_power /
                                                        plan.node.ouput_power)
                plan.station_wait = plan.node.ddl - plan.origin_wait / D
                plan.total = plan.origin_wait + plan.move_time + plan.station_wait + plan.charge_time

            # situation 3: ddl > △T
            elif plan.node.ddl > plan.dif_time:
                plan.station_wait = plan.dif_time
                plan.total += plan.station_wait

        st = 100000
        for plan in schedule_set:
            st = (plan.origin_wait + plan.move_time +
                  plan.station_wait) if (plan.origin_wait + plan.move_time +
                                         plan.station_wait) < st else st
        print('Final Schedule:\nStart Time:', st, '& End Time:',
              self.end_time)
        print(
            'Optimized ratio:',
            round((st - self.start_time) / (self.end_time - self.start_time) *
                  100, 2), '%')
        print('----------------------------------------------')
        return schedule_set

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

    def synthesizeWait(self):
        schedule_set: list[Plan] = copy.deepcopy(self.schedule_set)
        for plan in schedule_set:
            for t1 in range(1, plan.node.ddl):
                if plan.total + 11 * t1 <= self.end_time:
                    plan.origin_wait = 10 * t1
                else:
                    for t2 in range(1, plan.node.ddl - t1):
                        if plan.total + plan.origin_wait * 1.1 + t2 <= self.end_time:
                            plan.station_wait = t2
            plan.move_time += plan.origin_wait + plan.station_wait
            plan.charge_time += plan.origin_wait * 0.1
            plan.total = plan.charge_time + plan.move_time

        st = 100000
        for plan in schedule_set:
            st = plan.move_time if plan.move_time < st else st
        print('schedule_set after synthesize wait:\nStart Time:', st,
              '& End Time:', self.end_time)
        print(
            'Optimized ratio:',
            round((st - self.start_time) / (self.end_time - self.start_time) *
                  100, 2), '%')
        print('----------------------------------------------')

        # return [self.getOverlapTime(p) for p in schedule_set]


Node_set = []
random_list = list(itertools.product(range(1, 1000), range(1, 1000)))
asis_set = random.sample(random_list, 30)
for asis in asis_set:
    Node_set.append(Node(asis[0], asis[1]))

print('Node_set:', Node_set)
station = Base_Staion(500, 500, Node_set)

base_node = station.initSchedule()
# print('Base Node Coordinate:', base_node['info'].getX(),
#       base_node['info'].getY())
print('Initial Plan:\nBase Node:',station.base_node['plan'].move_time, 'Start Time:', station.start_time, '& End Time:',
      station.end_time)
# print('Overlap Set:', station.getOverlapSet())
# station.getOverlapSet()
print('----------------------------------------------')
# print('Overlap Set(wait at origin):', station.waitAtOrigin())
WAO = station.waitAtOrigin()
station.waitAtStation()
OPT = station.optSchedule()
# station.synthesizeWait()
# print(WAO)
# print(OPT)
