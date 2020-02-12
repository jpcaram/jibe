import tornado.ioloop
from webpy import MainApp, WebSocketHandler
from webpy import Widget, Button, Input, HBox, VBox


class ExampleApp(MainApp):
    """
    The cookie 'sessionid' is checked and created if non-existent
    by MainHandler.get(), which is invoked when the body of the page
    is requested. I think it is not possible to set cookies via
    websockets and that is why it is done that way.

    At the time an instance of the MainApp exists, the 'sessionid'
    cookie must exist as well.
    """

    def __init__(self, connection):
        super().__init__(connection)

        self.button = Button()
        self.inbox = Input()

        self.box1 = HBox()
        self.box1.children = [
            self.button,
            self.inbox
        ]

        self.children = [self.box1]

        self.button.register('click', self.on_button_click)

    # def wsopen(self):
    #     """
    #     TODO: This may be redundant. So far, the constructor is called when
    #         the websocket opens, so everything that is done here can be done
    #         in the constructor.
    #     """
    #     print(f'{self.__class__.__name__}.wsopen() -- Set the value of the input box.')
    #     super().wsopen()
    #     self.inbox.value = self.connection.get_cookie('sessionid')

    def on_inbox_change(self):
        print(f'{self.__class__.__name__}.on_inbox_change()')

    def on_button_click(self, source):
        print(f'{self.__class__.__name__}.on_button_click()')

        self.inbox.value = f"{self.connection.get_cookie('sessionid')}"


if __name__ == "__main__":
    app = ExampleApp.make_tornado_app()
    app.listen(8881)
    tornado.ioloop.IOLoop.current().start()
