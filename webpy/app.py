import tornado.web
import tornado.websocket
import json
from jinja2 import Template
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

    # mainApp = None
    """Instance of the mainApp."""

    def get(self):

        # body = "{}".format(
        #     self.mainApp.html()  # Serves the top level widgets.
        # )

        sessionid = self.get_cookie("sessionid")
        if not sessionid:
            sessionid = ''.join(choice(letter) for _ in range(10))
            self.set_cookie("sessionid", sessionid)

        self.write(htmlt.render(body=''))


class JSHandler(tornado.web.RequestHandler):
    """
    Serves app.js
    """

    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        pass

    def get(self):
        with open(f'{Path(__file__).parent.absolute()}/app.js') as f:
            self.write(f.read())


class CSSHandler(tornado.web.RequestHandler):
    """
    Serves app.js
    """

    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        pass

    def get(self):
        with open(f'{Path(__file__).parent.absolute()}/app.css') as f:
            self.write(f.read())


class MainApp(VBox):

    # wshandler = WebSocketHandler
    # mainhandler = MainHandler
    # jshandler = JSHandler
    # csshandler = CSSHandler

    def __init__(self, connection):
        print(f'{self.__class__.__name__}.__init__()')

        super().__init__(identifier='topwidget')

        self.connection = connection

        print(f'{self.__class__.__name__}.identifier == {self.identifier}')

        # self.wshandler.mainApp = self
        # self.mainhandler.mainApp = self

    # def make_app(self):
    #     return tornado.web.Application([
    #         (r"/", self.mainhandler),
    #         (r"/websocket", self.wshandler),
    #         (r"/(.*\.js)", tornado.web.StaticFileHandler, {"path": f"{Path(__file__).parent.absolute()}/"}),
    #         (r"/(.*\.css)", tornado.web.StaticFileHandler, {"path": f"{Path(__file__).parent.absolute()}/"})
    #     ])

    def wsopen(self):
        """
        Called by self.wshandler.open(). Here we deliver all queued meesages
        in self.outbox. self.deliver will queue the messages if
        self.wshandler.connection is None.

        :return: None
        """
        print(f'{self.__class__.__name__}.wsopen() -- Nothing to do here.')
        # for msg in self.outbox:
        #     self.deliver(msg)
        # self.outbox = []

    def on_message(self, msg: Dict):
        """
        Called by the websocket handler's on_message. Overrides
        the parent widget's on_message. Delivers the message to
        the parent (super) or to descendents.

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
        Opens the websocket connection. Accepts only one connection at this time.
        Further connection attempts will raise a RuntimeError. A new connection
        is accepted after this object's on_close() has been called.

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

    # def instapp(self):
    #     return 0

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


# class WebPyApplication(tornado.web.Application):
#
#     def __init__(self, wshandler):
#         handlers = [
#             # (r"/", self.mainhandler),
#             (r"/", MainHandler),
#             # (r"/websocket", self.wshandler),
#             (r"/websocket", wshandler),
#             (r"/(.*\.js)", tornado.web.StaticFileHandler, {"path": f"{Path(__file__).parent.absolute()}/"}),
#             (r"/(.*\.css)", tornado.web.StaticFileHandler, {"path": f"{Path(__file__).parent.absolute()}/"})
#         ]
#
#         super(WebPyApplication, self).__init__(handlers)
