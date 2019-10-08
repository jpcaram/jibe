from random import choice
from jinja2 import Template
from typing import Callable, List


letter = 'abcdefghijklmnopqrstuvwxyz1234567890'


def callback_method(func):
    """
    Used to wrap methods such that _callbacks in the class
    are called immediately after the method.

    :param func: Method to be wrapped.
    :return: Wrapped method.
    """

    def notify(self, *args, **kwargs):
        retval = func(self, *args, **kwargs)
        for callback in self._callbacks:
            callback(self, *args, **kwargs)
        return retval

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


def callback_method_x(method: Callable, cbname: str) -> Callable:
    """
    Used to attach callbacks to different methods that modify
    the list, in NotifyList2.

    :param method:
    :param cbname: Name of the method to be called as callback.
    :return: Wrapped method.
    """

    def notify(self: List, *args, **kwargs):
        """

        :param self: The object on which method is being called.
        :param args: Varies. For append, args[0] is the item being added.
        :param kwargs:
        :return:
        """
        retval = method(self, *args, **kwargs)
        for callback in getattr(self, cbname):
            callback(*args, **kwargs)
        return retval

    return notify


class NotifyList2(list):

    def __init__(self, *args):
        list.__init__(self, *args)
        self._on_extend_callbacks = []
        self._on_append_callbacks = []
        self._on_remove_callbacks = []
        self._on_pop_callbacks = []
        self._on_delitem_callbacks = []
        self._on_setitem_callbacks = []
        self._on_iadd_callbacks = []
        self._on_imul_callbacks = []

    extend = callback_method_x(list.extend, "_on_extend_callbacks")
    append = callback_method_x(list.append, "_on_append_callbacks")
    remove = callback_method_x(list.remove, "_on_remove_callbacks")
    pop = callback_method_x(list.pop, "_on_pop_callbacks")
    __delitem__ = callback_method_x(list.__delitem__, "_on_delitem_callbacks")
    __setitem__ = callback_method_x(list.__setitem__, "_on_setitem_callbacks")
    __iadd__ = callback_method_x(list.__iadd__, "_on_iadd_callbacks")
    __imul__ = callback_method_x(list.__imul__, "_on_imul_callbacks")


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

    def __init__(self, style=None):

        self.identifier = ''.join(choice(letter) for _ in range(10))
        """Unique identifier to find the browser counterpart."""

        self._parent = None
        """Widgets pass messages up to their parent to reach the main App,
        which sends the message to the browser.
        """

        self.descendent_index = {}

        self._children = NotifyList2([])
        """For composite widgets."""

        self._children._on_append_callbacks.append(self.on_children_append)
        self._children._on_remove_callbacks.append(self.on_children_remove)

        self.local_event_handlers = {}
        """To define event handlers within the object."""

        self.subscribers = {}
        """For others to benotified of events."""

        self.style = {} if style is None else style
        """Style attribute"""

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

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, p):
        """
        Sets the parent attribute and updates the parent with
        all known descendents.

        :param p: Parent widget.
        :return: None
        """
        print(f'{self.__class__.__name__}.parent set.')
        self._parent = p
        self.parent.update_descendents(self, self.descendent_index)

    def update_descendents(self, *args):
        """
        Called by children when adopted to notify about all
        known descendents. In turn, forwards this information
        to this widgent's parent and should bubble up to the main app.

        :param args: Widget, Dictionary of widgets by identifier or List of Widgets.
        :return: None
        """
        print(f'{self.__class__.__name__}.update_descendents()')

        for branch in args:
            if isinstance(branch, Widget):
                self.descendent_index[branch.identifier] = branch
            elif isinstance(branch, dict):
                self.descendent_index.update(branch)
            elif isinstance(branch, list):
                for w in branch:
                    self.descendent_index[w.identitier] = w
            else:
                raise TypeError("Cannot update descendent from type {}".format(type(branch)))

        try:
            self.parent.update_descendents(self.descendent_index)
        except AttributeError:
            print("This widget does not have a parent to notify about descendents.")

    def on_children_change(self):
        """
        Called when the children attribute is assigned. All the children
        are sent to the browser.

        :return: None
        """
        print(f'{self.__class__.__name__}.on_children_change()')

        # Adopt children
        print(f'{repr(self)} adopting children:')
        for child in self.children:
            print(f'   {repr(child)} adopted.')
            child.parent = self

        # TODO: Temporary experiment
        try:
            self.message({'event': 'children', 'children': [
                child.html() for child in self.children
            ]})
        except OrfanWidgetError:
            print("Temporarily allowing OrfanWidgetError!")

    def on_children_append(self, *args, **kwargs):
        """
        Called when this.children.append() is called. Sends the
        appended child to the browser.

        :param args:
        :param kwargs:
        :return:
        """
        print(f'{self.__class__.__name__}.on_children_append()')

        # Adopt the child
        child = args[0]
        print(f'{repr(self)} adopting child: {repr(child)}')
        child.parent = self

        # TODO: Temporary experiment
        try:
            self.message({'event': 'append', 'child': child.html()})
        except OrfanWidgetError:
            print("Temporarily allowing OrfanWidgetError!")

    def on_children_remove(self, *args, **kwargs):
        """
        Called when this.children.remove() is called. Notifies the
        browser of the removal.

        :param args:
        :param kwargs:
        :return:
        """

        print(f'{self.__class__.__name__}.on_children_remove()')
        child = args[0]
        try:
            self.message({'event': 'remove', 'childid': child.identifier})
        except OrfanWidgetError:
            print("Temporarily allowing OrfanWidgetError!")

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
        Passes a message to the parent to be delivered to the Browser.

        :param msg:
        :return:
        """

        try:
            self.parent.deliver(msg)
        except AttributeError:
            raise OrfanWidgetError(
                f'This widget is not attached to an app: {repr(self)}'
            )

    def register(self, event: str, handler: Callable):
        """
        Register the event handler for the specified event.
        The handler receives a single parameter, the widget
        generating the event.

        :param event: Name of the event
        :param handler: Callable.
        :return: None
        """

        try:
            if handler not in self.subscribers[event]:
                self.subscribers[event].append(handler)
        except KeyError:
            raise NoSuchEvent(event)

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

    def style_string(self):
        return " ".join([f"{key}: {value};" for key, value in self.style.items()])

    def css(self, style):

        self.message({'event': 'css', 'css': style})

    def attr(self, attrs):

        self.message({'event': 'attr', 'attr': attrs})


class HBox(Widget):

    def html(self):
        return Template("""
        <widget id="_{{identifier}}">
        <div id="{{identifier}}" style="display: flex; flex-direction: row;">
        </div>
        <script>
        new Widget("{{identifier}}", APP.wsopen);
        </script>
        """).render(
            identifier=self.identifier
        )

    @event_handler("started")
    def on_started(self, msg):
        self.on_children(msg)


class VBox(Widget):

    def html(self):
        return Template("""
        <widget id="_{{identifier}}">
        <div id="{{identifier}}" style="display: flex; flex-direction: column; {{style}}">
        </div>
        <script>
        new Widget("{{identifier}}", APP.wsopen);
        </script>
        </widget>
        """).render(
            identifier=self.identifier,
            style=self.style_string()
        )

    @event_handler("started")
    def on_started(self, msg):
        self.on_children(msg)


class Button(Widget):
    """
    Plain HTML button.

    Supported events: click.
    """

    def __init__(self, label="button", **kwargs):
        super().__init__(**kwargs)
        self.label = label

    def html(self):
        return Template("""
        <widget id="_{{identifier}}">
        <button id="{{identifier}}" style="{{style}}">{{label}}</button>
        <script>
        let b = new Widget("{{identifier}}", APP.wsopen);
        b.node.on("click", function( event ) {
          console.log({id:"{{identifier}}", event: 'click'});
          APP.send({id:"{{identifier}}", event: 'click'});
        });
        </script>
        </widget>
        """).render(
            identifier=self.identifier,
            label=self.label,
            style=self.style_string()
        )

    @event_handler("click")
    def on_click(self, msg):
        """
        Main event handler for the "click" event.

        :param msg:
        :return:
        """
        print(f'{self.__class__.__name__}.on_click()')
        print(f'{len(self.subscribers["click"])} subscribers.')
        for subscriber in self.subscribers['click']:
            subscriber(self)


class Input(Widget):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._value = ""

    def html(self):
        return Template("""
        <widget id="_{{identifier}}">
        <input id="{{identifier}}" type="text" style="{{style}}">
        <script>
        let w = new Widget("{{identifier}}", APP.wsopen);
        w.node.on("change", function(event) {
            console.log({id:"{{identifier}}", event: 'change', value: event.currentTarget.value});
            APP.send({id:"{{identifier}}", event: 'change', value: event.currentTarget.value});
        });
        w.onMsgType("value", function(message) {
            this.node[0].value = message.value;
        });
        </script>
        </widget>
        """).render(
            identifier=self.identifier,
            style=self.style_string()
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
        self._value = msg['value']
        for subscriber in self.subscribers['change']:
            subscriber(self)


class Label(Widget):

    def __init__(self, value="", **kwargs):
        super().__init__(**kwargs)
        self._value = value

    def html(self):
        return Template("""
        <widget id="_{{identifier}}">
        <div id="{{identifier}}" style="{{style}}">{{ value }}</div>
        <script>
        let w = new Widget("{{identifier}}", APP.wsopen);
        w.onMsgType("value", function(message) {
            this.innerHTML = message.value;
        });
        </script>
        </widget>
        """).render(
            identifier=self.identifier,
            value=self._value,
            style=self.style_string()
        )


class CheckBox(Widget):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._checked = False

    def html(self):
        return Template("""
        <widget id="_{{identifier}}">
        <input id="{{identifier}}" type="checkbox" style="{{style}}">
        <script>
        let w = new Widget("{{identifier}}", APP.wsopen);
        w.node.on("change", function( event ) {
            console.log({id:"{{identifier}}", event: 'change', value: event.currentTarget.checked});
            APP.send({id:"{{identifier}}", event: 'change', value: event.currentTarget.checked});
        });
        w.onMsgType("value", function(message) {
            console.log('message.event == "value"');
            this.node.checked = message.value;
        });
        </script>
        </widget>
        """).render(
            identifier=self.identifier,
            style=self.style_string()
        )

    @property
    def checked(self):
        return self._checked

    @checked.setter
    def checked(self, val):
        print(f'{self.__class__.__name__}.checked({val})')
        self.message({'event': 'value', 'value': val})
        self._checked = val

    @event_handler("change")
    def on_change(self, msg):
        """
        Event handler for the "change" event.

        TODO: This may need to be part of the Widget class and common to all.

        :param msg:
        :return:
        """
        print(f'{self.__class__.__name__}.on_change({msg})')

        self._checked = msg['value']

        print(f'{len(self.subscribers["change"])} subscribers.')
        for subscriber in self.subscribers['change']:
            subscriber(self)


class Image(Widget):

    def __init__(self):
        super().__init__()
        self._data = ""

    def html(self):

        return Template("""
        <widget id="_{{identifier}}">
        <img src="data:image/png;base64,{{ data }}" width="640" height="480" border="0" />
        <script>
        let w = new Widget("{{identifier}}", APP.wsopen);
        </script>
        </widget>
        """).render(
            self.identifier,
            self.data
        )

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value
        self.message({'event': 'attr',
                      'attr': {'src': f'data:image/png;base64,{value}'}})


