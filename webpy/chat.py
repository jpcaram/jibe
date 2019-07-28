import tornado.ioloop
import tornado.web
import tornado.websocket
from jinja2 import Template
from page import htmlt
from random import choice
import json
from typing import List, Dict


letter = 'abcdefghijklmnopqrstuvwxyz1234567890'


class Widget:

    # event_handlers = {}

    def __init__(self, connection=None):

        self.connection = connection

        self.identifier = ''.join(choice(letter)
                                  for _ in range(10))

        self.children = []

        self.event_handlers = {}

    def html(self):
        return ''

    def __str__(self):
        return self.html()

    def on_message(self, msg):
        """"""
        print(f'{self.__class__.__name__}.on_message()')
        print(f'   says: {msg}')

        if 'event' in msg and msg['event'] in self.event_handlers:
            self.event_handlers[msg['event']](msg)

    # def event_handler(method, event_name):
    #     .event_handlers[event_name] = method
    #     return method


class Button(Widget):

    label = "button"

    def __init__(self, connection=None):
        super().__init__(connection)

        self.event_handlers = {
            'click': self.on_click
        }

    def html(self):
        return Template("""
        <button id="{{identifier}}">{{label}}</button>
        <script>
        $("#{{identifier}}").click( function( event ) {
          console.log({id:"{{identifier}}", event: 'click'});
          message({id:"{{identifier}}", event: 'click'});
        });
        </script>
        """).render(
            identifier=self.identifier,
            label=self.label
        )

    # @Widget.event_handler("click")
    def on_click(self, msg):
        """"""
        print(f'{self.__class__.__name__}.on_click()')


class Input(Widget):

    def __init__(self, connection=None):
        super().__init__(connection)
        self._value = ""

        self.event_handlers = {
            "change": self.on_change
        }

    def html(self):
        return Template("""
        <input id="{{identifier}}" type="text">
        <script>
        // Event: "change" - Change in the value in the input box.
        // Occurs when hitting enter or focusing on something else (Chrome). 
        $("#{{identifier}}").change( function( event ) {
          console.log({id:"{{identifier}}", event: 'click', value: event.currentTarget.value});
          message({id:"{{identifier}}", event: 'click', value: event.currentTarget.value});
        });
        </script>
        """).render(
            identifier=self.identifier
        )

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self):
        pass

    def on_change(self, msg):
        """"""
        print(f'{self.__class__.__name__}.on_click()')


class MainHandler(tornado.web.RequestHandler):

    mainApp = None

    def get(self):

        body = "{}".format(self.mainApp.html())

        self.write(htmlt.render(body=body))


class WebSocketHandler(tornado.websocket.WebSocketHandler):

    mainApp = None

    # connections = set()
    connection = None

    def open(self):
        print(f'{self.__class__.__name__}.open()')
        # self.connections.add(self)
        if self.connection is None:
            WebSocketHandler.connection = self
            self.mainApp.wsopen()
        else:
            print(f'Existing connection: {self.connection}')
            raise RuntimeError('WS is in use.')

    def on_message(self, message):
        msg = json.loads(message)
        print(f'GOT MSG: {msg}')
        self.mainApp.on_message(msg)
        # [client.write_message(message) for client in self.connections]

    def on_close(self):
        print(f'{self.__class__.__name__}.on_close()')
        # self.connections.remove(self)
        WebSocketHandler.connection = None


class MainApp:

    wshandler = WebSocketHandler
    mainhandler = MainHandler

    def __init__(self):
        print(f'{self.__class__.__name__}.__init__()')
        self.wshandler.mainApp = self
        self.mainhandler.mainApp = self

        self.button = Button()
        self.inbox = Input()

        self.uielements: List[Widget] = [
            self.button,
            self.inbox
        ]

        self.uielements_by_id = MainApp.index_uielements(self.uielements)

    @staticmethod
    def index_uielements(elements=()):
        index = {}
        for elem in elements:
            index[elem.identifier] = elem
            index.update(MainApp.index_uielements(elem.children))
        return index

    def make_app(self):
        return tornado.web.Application([
            (r"/", self.mainhandler),
            (r"/websocket", self.wshandler)
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
        return Template("""
        {{inbox}}<BR>{{button}}
        """).render(inbox=self.inbox, button=self.button)

    def on_inbox_change(self):
        pass

    def on_button_click(self):
        self.inbox.value = "Hello!"


if __name__ == "__main__":
    app = MainApp().make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
