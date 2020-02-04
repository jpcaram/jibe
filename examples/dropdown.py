import tornado.ioloop
from webpy import MainApp
from webpy import Input, HBox, VBox, Dropdown


class ExampleApp(MainApp):

    def __init__(self, connection):
        super().__init__(connection)

        self.dropdown = Dropdown(
            options=[
                'apples',
                'banannas',
                'chocolate'
            ]
        )

        self.children = [
            self.dropdown
        ]


if __name__ == "__main__":
    app = ExampleApp.make_tornado_app()
    app.listen(8881)
    tornado.ioloop.IOLoop.current().start()
