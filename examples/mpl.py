import tornado.ioloop
from webpy import MainApp
from webpy import Widget, Button, Input, HBox, VBox, CheckBox, Label, Image
import matplotlib
matplotlib.use('AGG')
import matplotlib.pyplot as plt
from io import BytesIO, StringIO
import numpy as np
import base64


class MPLApp(MainApp):

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
    # app = MainApp().make_app()
    # app = MPLApp().make_app()
    app = MPLApp.make_tornado_app()
    app.listen(8881)
    tornado.ioloop.IOLoop.current().start()