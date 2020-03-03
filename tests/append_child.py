import tornado.ioloop
from jibe import MainApp
from jibe import Button, Label


class ExampleApp(MainApp):

    def __init__(self, connection):
        super().__init__(connection)

        self.count = 0
        self.button = Button()
        self.children = [
            self.button,
        ]

        self.button.register('click', self.on_button_click)

    def on_button_click(self, source):
        print(f'{self.__class__.__name__}.on_button_click()')
        self.count += 1
        self.children.append(Label(value=f'{self.count}'))


if __name__ == "__main__":
    app = ExampleApp.make_tornado_app()
    app.listen(8881)
    tornado.ioloop.IOLoop.current().start()