from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import time
import random
import math


class Node:

    def __init__(self, x, y, radius):
        self.x = x  # 节点的x坐标
        self.y = y  # 节点的y坐标
        self.radius = radius  # 节点的半径
        self.color = 'blue'  # 节点的颜色，默认为蓝色
        self.station = None  # 节点分配的基站，默认为 None

    def move(self, dest_x, dest_y):
        # 将节点移动到目标坐标(dest_x, dest_y)
        self.x = dest_x
        self.y = dest_y

    def set_color(self, color):
        # 设置节点颜色
        self.color = color

    def assign_station(self, station):
        # 为节点分配基站
        self.station = station

    def get_distance_to_station(self):
        # 获取节点与分配的基站之间的距离
        if self.station is None:
            return None
        dx = self.station.x - self.x
        dy = self.station.y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        return distance

    def draw(self, qp):
        # 绘制节点
        qp.setBrush(QColor(self.color))
        qp.drawEllipse(self.x - self.radius, self.y - self.radius,
                       2 * self.radius, 2 * self.radius)

    def update(self, dest_x, dest_y, speed, update_interval, qp):
        # 更新节点位置，并在界面上显示
        dx = dest_x - self.x
        dy = dest_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        steps = int(distance / speed)
        if steps == 0:
            self.move(dest_x, dest_y)
            self.draw(qp)
            return
        x_step = dx / steps
        y_step = dy / steps
        for i in range(steps):
            self.move(self.x + x_step, self.y + y_step)
            self.draw(qp)
            QApplication.processEvents()
            time.sleep(update_interval / 1000)
        self.move(dest_x, dest_y)
        self.draw(qp)


