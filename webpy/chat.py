import tornado.ioloop
import tornado.web
import tornado.websocket
from jinja2 import Template
from page import htmlt
from random import choice
import json
from typing import List, Dict


letter = 'abcdefghijklmnopqrstuvwxyz1234567890'


class OrfanWidgetError(Exception):
    pass


class NoSuchEvent(Exception):
    pass


class Widget:

    # event_handlers = {}

    def __init__(self, connection=None):

        self.parent = None

        self.connection = connection

        self.identifier = ''.join(choice(letter)
                                  for _ in range(10))

        self.children = []

        self.local_event_handlers = {}

        self.subscribers = {}

    def html(self):
        return '<widget id="_{{identifier}}"></widget>'.format(
            identifier=self.identifier
        )

    def __str__(self):
        return self.html()

    def on_message(self, msg):
        """
        Invoked when a message for this Widget is received from the browser.

        :param msg:
        :return:
        """
        print(f'{self.__class__.__name__}.on_message()')
        print(f'   says: {msg}')

        if 'event' in msg and msg['event'] in self.local_event_handlers:
            self.local_event_handlers[msg['event']](msg)

    def message(self, msg):
        """
        Send a message to this widget's browser side.

        :param msg:
        :return:
        """

        msg['id'] = self.identifier

        self.deliver(msg)

    def deliver(self, msg):
        """

        :param msg:
        :return:
        """

        try:
            self.parent.deliver(msg)
        except AttributeError:
            raise OrfanWidgetError("This widget is not attached to an app.")

    # def event_handler(method, event_name):
    #     .event_handlers[event_name] = method
    #     return method

    def register(self, event, handler):

        try:
            if handler not in self.subscribers[event]:
                self.subscribers[event].append(handler)
        except KeyError:
            raise NoSuchEvent(event)


class Button(Widget):

    label = "button"

    def __init__(self, connection=None):
        super().__init__(connection)

        self.local_event_handlers = {
            'click': self.on_click
        }

        self.subscribers['click'] = []

    def html(self):
        return Template("""
        <widget id="_{{identifier}}">
        <button id="{{identifier}}">{{label}}</button>
        <script>
        $("#{{identifier}}").click( function( event ) {
          console.log({id:"{{identifier}}", event: 'click'});
          message({id:"{{identifier}}", event: 'click'});
        });
        $("#{{identifier}}").on("message", function( evt, data ) {
          console.log("message event for #{{identifier}}");
          console.log(evt);
          console.log(data);
        });
        </script>
        </widget>
        """).render(
            identifier=self.identifier,
            label=self.label
        )

    # @Widget.event_handler("click")
    def on_click(self, msg):
        """"""
        print(f'{self.__class__.__name__}.on_click()')

        for subscriber in self.subscribers['click']:
            subscriber(self)


class Input(Widget):

    def __init__(self, connection=None):
        super().__init__(connection)
        self._value = ""

        self.event_handlers = {
            "change": self.on_change
        }

    def html(self):
        return Template("""
        <widget id="_{{identifier}}">
        <input id="{{identifier}}" type="text">
        <script>
        // Event: "change" - Change in the value in the input box.
        // Occurs when hitting enter or focusing on something else (Chrome). 
        $("#{{identifier}}").change( function( event ) {
          console.log({id:"{{identifier}}", event: 'click', value: event.currentTarget.value});
          message({id:"{{identifier}}", event: 'click', value: event.currentTarget.value});
        });
        $("#{{identifier}}").on("message", function( evt, data ) {
          console.log("message event for #{{identifier}}");
          console.log(evt);
          console.log(data);
        });
        </script>
        </widget>
        """).render(
            identifier=self.identifier
        )

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        print(f'{self.__class__.__name__}.value()')
        self.message({'event': 'value'})

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

        # Adopt widgets.
        for w in self.uielements:
            w.parent = self

        self.button.register('click', self.on_button_click)

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

    def deliver(self, msg):
        print(f'{self.__class__.__name__}.deliver()')
        self.wshandler.connection.write_message(json.dumps(msg))

    def on_inbox_change(self):
        pass

    def on_button_click(self, source):
        print(f'{self.__class__.__name__}.on_button_click()')
        self.inbox.value = "Hello!"


if __name__ == "__main__":
    app = MainApp().make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
