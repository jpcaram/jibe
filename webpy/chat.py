import tornado.ioloop
import tornado.web
import tornado.websocket
from jinja2 import Template
from page import htmlt
from random import choice
import json
from typing import List, Dict


letter = 'abcdefghijklmnopqrstuvwxyz1234567890'


def callback_method(func):
    """
    Used to wrap methods such that _callbacks in the class
    are called immediately before the method.

    :param func: Method to be wrapped.
    :return: Wrapped method.
    """
    def notify(self, *args, **kwargs):
        for callback in self._callbacks:
            callback(self, *args, **kwargs)
        return func(self, *args, **kwargs)
    return notify


class NotifyList(list):
    """
    Extends list to support a callback on change.
    """
    extend = callback_method(list.extend)
    append = callback_method(list.append)
    remove = callback_method(list.remove)
    pop = callback_method(list.pop)
    __delitem__ = callback_method(list.__delitem__)
    __setitem__ = callback_method(list.__setitem__)
    __iadd__ = callback_method(list.__iadd__)
    __imul__ = callback_method(list.__imul__)

    def __init__(self, *args):
        list.__init__(self, *args)
        self._callbacks = []


def event_handler(*args):
    """
    A decorator for methods.

    Mark the method as an event handler. Simply sets the attribute
    event_register to the given arguments tuple. This attribute is then
    checked by the constructor of the class.

    :param args:
    :return:
    """
    print(f'event_handler({args})')

    def decorator(f):
        print(f'decorator({f})')
        f.event_register = tuple(args)
        return f
    return decorator


class OrfanWidgetError(Exception):
    pass


class NoSuchEvent(Exception):
    pass


