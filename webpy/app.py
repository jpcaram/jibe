import tornado.web
import tornado.websocket
import tornado.ioloop
import json
from .widget import Widget, VBox
from .page import htmlt
from typing import List, Dict, Optional, Awaitable
from pathlib import Path
from random import choice


letter = 'abcdefghijklmnopqrstuvwxyz1234567890'


class MainHandler(tornado.web.RequestHandler):
    """
    Serves the top level html and core elements (javascript) of
    the application.
    """

    def get(self):

        sessionid = self.get_cookie("sessionid")
        if not sessionid:
            sessionid = ''.join(choice(letter) for _ in range(10))
            self.set_cookie("sessionid", sessionid)

        self.write(htmlt.render(body='', appname=''))


class MainApp(VBox):

    def __init__(self, connection):
        """
        The MainApp class represents the top-level widget of a page.
        Extend this class to create a single-page web application.

        :param connection: Instance of
            WebSocketHandler(tornado.websocket.WebSocketHandler)
        """
        print(f'{self.__class__.__name__}.__init__()')

        super().__init__(identifier='topwidget')

        self.connection = connection

        print(f'{self.__class__.__name__}.identifier == {self.identifier}')

    def on_message(self, msg: Dict):
        """
        Called by the websocket handler's on_message. Overrides
        the parent widget's on_message. Delivers the message to
        the parent class (super) or to descendent (child).

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

        # Queued messages will re-attempt delivery so the
        # identifier will already be attached to the path.
        if len(msg['path']) == 0 or msg['path'][0] != self.identifier:
            msg['path'].insert(0, self.identifier)

        # if self.wshandler.connection is None:
        if not self.browser_side_ready:
            # Save the messages. They will be delivered when we open
            # the connection.
            self.outbox.append(msg)
            print(f'   Appended to outbox: {msg}')
        else:
            # self.wshandler.connection.write_message(json.dumps(msg))
            self.connection.write_message(json.dumps(msg))
            print(f'   Sent out: {msg}')

    @classmethod
    def make_tornado_app(cls):

        class WSH(WebSocketHandler):
            mainApp = cls

        return tornado.web.Application(
            [
                (r"/", MainHandler),
                (r"/websocket", WSH),
                (r"/(.*\.js)", tornado.web.StaticFileHandler, {"path": f"{Path(__file__).parent.absolute()}/"}),
                (r"/(.*\.css)", tornado.web.StaticFileHandler, {"path": f"{Path(__file__).parent.absolute()}/"})
            ]
        )

    @classmethod
    def run(cls, port=8881):
        """
        Single App quick starter.

        :param port: Port to listen at.
        :return: None
        """
        app = cls.make_tornado_app()
        app.listen(port)
        tornado.ioloop.IOLoop.current().start()


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    """
    Serves application widgets and handles communications during the
    life time of the application.

    The class is common to all connections. Each connection uses one instance.
    """

    mainApp = None
    # connection = None

    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        pass

    def __init__(self, *args, **kwargs):
        super(WebSocketHandler, self).__init__(*args, **kwargs)
        self.app = None

    def open(self):
        """
        Invoked when a new WebSocket is opened.

        An instance of self.mainApp is created and saved in self.app.

        :return:
        """
        print(f'################################# {self.__class__.__name__}.open()')
        # if self.connection is None:
        #     WebSocketHandler.connection = self
        #
        #     # Call the APPs handler for open websocket.
        #     self.mainApp.wsopen()
        # else:
        #     print(f'Existing connection: {self.connection}')
        #     raise RuntimeError('WS is in use.')
        self.app = self.mainApp(self)
        # self.app.wsopen()  # TODO: This is redundant. Whatever is in there can
        #                    #    be done in the constructor.

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
        # self.mainApp.on_message(msg)
        self.app.on_message(msg)

    def on_close(self):
        """
        Called when the connection has been closed (Probably by the client).
        Clears the class' connection attribute.

        :return: None
        """
        print(f'{self.__class__.__name__}.on_close()')
        WebSocketHandler.connection = None

