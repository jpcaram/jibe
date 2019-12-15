import tornado.ioloop
from webpy import MainApp
from webpy import Widget, Button, Input, HBox, VBox


class ExampleApp(MainApp):

    def __init__(self, connection):
        super().__init__(connection)

        self.button = Button()
        self.inbox = Input()
        self.inbox.value = 'The value'

        self.box1 = VBox()
        self.box1.children = [
            self.button,
            self.inbox
        ]

        self.children = [
            self.box1
        ]

        self.button.register('click', self.on_button_click)

    def on_inbox_change(self):
        pass

    def on_button_click(self, source):
        print(f'{self.__class__.__name__}.on_button_click()')
        self.inbox.value = "Hello!"


if __name__ == "__main__":
    # app = MainApp().make_app()
    app = ExampleApp.make_tornado_app()
    app.listen(8881)
    tornado.ioloop.IOLoop.current().start()