class Station:

    def __init__(self, x, y, radius):
        self.x = x  # 基站的x坐标
        self.y = y  # 基站的y坐标
        self.radius = radius  # 基站的半径
        self.color = 'red'  # 基站的颜色，默认为红色

    def set_color(self, color):
        # 设置基站颜色
        self.color = color

    def draw(self, qp):
        # 绘制基站
        qp.setBrush(QColor(self.color))
        qp.drawEllipse(self.x - self.radius, self.y - self.radius,
                       2 * self.radius, 2 * self.radius)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # 窗口标题和大小
        self.setWindowTitle('演示系统')
        self.setFixedSize(1200, 1000)

        # 初始化演示区域
        self.nodes: list[Node] = []
        self.stations: list[Station] = []
        self.init_demo_area(1000, 1000, 20)

        # 初始化参数栏
        self.init_parameters()
        # self.create_parameter_box()

    def init_demo_area(self, width, height, grid_size):
        # 初始化演示区域
        self.demo_area_width = width
        self.demo_area_height = height
        self.grid_size = grid_size

        # 初始化网格
        self.grid = []
        for i in range(0, self.demo_area_width, self.grid_size):
            row = []
            for j in range(0, self.demo_area_height, self.grid_size):
                row.append((i, j))
            self.grid.append(row)

        # 随机生成基站和节点
        self.generate_stations(10)
        self.generate_nodes(50)

    def init_parameters(self):
        # 初始化参数栏
        self.parameter_widget = QWidget(self)
        self.parameter_widget.setGeometry(1010, 0, 200, 1000)

        self.parameter_grid = QGridLayout()
        self.parameter_grid.setSpacing(20)

        # 初始化输入框
        self.width_label = QLabel('演示区域长度:', self.parameter_widget)
        self.parameter_grid.addWidget(self.width_label, 0, 0)
        self.width_input = QLabel(str(self.demo_area_width),
                                  self.parameter_widget)
        self.parameter_grid.addWidget(self.width_input, 0, 1)

        self.height_label = QLabel('演示区域宽度:', self.parameter_widget)
        self.parameter_grid.addWidget(self.height_label, 1, 0)
        self.height_input = QLabel(str(self.demo_area_height),
                                   self.parameter_widget)
        self.parameter_grid.addWidget(self.height_input, 1, 1)

        self.station_label = QLabel('基站数量:', self.parameter_widget)
        self.parameter_grid.addWidget(self.station_label, 2, 0)
        self.station_input = QLabel(str(len(self.stations)),
                                    self.parameter_widget)
        self.parameter_grid.addWidget(self.station_input, 2, 1)

        self.node_label = QLabel('节点数量:', self.parameter_widget)
        self.parameter_grid.addWidget(self.node_label, 3, 0)
        self.node_input = QLabel(str(len(self.nodes)), self.parameter_widget)
        self.parameter_grid.addWidget(self.node_input, 3, 1)

        # 添加参数栏到窗口中
        self.parameter_widget.setLayout(self.parameter_grid)

    def generate_stations(self, count):
        # 在演示区域中随机生成 count 个基站
        for i in range(count):
            x = random.randint(0, self.demo_area_width)
            y = random.randint(0, self.demo_area_height)
            station = Station(x, y, 10)
            self.stations.append(station)

    def generate_nodes(self, count):
        # 在演示区域中随机生成 count 个节点
        for i in range(count):
            x = random.randint(0, self.demo_area_width)
            y = random.randint(0, self.demo_area_height)
            node = Node(x, y, 5)
            self.nodes.append(node)

        self.update()

    def paintEvent(self, event):
        # 在界面上绘制元素
        painter = QPainter(self)
        painter.setPen(QPen(Qt.black, 1, Qt.SolidLine))

        # 绘制网格
        for i in range(len(self.grid)):
            for j in range(len(self.grid[i])):
                x, y = self.grid[i][j]
                painter.drawRect(x, y, self.grid_size, self.grid_size)

        # 绘制基站
        for station in self.stations:
            painter.setBrush(QColor(255, 0, 0))
            painter.drawEllipse(station.x - station.radius,
                                station.y - station.radius, station.radius * 2,
                                station.radius * 2)

        # 绘制节点
        for node in self.nodes:
            painter.setBrush(QColor(0, 0, 255))
            painter.drawEllipse(node.x - node.radius, node.y - node.radius,
                                node.radius * 2, node.radius * 2)

    def create_parameter_box(self):
        # 创建参数栏容器
        self.parameter_box = QGroupBox("Parameters")
        self.parameter_box_layout = QVBoxLayout()

        # 添加输入框及标签
        label1 = QLabel("Area Length:")
        self.input1 = QLineEdit("1000")
        label1.setBuddy(self.input1)
        hbox1 = QHBoxLayout()
        hbox1.addWidget(label1)
        hbox1.addWidget(self.input1)

        label2 = QLabel("Area Width:")
        self.input2 = QLineEdit("1000")
        label2.setBuddy(self.input2)
        hbox2 = QHBoxLayout()
        hbox2.addWidget(label2)
        hbox2.addWidget(self.input2)

        label3 = QLabel("Number of Stations:")
        self.input3 = QLineEdit("3")
        label3.setBuddy(self.input3)
        hbox3 = QHBoxLayout()
        hbox3.addWidget(label3)
        hbox3.addWidget(self.input3)

        label4 = QLabel("Number of Nodes:")
        self.input4 = QLineEdit("10")
        label4.setBuddy(self.input4)
        hbox4 = QHBoxLayout()
        hbox4.addWidget(label4)
        hbox4.addWidget(self.input4)

        # 将输入框添加到参数栏中
        self.parameter_box_layout.addLayout(hbox1)
        self.parameter_box_layout.addLayout(hbox2)
        self.parameter_box_layout.addLayout(hbox3)
        self.parameter_box_layout.addLayout(hbox4)
        self.parameter_box.setLayout(self.parameter_box_layout)

        # 将参数栏添加到主窗口中
        self.layout.addWidget(self.parameter_box, 0, 1, 2, 1)

    def update_node_positions(self):
        for node in self.nodes:
            # node.move()
            node.update()

    def start_simulation(self):
        self.generate_stations(self.input3)
        self.generate_nodes(self.input4)

        timer = QTimer(self)
        timer.timeout.connect(self.update_node_positions)
        timer.start(1000)


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
