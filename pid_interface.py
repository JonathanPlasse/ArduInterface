#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import (QWidget, QPushButton, QSpinBox, QDoubleSpinBox, QVBoxLayout, QLineEdit, QCheckBox, QSlider, QHBoxLayout, QFormLayout, QGroupBox, QApplication, QSizePolicy)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import yaml
from PyQt5 import QtCore
import threading
from binserial import BinSerial
from beautifulplot import BeautifulPlot

class PidInterface(QWidget):
    def __init__(self):
        super().__init__()
        self.init_parameters()
        self.init_ui()
        # self.init_serial()

    def init_serial(self):
        self.bser = BinSerial(self.port_name, self.baud_rate)

        self.read_thread = threading.Thread(target=self.read_variables, args=(self.bser, self.plot.time, self.plot.deque_position_input, self.plot.deque_position_setpoint, self.plot.deque_speed_input, self.plot.deque_speed_setpoint), daemon=True)
        self.read_thread.start()

    def init_parameters(self):
        with open('config.yml', 'r') as config_yml:
            config = yaml.safe_load(config_yml)
        self.port_name = config['port_name']
        self.baud_rate = config['baud_rate']
        self.kp = config['kp']
        self.ki = config['ki']
        self.kd = config['kd']
        self.sample_time = config['sample_time']
        self.max_setpoint = config['max_setpoint']
        self.mode = config['mode']
        self.anti_windup = config['anti_windup']

    def set_sample_time(self, new_sample_time):
        self.sample_time = new_sample_time

    def set_kp(self, new_kp):
        self.kp = new_kp

    def set_ki(self, new_ki):
        self.ki = new_ki

    def set_kd(self, new_kd):
        self.kd = new_kd

    def set_setpoint(self, new_setpoint):
        self.setpoint = new_setpoint
        self.sent_parameters()

    def set_mode(self, new_mode):
        self.mode = new_mode

    def set_anti_windup(self, new_anti_windup):
        self.anti_windup = new_anti_windup

    def init_ui(self):
        self.setWindowTitle('PidInterface')

        # Parameters
        self.sample_time_spin = QSpinBox()
        self.sample_time_spin.setMinimum(0)
        self.sample_time_spin.setMaximum(1000)
        self.sample_time_spin.setSuffix(' ms')
        self.sample_time_spin.setValue(self.sample_time)
        self.sample_time_spin.valueChanged.connect(self.set_sample_time)

        self.kp_spin = QDoubleSpinBox()
        self.kp_spin.setMinimum(0)
        self.kp_spin.setMaximum(float('inf'))
        self.kp_spin.setValue(self.kp)
        self.kp_spin.valueChanged.connect(self.set_kp)

        self.ki_spin = QDoubleSpinBox()
        self.ki_spin.setMinimum(0)
        self.ki_spin.setMaximum(float('inf'))
        self.ki_spin.setValue(self.ki)
        self.ki_spin.valueChanged.connect(self.set_ki)

        self.kd_spin = QDoubleSpinBox()
        self.kd_spin.setMinimum(0)
        self.kd_spin.setMaximum(float('inf'))
        self.kd_spin.setValue(self.kd)
        self.kd_spin.valueChanged.connect(self.set_kd)

        self.setpoint_slider = QSlider(QtCore.Qt.Horizontal)
        self.setpoint_slider.setMinimum(0)
        self.setpoint_slider.setMaximum(self.max_setpoint)
        self.setpoint_slider.setValue(0)
        self.setpoint_slider.sliderMoved.connect(self.set_setpoint)

        self.mode_check = QCheckBox()
        self.mode_check.setChecked(self.mode)
        self.mode_check.toggled.connect(self.set_mode)

        self.anti_windup_check = QCheckBox()
        self.anti_windup_check.setChecked(self.anti_windup)
        self.anti_windup_check.toggled.connect(self.set_anti_windup)

        parameters_layout = QFormLayout()
        parameters_layout.addRow('sample_time', self.sample_time_spin)
        parameters_layout.addRow('kp', self.kp_spin)
        parameters_layout.addRow('ki', self.ki_spin)
        parameters_layout.addRow('kd', self.kd_spin)
        parameters_layout.addRow('setpoint', self.setpoint_slider)
        parameters_layout.addRow('mode', self.mode_check)
        parameters_layout.addRow('anti_windup', self.anti_windup_check)

        parameters_group = QGroupBox('Parameters')
        parameters_group.setLayout(parameters_layout)

        apply_button = QPushButton('Apply')
        apply_button.clicked.connect(self.sent_parameters)

        pid_layout = QVBoxLayout()
        pid_layout.addWidget(parameters_group)
        pid_layout.addWidget(apply_button)
        pid_layout.addStretch()

        # Display
        self.plot = BeautifulPlot(self)

        # Main
        main_layout = QHBoxLayout()
        main_layout.addLayout(pid_layout)
        main_layout.addWidget(self.plot)

        self.setLayout(main_layout)

    def sent_parameters(self):
        """run the step response and get the measures"""
        # Write some data to the arduino
        self.bser.write(['uint32']+['float']*4+['bool']*2, [self.sample_time, self.kp, self.ki, self.kd, self.setpoint, self.mode, self.anti_windup])

    def read_variables(self, bser, time, deque_position_input, deque_position_setpoint, deque_speed_input, deque_speed_setpoint):
        i = 0
        while (True):
            i += 1
            position_input, position_setpoint, position_output, position_integral, speed_input, speed_setpoint, speed_output, speed_integral = bser.read(['float']*8)
            time.append(i)
            deque_position_input.append(position_input)
            deque_position_setpoint.append(position_setpoint)
            deque_speed_input.append(speed_input)
            deque_speed_setpoint.append(speed_setpoint)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    pid_interface = PidInterface()
    pid_interface.show()
    sys.exit(app.exec_())
