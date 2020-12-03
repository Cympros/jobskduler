# coding=utf-8

import sys

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtChart import QChartView, QLineSeries
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import PyQt5.QtChart

from PyQt5 import QtWidgets
import sys
import pyqtgraph


# 主窗口类
class MainWidget(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("瞎扯淡")  # 设置窗口标题
        data = [3, 6, 7, 8, 54, 3, 5, 3, 3, 3, 3]

        main_widget = QtWidgets.QWidget()  # 实例化一个widget部件
        main_layout = QtWidgets.QGridLayout()  # 实例化一个网格布局层
        main_widget.setLayout(main_layout)  # 设置主widget部件的布局为网格布局
        self.setCentralWidget(main_widget)  # 设置窗口默认部件为主widget

        pw = pyqtgraph.PlotWidget()  # 实例化一个绘图部件
        pw.plot(data, )  # 在绘图部件中绘制折线图
        main_layout.addWidget(pw)  # 添加绘图部件到网格布局层
        self.setCentralWidget(main_widget)  # 设置窗口默认部件为主widget


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    gui = MainWidget()
    gui.show()
    sys.exit(app.exec_())
