#!/usr/bin/python3
# -*- coding: utf-8 -*-

import yaml
import threading
from binserial import BinSerial
from beautifulplot import BeautifulPlot

class SerialInterface:
    def __init__(self):
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

        self.serial = config['serial']
        self.port_name = config['port_name']
        self.baud_rate = config['baud_rate']



    def init_ui(self):
        self.plot = BeautifulPlot(self)

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
    SerialInterface()
