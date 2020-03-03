# Jibe
# A Full-Stack Pure-Python Web Framework.
# Copyright (c) 2020 Juan Pablo Caram
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import tornado.ioloop
from jibe import MainApp
from jibe import Widget, Button, Input, HBox, VBox, CheckBox, Label, Image
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO, StringIO
import numpy as np
import base64

matplotlib.use('AGG')


class MPLApp(MainApp):
    """
    Images and dynamic update. Specifically, we plot some curves
    using the Matplotlib plotting library.
    """

    def __init__(self, connection):
        super().__init__(connection)

        self.chart = Image()
        self.button1 = Button('Button 1')
        self.button2 = Button('Button 2')
        self.button3 = Button('Button 3')
        self.buttonbox = HBox()
        self.buttonbox.children = [
            self.button1, self.button2, self.button3
        ]

        self.button1.register('click', self.on_btn1)
        self.button2.register('click', self.on_btn2)
        self.button3.register('click', self.on_btn3)

        self.children = [
            self.chart,
            self.buttonbox
        ]

        self.figure, self.ax = plt.subplots(1, 1, figsize=(6, 4), dpi=100)

        x = np.linspace(0, 10, num=100)
        y = np.sin(x)
        image = BytesIO()
        self.ax.plot(x, y)
        self.ax.grid()
        self.figure.savefig(image, format='png')
        w, h = self.figure.get_size_inches() * self.figure.dpi
        self.chart.attr({'width': str(w), 'height': str(h)})
        self.chart.data = base64.encodebytes(image.getvalue()).decode('utf8')

    def on_btn1(self, source):
        self.ax.clear()
        x = np.linspace(0, 10, num=100)
        y = np.sin(2*x)
        image = BytesIO()
        self.ax.plot(x, y)
        self.ax.grid()
        self.figure.savefig(image, format='png')
        self.chart.data = base64.encodebytes(image.getvalue()).decode('utf8')

    def on_btn2(self, source):
        self.ax.clear()
        x = np.linspace(0, 10, num=100)
        y = np.sin(x)
        image = BytesIO()
        self.ax.plot(x, y)
        self.ax.grid()
        self.figure.savefig(image, format='png')
        self.chart.data = base64.encodebytes(image.getvalue()).decode('utf8')

    def on_btn3(self, source):
        w, h = self.figure.get_size_inches() * self.figure.dpi
        self.chart.attr({'width': str(w), 'height': str(h)})


if __name__ == "__main__":
    app = MPLApp.make_tornado_app()
    app.listen(8881)
    tornado.ioloop.IOLoop.current().start()