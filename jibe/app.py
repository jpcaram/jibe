# Jibe
# A Full-Stack Pure-Python Web Framework.
# Copyright (c) 2020 Juan Pablo Caram
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

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


# noinspection PyAbstractClass
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

        self.write(htmlt.render(
            body=self.body(),
            appname=self.appname(),
            scripts=self.scripts(),
            cssfiles=self.cssfiles(),
            presetup=self.presetup(),
            css=self.css()
        ))

    def body(self):
        return ''

    def appname(self):
        return ''

    def scripts(self):
        return []

    def cssfiles(self):
        return []

    def presetup(self):
        return ''

    def css(self):
        return ''


# noinspection PyAbstractClass
class MultiAppHandler(MainHandler):
    """
    Serves the top level html and core elements (javascript) of
    a Jibe MultiApp.
    """

    def get(self, appname):
        print(f'{__class__.__name__}.get("{appname}")')

        sessionid = self.get_cookie("sessionid")
        if not sessionid:
            sessionid = ''.join(choice(letter) for _ in range(10))
            self.set_cookie("sessionid", sessionid)

        self.write(htmlt.render(
            body=self.body(),
            appname=appname,
            scripts=self.scripts(),
            cssfiles=self.cssfiles(),
            presetup=self.presetup(),
            css=self.css()
        ))


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

    def on_message(self, message: Dict):
        """
        Called by the websocket handler's on_message. Overrides
        the parent widget's on_message. Delivers the message to
        the parent class (super) or to descendent (child).

        :param message: The message from the client.
        :return: None
        """
        print(f'{self.__class__.__name__}.on_message():')
        print(message)

        if message['id'] == self.identifier:
            super().on_message(message)
        else:
            self.descendent_index[message['id']].on_message(message)

    def deliver(self, message: Dict):
        """
        Delivers a message to the browser. If self.wshandler.connection
        is None (websocket has not been opened), the messages are queued in
        self.outbox. All queued messages are delivered once the websocket opens
        (self.wsopen is called).

        :param message: Message to be delivered.
        :return: None
        """
        print(f'{self.__class__.__name__}.deliver()')

        # Queued messages will re-attempt delivery so the
        # identifier will already be attached to the path.
        if len(message['path']) == 0 or message['path'][0] != self.identifier:
            message['path'].insert(0, self.identifier)

        # if self.wshandler.connection is None:
        if not self.browser_side_ready:
            # Save the messages. They will be delivered when we open
            # the connection.
            self.outbox.append(message)
            print(f'   Appended to outbox: {message}')
        else:
            # self.wshandler.connection.write_message(json.dumps(msg))
            self.connection.write_message(json.dumps(message))
            print(f'   Sent out: {message}')

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
        self.app = self.mainApp(self)

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
        self.app.on_message(msg)

    def on_close(self):
        """
        Called when the connection has been closed (Probably by the client).
        Clears the class' connection attribute.

        :return: None
        """
        print(f'{self.__class__.__name__}.on_close()')
        WebSocketHandler.connection = None


class MultiApp(tornado.web.Application):
    """
    Creates a WebSocketHandler-derived class for each Jibe App.
    The initializes itself (a tornado.web.Application) with with a list of
    Tornado Handlers.
    """

    def __init__(self, **kwargs):
        """
        Creates a Jibe MultiApp.

        :param kwargs: Jibe MainApps by name. The names are used as part of
            the URL to reach each App.
        """

        # TODO: Support specifying alternative files.
        assets_path = Path(__file__).parent.absolute()
        print(f'Assets path: {assets_path}')

        handlers = [
            (r"/(.*\.js)", tornado.web.StaticFileHandler, {"path": assets_path}),
            (r"/(.*\.css)", tornado.web.StaticFileHandler, {"path": assets_path})
        ]

        for name, cls in kwargs.items():
            wsh = type(
                'WSH' + name,
                (WebSocketHandler, ),
                {'mainApp': cls}
            )
            handlers.append((fr'/({name})', MultiAppHandler))
            handlers.append((fr'/{name}/websocket', wsh))

        from pprint import pprint
        pprint(handlers)
        super().__init__(handlers, debug=True)

    def run(self, port=8881):
        """
        Start the Jibe MultiApp listening on the given port.

        :param port: Port to listen at. Default is 8881.
        :return: None
        """
        self.listen(port)
        tornado.ioloop.IOLoop.current().start()