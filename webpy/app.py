import tornado.web
import tornado.websocket
import json
from jinja2 import Template
from .widget import Widget
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


class MainApp:

    wshandler = WebSocketHandler
    mainhandler = MainHandler
    jshandler = JSHandler

    def __init__(self):
        print(f'{self.__class__.__name__}.__init__()')
        self.wshandler.mainApp = self
        self.mainhandler.mainApp = self

        self.uielements_by_id = {}
        self.uielements: List[Widget] = [

        ]

    @staticmethod
    def index_uielements(elements=()):
        """
        Recursively visits children and collects their
        identifiers.

        :param elements:
        :return:
        """
        index = {}
        for elem in elements:
            index[elem.identifier] = elem
            index.update(MainApp.index_uielements(elem.children))
        return index

    def announce_children(self, *args):

        for child in args:
            self.uielements_by_id[child.identifier] = child

    def make_app(self):
        return tornado.web.Application([
            (r"/", self.mainhandler),
            (r"/websocket", self.wshandler),
            (r"/app.js", self.jshandler)
        ])

    def wsopen(self):
        """"""

    def on_message(self, msg: Dict):
        """
        Called by the websocket handler's on_message.

        :param msg: The message from the client.
        :return: None
        """
        print(f'{self.__class__.__name__}.on_message():')
        print(msg)
        print(repr(self.uielements_by_id[msg["id"]]))
        self.uielements_by_id[msg["id"]].on_message(msg)

    def html(self):
        """
        Called by the main handler to render the body of
        the page on to the client.

        :return:
        """
        content = "\n".join(child.html() for child in self.uielements)

        return Template("""
        {{content}}
        """).render(content=content)

    def deliver(self, msg: Dict):
        """
        Delivers a message to the browser.

        :param msg: Message to be delivered.
        :return: None
        """
        print(f'{self.__class__.__name__}.deliver()')
        self.wshandler.connection.write_message(json.dumps(msg))

    def update_descendents(self, *args):
        print(f"{self.__class__.__name__}.update_descendents()")
        for branch in args:
            if isinstance(branch, Widget):
                self.uielements_by_id[branch.identifier] = branch
            elif isinstance(branch, dict):
                self.uielements_by_id.update(branch)
            elif isinstance(branch, list):
                for w in branch:
                    self.uielements_by_id[w.identitier] = w
            else:
                raise TypeError("Cannot update descendent from type {}".format(type(branch)))

        for ident, w in self.uielements_by_id.items():
            print(f'   {ident}: {w.__class__.__name__}')