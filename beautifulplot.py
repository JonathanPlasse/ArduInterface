#!/usr/bin/python3
# -*- coding: utf-8 -*-

from matplotlib.pyplot import plt
import collections

class BeautifulPlot:
    def __init__(self):
        fig = plt.figure()

        # Add subplots
        self.axes = {}

        # Add plots
        self.plots = {}

        self.nb_point = 1000

        # Declare queue
        self.time = collections.deque([0]*nb_point, nb_point)
        self.deques = {}

        # Declare plot data
        self.data = {}

    def add_subplot(self, pos, title, min, max):
        self.axes[pos] = fig.add_subplot(pos)
        self.axes[pos].set_title(title)
        self.axes[pos].legend()
        self.axes[pos].set_ylim(min, max)

    def add_plot(self, pos, label):
        self.plots[(pos, label)] = self.axes[pos].plot([], [], label=label)[0]
        self.deques[(pos, label)] = collections.deque([0]*self.nb_point, self.nb_point)
        self.data[(pos, label)] = [self.time, self.deques[(pos, label)]]

    def update_figure(self):
        for key in self.plots:
            self.plots[key].set_data(self.data[key])

        for key in self.axes:
            self.axes[key].relim()
            self.axes[key].autoscale_view(True,True,False)

        plt.show()