class Widget:

    def __init__(self):

        self.parent = None
        """Widgets pass messages up to their parent to reach the main App,
        which sends the message to the browser.
        """

        self.identifier = ''.join(choice(letter) for _ in range(10))
        """Unique identifier to find the browser counterpart."""

        self._children = []
        """For composite widgets."""

        self.local_event_handlers = {}
        """To define event handlers within the object."""

        self.subscribers = {}
        """For others to benotified of events."""

        # Process methods marked as event handlers
        # (Decorated with @event_handler('event_name)).
        for method_name in dir(self):

            # Skip properties
            if isinstance(getattr(self.__class__, method_name, None), property):
                continue

            method = getattr(self, method_name)

            # Methods only.
            if callable(method) and not method_name.startswith('__'):  # It's a method.
                try:
                    # This will raise AttributeError if not a callback.
                    # (Event handlers have attribute event_register which is a tuple).
                    event_name = method.event_register[0]

                    self.local_event_handlers[event_name] = method
                    self.subscribers[event_name] = []
                    print(f'{self.__class__.__name__}: Registered event "{event_name}"')
                except AttributeError:  # Does not have 'register'
                    pass

    @property
    def children(self):
        return self._children

    @children.setter
    def children(self, value):
        """
        Sets the children list. If value is of type list, it gets
        converted into a NotifyList and the on_children_change method
        is set as a callback for changes. This same method is called
        after the list is set.

        :param value: List of children.
        :return: None
        """
        print(f'{self.__class__.__name__}.children({value})')

        self._children = NotifyList(value)
        self._children._callbacks.append(self.on_children_change)
        self.on_children_change()

    def on_children_change(self):
        """
        Called after the children attribute changes, this is when it gets assigned
        or when the elements in that list change (append, remove, etc).

        :return: None
        """
        print(f'{self.__class__.__name__}.on_children_change()')

        # Adopt children
        print(f'{repr(self)} adopting children:')
        for child in self.children:
            print(f'   {repr(child)} adopted.')
            child.parent = self

    def html(self):
        """
        Generates the HTML for this widget in the browser.

        :return: HTML text.
        """
        return Template('<widget id="_{{identifier}}"></widget>').render(
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
            raise OrfanWidgetError(
                f'This widget is not attached to an app: {repr(self)}'
            )

    def register(self, event, handler):
        """
        Register the event handler for the specified event.

        :param event: Name of the event
        :param handler: Callable.
        :return: None
        """

        try:
            if handler not in self.subscribers[event]:
                self.subscribers[event].append(handler)
        except KeyError:
            raise NoSuchEvent(event)


class HBox(Widget):

    def html(self):
        content = "\n".join(child.html() for child in self.children)

        return Template("""
        <widget id="_{{identifier}}">
        <div style="display: flex; flex-direction: row;">
        {{content}}
        </div>
        </widget>
        """).render(
            identifier=self.identifier,
            content=content
        )


class HBox2(Widget):

    def html(self):

        return Template("""
        <widget id="_{{identifier}}">
        <div id="{{identifier}}" style="display: flex; flex-direction: row;">
        
        </div>
        <script>
        $(document).ready( function() {
            $( document ).on("wsconnected", function() {
                console.log("HBox2 {{identifier}} instantiated.");
                message( {'id': '{{identifier}}', 'event': 'children'} );
            });
        });
        $("#{{identifier}}").on("message", function(evt, data) {
            console.log("message event for #{{identifier}}");
            console.log(evt);
            console.log(data);
            if (data.event == "children") {
                console.log('data.event == "children"');
                data.children.forEach(function(child) {
                    contents =  $(evt.currentTarget).html();
                    $(evt.currentTarget).html(contents + child);
                });
            }
        });
        </script>
        </widget>
        """).render(
            identifier=self.identifier
        )

    @event_handler("children")
    def on_children(self, msg):
        """
        Javascript counterpart request for children. Widgets that have children
        will request for their children once they are instantiated in the browser.

        :param msg: Message from the browser
        :return:
        """
        self.message({'event': 'children', 'children': [
            child.html() for child in self.children
        ]})


class VBox(Widget):

    def html(self):
        content = "\n".join(child.html() for child in self.children)

        return Template("""
        <widget id="_{{identifier}}">
        <div style="display: flex; flex-direction: column;">
        {{content}}
        </div>
        </widget>
        """).render(
            identifier=self.identifier,
            content=content
        )


class Button(Widget):

    label = "button"

    def __init__(self):
        super().__init__()

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

    @event_handler("click")
    def on_click(self, msg):
        """
        Main event handler for the "click" event.

        :param msg:
        :return:
        """
        print(f'{self.__class__.__name__}.on_click()')
        print(f'{len(self.subscribers)} subscribers.')
        for subscriber in self.subscribers['click']:
            subscriber(self)


class Input(Widget):

    def __init__(self):
        super().__init__()
        self._value = ""

    def html(self):
        return Template("""
        <widget id="_{{identifier}}">
        <input id="{{identifier}}" type="text">
        <script>
        // Event: "change" - Change in the value in the input box.
        // Occurs when hitting enter or focusing on something else (Chrome). 
        $("#{{identifier}}").change( function( event ) {
            console.log({id:"{{identifier}}", event: 'change', value: event.currentTarget.value});
            message({id:"{{identifier}}", event: 'change', value: event.currentTarget.value});
        });
        $("#{{identifier}}").on("message", function( evt, data ) {
              console.log("message event for #{{identifier}}");
              console.log(evt);
              console.log(data);
              if (data.event == "value") {
                    console.log('data.event == "value"');
                    evt.currentTarget.value = data.value;
              }
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
        print(f'{self.__class__.__name__}.value({val})')
        self.message({'event': 'value', 'value': val})
        self._value = val

    @event_handler("change")
    def on_change(self, msg):
        """
        Event handler for the "change" event.

        :param msg:
        :return:
        """
        print(f'{self.__class__.__name__}.on_change({msg})')


class MainHandler(tornado.web.RequestHandler):
    """
    Serves the top level html and core elements (javascript) of the application.
    """

    mainApp = None

    def get(self):

        body = "{}".format(self.mainApp.html())

        self.write(htmlt.render(body=body))


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
        print(f'GOT MSG: {msg}')
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

    def __init__(self):
        print(f'{self.__class__.__name__}.__init__()')
        self.wshandler.mainApp = self
        self.mainhandler.mainApp = self

        # self.button = Button()
        # self.inbox = Input()
        #
        # self.box1 = HBox2()
        # self.box1.children = [
        #     self.button,
        #     self.inbox
        # ]
        #
        # # self.box1 = HBox()
        # # self.box1.children = [
        # #     self.button,
        # #     self.inbox
        # # ]

        # self.uielements: List[Widget] = [
        #     self.box1
        # ]
        #
        # self.uielements_by_id = MainApp.index_uielements(self.uielements)
        #
        # # Adopt widgets.
        # print(f'{repr(self)} adopting children:')
        # for w in self.uielements:
        #     print(f'   {repr(w)} adopted.')
        #     w.parent = self
        #
        # self.button.register('click', self.on_button_click)

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
        content = "\n".join(child.html() for child in self.uielements)

        return Template("""
        {{content}}
        """).render(content=content)

    def deliver(self, msg):
        print(f'{self.__class__.__name__}.deliver()')
        self.wshandler.connection.write_message(json.dumps(msg))

    # def on_inbox_change(self):
    #     pass
    #
    # def on_button_click(self, source):
    #     print(f'{self.__class__.__name__}.on_button_click()')
    #     self.inbox.value = "Hello!"


class ExampleApp(MainApp):

    def __init__(self):
        super().__init__()

        self.button = Button()
        self.inbox = Input()

        self.box1 = HBox2()
        self.box1.children = [
            self.button,
            self.inbox
        ]

        self.uielements: List[Widget] = [
            self.box1
        ]

        self.uielements_by_id = MainApp.index_uielements(self.uielements)

        # Adopt widgets.
        print(f'{repr(self)} adopting children:')
        for w in self.uielements:
            print(f'   {repr(w)} adopted.')
            w.parent = self

        self.button.register('click', self.on_button_click)

    def on_inbox_change(self):
        pass

    def on_button_click(self, source):
        print(f'{self.__class__.__name__}.on_button_click()')
        self.inbox.value = "Hello!"


if __name__ == "__main__":
    # app = MainApp().make_app()
    app = ExampleApp().make_app()
    app.listen(8881)
    tornado.ioloop.IOLoop.current().start()
