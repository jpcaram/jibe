import tornado.ioloop
from webpy import MainApp
from webpy import Button, HBox, ProgressBar


class ExampleApp(MainApp):

    def __init__(self, connection):
        super().__init__(connection)

        self.button = Button()
        self.progress = ProgressBar()
        self.progress.value = 10

        self.box1 = HBox()
        self.box1.children = [
            self.button,
            self.progress
        ]

        self.children = [
            self.box1
        ]

        self.button.register('click', self.on_button_click)

    def on_button_click(self, source):
        print(f'{self.__class__.__name__}.on_button_click()')
        self.progress.value += 10


if __name__ == "__main__":
    app = ExampleApp.make_tornado_app()
    app.listen(8881)
    tornado.ioloop.IOLoop.current().start()
