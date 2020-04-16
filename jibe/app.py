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

    main_handler_class: tornado.web.RequestHandler = MainHandler
    """
    This is the server's handler for http requests made on this app.
    Used in MainApp.make_tornado_app(). Override and replace to change
    to change the default behavior.
    """

    assets_path = None
    """
    Set to serve the files in a folder in the file system
    on a specific URL path. For example:
        
        {'from': 'path/to/files', 'to': 'path/on/url'}
        
    This will make files available in the folder 'path/to/files'
    on the URL 'path/on/url'.
    
    You can specify multiple pairs in a list:
        
        [
            {'to': '...', 'from': '...'}, 
            {'to': '...', 'from': '...'},
            etc
        ]
        
    Note: At this time, the 'from' path is relative to the
    path where the app was started unless it is made absolute
    by prepending a '/'. The 'to' path is always absolute,
    i.e. a '/' is prepended. This behavior may change in
    the future.
    """

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
            print(f'   Appended to outbox: {message["event"]}')
        else:
            # self.wshandler.connection.write_message(json.dumps(msg))
            self.connection.write_message(json.dumps(message))
            print(f'   Sent out: {"message"}')

    @classmethod
    def make_tornado_app(cls) -> tornado.web.Application:
        """
        Puts together the websocket handler and http handlers for this app
        into a tornado.web.Application.

        :return: A Tornado application that ew can then serve
            at a specific port.
        """

        class WSH(WebSocketHandler):
            mainApp = cls

        jibe_assets_path = Path(__file__).parent.absolute()
        handlers = [
            (r"/", cls.main_handler_class),
            (r"/websocket", WSH),
            (r"/(.*\.js)", tornado.web.StaticFileHandler, {"path": f"{jibe_assets_path}/"}),
            (r"/(.*\.css)", tornado.web.StaticFileHandler, {"path": f"{jibe_assets_path}/"})
        ]

        # Additional handlers for user-defined assets.
        ap = cls.assets_path
        if isinstance(ap, dict):
            ap = [ap]
        elif isinstance(ap, (list, tuple)):
            pass
        elif ap is None:
            ap = []
        else:
            raise TypeError(f'{cls.__name__}.assets_path must be a'
                            'dictionary, list, tuple or None')

        for path in ap:
            if path['from'][0] != '/':
                raise ValueError(f'Assets path must be absolute: {path["from"]}')

            print(f'ASSETS SOURCE: {path["from"]}')
            handlers.append(
                (rf"/{path['to']}/(.*)", tornado.web.StaticFileHandler,
                 {"path": f'{path["from"]}'})
            )

        return tornado.web.Application(handlers)

    @classmethod
    def run(cls, port=8881):
        """
        Single App quick starter.

        :param port: Port to listen at.
        :return: None
        """
        app = cls.make_tornado_app()
        app.listen(port)
        print(f'Listening on port {port}.')
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

        :return: None
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
    Then initializes itself (a tornado.web.Application) with a list of
    Tornado Handlers.
    """

    def __init__(self, **kwargs):
        """
        Creates a Jibe MultiApp.

        :param kwargs: Jibe MainApps by name. The names are used as part of
            the URL to reach each App. Additionally, 'assets_path' can be
            used to specify user-defined folders to make available in the
            form [{'to':..., 'from':...}, ...].
        """

        # TODO: Support specifying alternative files.
        jibe_assets_path = Path(__file__).parent.absolute()
        print(f'Assets path: {jibe_assets_path}')

        handlers = [
            (r"/(.*\.js)", tornado.web.StaticFileHandler, {"path": jibe_assets_path}),
            (r"/(.*\.css)", tornado.web.StaticFileHandler, {"path": jibe_assets_path})
        ]

        for name, cls in kwargs.items():

            if type(cls) is not type or not issubclass(cls, MainApp):
                continue

            # Create a new class inheriting from WebSocketHandler,
            # and setting their mainApp to each cls.
            wsh = type(
                'WSH' + name,
                (WebSocketHandler, ),
                {'mainApp': cls}
            )
            handlers.append((fr'/({name})', MultiAppHandler))
            handlers.append((fr'/{name}/websocket', wsh))

            # User-defined asses in app.
            ap = cls.assets_path
            if isinstance(ap, dict):
                ap = [ap]
            elif isinstance(ap, (list, tuple)):
                pass
            elif ap is None:
                ap = []
            else:
                raise TypeError(f'{cls.__name__}.assets_path must be a'
                                'dictionary, list, tuple or None')

            for path in ap:
                if path['from'][0] != '/':
                    raise ValueError(f'Assets path must be absolute: {path["from"]}')

                print(f'ASSETS SOURCE: {path["from"]}')
                handlers.append(
                    (rf"/{name}/{path['to']}/(.*)", tornado.web.StaticFileHandler,
                     {"path": path["from"]})
                )

        # User defined assets.
        if 'assets_path' in kwargs:
            ap = kwargs['assets_path']
            if not isinstance(ap, (dict, list, tuple)):
                raise TypeError(f'assets_path must be a '
                                'dictionary, list or tuple')
            if isinstance(ap, dict):
                ap = [ap]

            for path in ap:
                if path['from'][0] != '/':
                    raise ValueError(f'Assets path must be absolute: {path["from"]}')
                print(f'ASSETS SOURCE: {path["from"]}')
                handlers.append(
                    (str(Path(path['to'] + "/")) + r"(.*)",
                     tornado.web.StaticFileHandler,
                     {"path": path['from']})
                )

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


class InJupyterMultiApp(MultiApp):
    _io_loops = []
    server = None
    port = 8881
    loop = None

    # TODO: Identical to InJupyterApp.get_ioloop.
    @classmethod
    def get_ioloop(cls):
        from tornado.ioloop import IOLoop
        import threading
        if not cls._io_loops:
            print('No loop. Creating one.')
            loop = IOLoop()
            thread = threading.Thread(target=loop.start)
            thread.daemon = True
            thread.start()
            cls._io_loops.append(loop)
        return cls._io_loops[0]

    def _start_server(self):
        from tornado.httpserver import HTTPServer

        self.server = HTTPServer(self)
        self.server.listen(self.port)

    def juprun(self, port=8881):
        self.port = port
        self.loop = self.get_ioloop()
        self.loop.add_callback(self._start_server)


class InJupyterApp(MainApp):
    _io_loops = []
    server = None
    port = 8881
    loop = None

    @classmethod
    def get_ioloop(cls):
        from tornado.ioloop import IOLoop
        import threading
        if not cls._io_loops:
            print('No loop. Creating one.')
            loop = IOLoop()
            thread = threading.Thread(target=loop.start)
            thread.daemon = True
            thread.start()
            cls._io_loops.append(loop)
        return cls._io_loops[0]

    @classmethod
    def _start_server(cls):
        from tornado.httpserver import HTTPServer

        application = cls.make_tornado_app()
        cls.server = HTTPServer(application)
        cls.server.listen(cls.port)

    @classmethod
    def juprun(cls, port=8881):
        cls.port = port
        cls.loop = cls.get_ioloop()
        cls.loop.add_callback(cls._start_server)