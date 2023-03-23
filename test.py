import copy
import itertools
import math
import random


class Node:

    def __init__(self, x=0, y=0, power=1000, target=10800, ddl=4000):
        self.x = x
        self.y = y
        self.ddl = ddl
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

    def __init__(self, node: Node, move_time, charge_time, ddl):
        self.node = node
        self.move_time = move_time
        self.charge_time = charge_time
        self.total = move_time + charge_time
        self.ddl = ddl
        self.origin_wait = 0
        self.station_wait = 0

    def __repr__(self) -> str:
        return '<MoveTime:' + str(self.move_time) + '|ChargeTime:' + str(
            self.charge_time) + '|Total:' + str(self.total) + '>'


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
                        (node.target - node.power) / self.charging_power,
                        node.ddl)

            if plan.move_time < self.start_time:
                self.start_time = plan.move_time
            if plan.total > self.end_time:
                self.base_node = {'info': node, 'plan': plan}
                self.end_time = plan.total

            self.schedule_set.append(plan)
        return self.base_node

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
            plan.ddl = round(plan.ddl - plan.move_time * 2 - plan.charge_time)
            if plan.ddl < 0:
                plan.ddl = round(plan.move_time * 2 - plan.charge_time)
            for t in range(1, plan.ddl):
                if plan.total + (self.charging_power /
                                 plan.node.ouput_power) * t <= self.end_time:
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

        return [self.getOverlapTime(p) for p in schedule_set]

    def waitAtStation(self):
        schedule_set: list[Plan] = copy.deepcopy(self.schedule_set)
        for plan in schedule_set:
            plan.ddl = round(plan.ddl - plan.move_time * 2 - plan.charge_time)
            if plan.ddl < 0:
                plan.ddl = round(plan.move_time * 2 - plan.charge_time)
            for t in range(1, plan.ddl):
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

        return [self.getOverlapTime(p) for p in schedule_set]

    def synthesizeWait(self):
        schedule_set: list[Plan] = copy.deepcopy(self.schedule_set)
        for plan in schedule_set:
            plan.ddl = round(plan.ddl - plan.move_time * 2 - plan.charge_time)
            if plan.ddl < 0:
                plan.ddl = round(plan.move_time * 2 - plan.charge_time)
            for t1 in range(1, plan.ddl):
                if plan.total + 11 * t1 <= self.end_time:
                    plan.origin_wait = 10 * t1
                else:
                    for t2 in range(1, plan.ddl - t1):
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

        return [self.getOverlapTime(p) for p in schedule_set]


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
print('Initial Plan:\nStart Time:', station.start_time, '& End Time:',
      station.end_time)
# print('Overlap Set:', station.getOverlapSet())
station.getOverlapSet()
# print('----------------------------------------------')
# print('Overlap Set(wait at origin):', station.waitAtOrigin())
station.waitAtStation()
station.waitAtOrigin()
station.synthesizeWait()