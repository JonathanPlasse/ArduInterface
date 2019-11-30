#!/usr/bin/python3
# -*- coding: utf-8 -*-

import yaml
import threading
from binserial import BinSerial
from easyplot import EasyPlot

class SerialInterface:
    def __init__(self):
        self.init_config()
        self.init_serial()

    def init_config(self):
        # Load configuration file
        with open('config.yml', 'r') as config_yml:
            config = yaml.safe_load(config_yml)

        # Store serial config
        self.serial = config['serial']

        # Initialise EasyPlot
        self.easyplot = EasyPlot()

        # Initialise the subplots
        for subplot in config['subplots']:
            self.easyplot.add_subplot(subplot['pos'], subplot['title'], subplot['min'], subplot['max'])

        # Initialise the plots for reading
        self.read_format = []
        self.plot_data = []
        for plot in config['data']['read']:
            self.read_format.append(plot['type'])
            self.plot_data.append(self.easyplot.add_plot(plot['pos'], plot['label']))
        # Initialise for writing
        self.write_format = []
        for widget in config['data']['write']:
            self.write_format.append(widget['type'])

    def init_serial(self):
        self.bser = BinSerial(self.serial['port'], self.serial['baud'])

        self.read_thread = threading.Thread(target=self.read_serial, args=(self.bser, self.read_format, self.plot_data), daemon=True)
        self.read_thread.start()

    def read_serial(self, bser, read_format, plot_data):
        i = 0
        while (True):
            i += 1
            data = bser.read(read_format)
            for j in range(len(read_format)):
                plot_data[j][0].append(i)
                plot_data[j][1].append(data[j])

            self.easyplot.update_figure()

    def write_serial(self):
        """run the step response and get the measures"""
        # Write some data to the arduino
        self.bser.write(['float'], [self.setpoint])


if __name__ == '__main__':
    SerialInterface()
