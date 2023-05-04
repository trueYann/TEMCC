import random

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPainter, QBrush, QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QSpinBox, QPushButton


class Node:

    def __init__(self, x, y, size, color):
        self.x = x
        self.y = y
        self.size = size
        self.color = color

    def draw(self, painter):
        painter.setBrush(QBrush(QColor(*self.color)))
        painter.drawEllipse(self.x, self.y, self.size, self.size)

    def move(self):
        pass  # To be implemented


class Station:

    def __init__(self, x, y, size, color):
        self.x = x
        self.y = y
        self.size = size
        self.color = color

    def draw(self, painter):
        painter.setBrush(QBrush(QColor(*self.color)))
        painter.drawRect(self.x, self.y, self.size, self.size)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("演示系统")
        self.setGeometry(100, 100, 1200, 1200)

        self.nodes = []
        self.stations = []

        self.label_node_count = QLabel("节点数量", self)
        self.label_node_count.move(20, 20)

        self.spin_box_node_count = QSpinBox(self)
        self.spin_box_node_count.move(100, 20)
        self.spin_box_node_count.setRange(1, 100)
        self.spin_box_node_count.setValue(10)

        self.label_station_count = QLabel("基站数量", self)
        self.label_station_count.move(20, 60)

        self.spin_box_station_count = QSpinBox(self)
        self.spin_box_station_count.move(100, 60)
        self.spin_box_station_count.setRange(1, 10)
        self.spin_box_station_count.setValue(2)

        self.start_button = QPushButton("开始", self)
        self.start_button.move(20, 100)
        self.start_button.clicked.connect(self.start_simulation)

        # 创建定时器，每隔10毫秒更新一次节点位置
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_nodes)
        self.timer.start(10)

    def paintEvent(self, event):
        painter = QPainter(self)

        # 绘制节点和基站
        for node in self.nodes:
            node.draw(painter)

        for station in self.stations:
            station.draw(painter)

    def update_nodes(self):
        # 更新节点位置
        for node in self.nodes:
            node.move()

        # 重绘界面
        self.update()

    def start_simulation(self):
        self.nodes = []
        self.stations = []
        node_count = self.spin_box_node_count.value()
        station_count = self.spin_box_station_count.value()

        # TODO: 根据节点数量和基站数量生成充电节点和基站
        for i in range(node_count):
            node = Node(random.randint(0, 1000), random.randint(0, 1000), 10,
                        (0, 0, 255))
            self.nodes.append(node)
        for i in range(station_count):
            station = Station(random.randint(0, 1000), random.randint(0, 1000),
                              50, (0, 255, 0))
            self.stations.append(station)

        # TODO: 根据给定算法分配基站并让节点移动


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
