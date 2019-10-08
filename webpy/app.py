import tornado.web
import tornado.websocket
import json
from jinja2 import Template
from .widget import Widget, VBox
from .page import htmlt
from typing import List, Dict
from pathlib import Path


class MainHandler(tornado.web.RequestHandler):
    """
    Serves the top level html and core elements (javascript) of
    the application.
    """

    mainApp = None

    def get(self):

        body = "{}".format(
            self.mainApp.html()  # Serves the top level widgets.
        )

        self.write(htmlt.render(body=body))


class JSHandler(tornado.web.RequestHandler):
    """
    Serves app.js
    """

    def get(self):
        with open(f'{Path(__file__).parent.absolute()}/app.js') as f:
            self.write(f.read())


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    """
    Serves application widgets and handles communications during the
    life time of the application.
    """

    mainApp = None
    connection = None

    def open(self):
        """
        Opens the websocket connection. Accepts only one connection at this time.
        Further connection attempts will raise a RuntimeError. A new connection
        is accepted after this object's on_close() has been called.

        :return:
        """
        print(f'{self.__class__.__name__}.open()')
        if self.connection is None:
            WebSocketHandler.connection = self

            # Call the APPs handler for open websocket.
            self.mainApp.wsopen()
        else:
            print(f'Existing connection: {self.connection}')
            raise RuntimeError('WS is in use.')

    def on_message(self, message):
        """
        Handles messages received from the browser.
        So far, messages are passed directly to the application. They could
        potentially be intercepted here for "pluggable" processing of messages.

        :param message: A valid JSON string.
        :return: None
        """
        msg = json.loads(message)
        print(f'{self.__class__.__name__} GOT MSG: {msg}')
        self.mainApp.on_message(msg)

    def on_close(self):
        """
        Called when the connection has been closed (Probably by the client).
        Clears the class' connection attribute.

        :return: None
        """
        print(f'{self.__class__.__name__}.on_close()')
        WebSocketHandler.connection = None


class MainApp(VBox):

    wshandler = WebSocketHandler
    mainhandler = MainHandler
    jshandler = JSHandler

    def __init__(self):
        print(f'{self.__class__.__name__}.__init__()')
        super().__init__()
        print(f'{self.__class__.__name__}.identifier == {self.identifier}')

        self.wshandler.mainApp = self
        self.mainhandler.mainApp = self

        self.outbox = []

    def make_app(self):
        return tornado.web.Application([
            (r"/", self.mainhandler),
            (r"/websocket", self.wshandler),
            (r"/app.js", self.jshandler)
        ])

    def wsopen(self):
        """
        Called by self.wshandler.open(). Here we deliver all queued meesages
        in self.outbox. self.deliver will queue the messages if
        self.wshandler.connection is None.

        :return: None
        """
        print(f'{self.__class__.__name__}.wsopen()')
        for msg in self.outbox:
            self.deliver(msg)
        self.outbox = []

    def on_message(self, msg: Dict):
        """
        Called by the websocket handler's on_message.

        :param msg: The message from the client.
        :return: None
        """
        print(f'{self.__class__.__name__}.on_message():')
        print(msg)

        if msg['id'] == self.identifier:
            super().on_message(msg)
        else:
            self.descendent_index[msg['id']].on_message(msg)

    def deliver(self, msg: Dict):
        """
        Delivers a message to the browser. If self.wshandler.connection
        is None (websocket has not been opened), the messages are queued in
        self.outbox. All queued messages are delivered once the websocket opens
        (self.wsopen is called).

        :param msg: Message to be delivered.
        :return: None
        """
        print(f'{self.__class__.__name__}.deliver()')

        if self.wshandler.connection is None:
            # Save the messages. They will be delivered when we open
            # the connection.
            self.outbox.append(msg)
        else:
            self.wshandler.connection.write_message(json.dumps(msg))
