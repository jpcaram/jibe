from random import choice
from jinja2 import Template
from typing import Callable, List
import json


letter = 'abcdefghijklmnopqrstuvwxyz1234567890'


# def callback_method(func):
#     """
#     Used to wrap methods such that _callbacks in the class
#     are called immediately after the method.
#
#     :param func: Method to be wrapped.
#     :return: Wrapped method.
#     """
#
#     def notify(self, *args, **kwargs):
#         retval = func(self, *args, **kwargs)
#         for callback in self._callbacks:
#             callback(self, *args, **kwargs)
#         return retval
#
#     return notify
#
#
# class NotifyList(list):
#     """
#     Extends list to support a callback on change.
#     """
#     extend = callback_method(list.extend)
#     append = callback_method(list.append)
#     remove = callback_method(list.remove)
#     pop = callback_method(list.pop)
#     __delitem__ = callback_method(list.__delitem__)
#     __setitem__ = callback_method(list.__setitem__)
#     __iadd__ = callback_method(list.__iadd__)
#     __imul__ = callback_method(list.__imul__)
#
#     def __init__(self, *args):
#         list.__init__(self, *args)
#         self._callbacks = []


def callback_method_x(method: Callable, cbname: str) -> Callable:
    """
    Used to attach callbacks to different methods of list that modify
    the list, in NotifyList2.

    The list is modified first. Then the callback is invoked.

    :param method: Method to which we attach the callback.
    :param cbname: Name of the method to be called as callback.
    :return: Wrapped method.
    """

    def notify(self: List, *args, **kwargs):
        """

        :param self: The object on which method is being called.
        :param args: Varies. For append, args[0] is the item being added.
        :param kwargs: Additional keyword arguments are passed to the
            method and the callback.
        :return:
        """
        retval = method(self, *args, **kwargs)
        for callback in getattr(self, cbname):
            callback(*args, **kwargs)
        return retval

    return notify


class NotifyList2(list):
    """
    Extends list to support callbacks on different methods that
    modify the contents of the list.

    The list is modified first. Then the callback is invoked.
    """

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
    checked by the constructor of the class (eg. Widget).

    Example:

    Set @event_handler('click') on a method of a Widget. This will
    define widget.subscribers['click']. In the marked mathod, call
    the subscribers. The method will be called when the event is triggered.

    Other can subscribe via widget.register('click', callback).

    :param args:
    :return:
    """
    print(f'event_handler({args})')

    def decorator(f):
        print(f'decorator({f})')
        f.event_register = tuple(args)
        return f

    return decorator


class LoudDict(dict):
    """
    A Dictionary with a callback for
    item changes.
    """

    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.callback = lambda x, y, z: None

    def __setitem__(self, key, value):
        """
        Overridden __setitem__ method. Will call self.callback
        with the key as paramater if the new value is different
        from the previous value.
        """

        last = None
        if key in self:
            last = self.__getitem__(key)
            if last == value:
                return

        dict.__setitem__(self, key, value)
        self.callback(key, value, last)

    def update(self, *args, **kwargs):
        if len(args) > 1:
            raise TypeError("update expected at most 1 arguments, got %d" % len(args))
        other = dict(*args, **kwargs)
        for key in other:
            self[key] = other[key]

    def set_change_callback(self, callback):
        """
        Assigns a function as callback on item change. The callback
        will receive the key of the object that was changed.

        :param callback: Function to call on item change.
        :type callback: func
        :return: None
        """

        self.callback = callback


class OrfanWidgetError(Exception):
    pass


class NoSuchEvent(Exception):
    pass


class Widget:

    def __init__(self, *args, style=None, identifier=None,
                 renderOnChange=True, notifyServerOnChange=True):

        super().__setattr__('properties', LoudDict())

        # There is nothing in on_change yet.
        self.properties.set_change_callback(self.on_change)

        self.renderOnChange = renderOnChange

        self.notifyServerOnChange = notifyServerOnChange

        self.identifier = identifier or self.__class__.__name__ + '-' + ''.join(choice(letter) for _ in range(10))
        """Unique identifier to find the browser counterpart."""

        self.browser_side_ready = False

        self._parent = None
        """Widgets pass messages up to their parent to reach the main App,
        which sends the message to the browser.
        """

        self.descendent_index = {}

        self._children = NotifyList2([])
        """For composite widgets."""

        # What to do when we make changes to self._children.
        self._children._on_append_callbacks.append(self.on_children_append)
        self._children._on_remove_callbacks.append(self.on_children_remove)

        self.local_event_handlers = {}
        """To define event handlers within the object."""

        self.subscribers = {}
        """For others to benotified of events."""

        self.style = {} if style is None else style
        """Style attribute"""

        self.classname = "widget"

        self.tagname = "div"

        # self.properties = {}

        self.attributes = {}

        self._jshandlers = {}
        """Defines the bodies of the callback functions in Javascript for
        events occurring on the DOM element. The keys are the event names.
        The 'this' object is the widget, not the DOM element."""

        self.outbox = []
        """Message queue waiting for browser side to be ready."""

        self.template_txt = ""

        self._jsrender = None
        """Defines the body of the Javascript rendering function."""

        self._jscustomMethods = {}

        # Process methods marked as event handlers
        # (Decorated with @event_handler('event_name')).
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

                    if event_name in self.local_event_handlers:
                        raise TypeError(f'Event "{event_name}" of {repr(self)} already has a handler.')

                    self.local_event_handlers[event_name] = method
                    self.subscribers[event_name] = []
                    print(f'{self.__class__.__name__}: Registered event "{event_name}"')
                except AttributeError:  # Does not have 'register'
                    pass

        # self.children = [] if len(args) == 0 else args[1]  # This will trigger a message, even if empty.

    def __setattr__(self, key, value):
        """
        Allows keys in the 'properties' member to behave as members. When assigned
        to and if the item changes, this.on_change is called, which sends out
        a message to notify of the change.

        :param key: Name of the attribute (or property).
        :param value: Value to be assigned.
        :return: None
        """

        if key in self.properties:
            self.properties[key] = value
        else:
            super().__setattr__(key, value)

    def __getattr__(self, item):
        """
        Note: This gets called when the normal lookup fails, so we don't
        need to handle the normal lookup here.
        """

        if item == 'properties':
            # This can happen if a descendent class did not call super()
            # before trying to access the 'properties' member.
            raise AttributeError('This Widget has not been properly initialized.')
        try:
            return self.properties[item]
        except KeyError:
            raise AttributeError

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

        TODO: Make sure the new value is different.

        :param value: List of children.
        :return: None
        """
        print(f'{self.__class__.__name__}.children({value})')

        self._children = NotifyList2(value)
        # What to do when we make changes to self._children.
        self._children._on_append_callbacks.append(self.on_children_append)
        self._children._on_remove_callbacks.append(self.on_children_remove)

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
            print(f"[{self.identifier}] This widget does not have a parent to notify about descendents.")

    def template(self):
        return self.template_txt

    def on_children_change(self):
        """
        Called when the children attribute is assigned. Children are "adopted",
        i.e. their parent property is set to this widget.

        This also triggers a call to self.update_descendents(). Actually,
        each child calls it when it detects that its 'parent' member is
        being set.

        :return: None
        """
        print(f'{self.__class__.__name__}.on_children_change()')

        # Adopt children
        print(f'{repr(self)} adopting children:')
        for child in self.children:
            print(f'   {repr(child)} adopted.')
            child.parent = self  # Invokes child.parent.update_descendents().

        # Notify the client if it is ready. If we do it before it is ready,
        # the messages will be queued and then this will happen twice when
        # it becomes ready.
        if self.browser_side_ready:
            self.on_children()

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

        self.message({'event': 'append', 'child': child.toJSON()})

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

    def __repr__(self):
        return f'{self.__class__.__name__}(id="{self.identifier}")'

    def __str__(self):
        # return self.html()
        return self.__repr__()

    def on_message(self, msg):
        """
        Invoked when a message for this Widget is received from the browser.

        :param msg:
        :return:
        """
        print(f'{repr(self)}.on_message()')
        print(f'   says: {msg}')

        if 'event' in msg and msg['event'] in self.local_event_handlers:
            print(f'   Forwarding to \"{msg["event"]}\" event handler.')
            self.local_event_handlers[msg['event']](msg)

    def message(self, msg):
        """
        Send a message to this widget's browser side.

        :param msg:
        :return:
        """

        msg['id'] = self.identifier
        msg['path'] = []
        self.deliver(msg)

    def deliver(self, msg):
        """
        Passes a message to the parent to be delivered to the Browser.

        :param msg:
        :return:
        """
        print(f'{self.__class__.__name__}.deliver()')

        # Queued messages will re-attempt delivery so the
        # identifier will already be attached to the path.
        if len(msg['path']) == 0 or msg['path'][0] != self.identifier:
            msg['path'].insert(0, self.identifier)

        if not self.browser_side_ready:
            self.outbox.append(msg)
            print(f'   Appended to outbox: {msg}')
        else:
            try:
                self.parent.deliver(msg)
                print(f'   Passed to parent: {msg}')
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
    def on_children(self, msg=None):
        """
        Javascript counterpart request for children. Widgets that have children
        will request for their children once they are instantiated in the browser.

        :param msg: Message from the browser
        :return: None
        """
        print(f"{self.__class__.__name__}.on_children(...)")
        self.send_children()

    def send_children(self):
        """
        Serialize and send children to the browser.

        :return: None
        """
        self.message({'event': 'children', 'children': [
            child.toJSON() for child in self.children
        ]})

    @event_handler("started")
    def on_browser_side_ready(self, msg):
        """
        Javascript counterpart is ready in the browser and can receive
        messages. Delivers all queued messages.

        :param msg: Message from the browser
        :return: None
        """

        # These will get put in the outbox and delivered after.
        if len(self.children) > 0:
            self.send_children()

        self.browser_side_ready = True
        for msg in self.outbox:
            self.deliver(msg)
        self.outbox = []

    def style_string(self):
        """
        Serialize this widget's style member into a CSS compatible string.

        :return: CSS string for this widget.
        """
        return " ".join([f"{key}: {value};" for key, value in self.style.items()])

    def css(self, style):

        self.message({'event': 'css', 'css': style})

    def attr(self, attrs):

        self.message({'event': 'attr', 'attr': attrs})

    def toJSON(self):
        """
        JSON representation of the object.

        :return: JSON-compatible object representation of this widget.
        """

        return {
            'id': self.identifier,
            'properties': self.properties,  # "model"
            'attributes': self.attributes,
            'style': self.style,
            'tagName': self.tagname,
            'className': self.classname,
            'template': self.template(),  # TODO: Why call?
            'handlers': self._jshandlers,
            'render': self._jsrender,
            'renderOnChange': self.renderOnChange,
            'notifyServerOnChange': self.notifyServerOnChange,
            'customMethods': self._jscustomMethods
        }

    def serialize(self):
        """
        Returns a string with a JSON representation of this widget.
        """
        return json.dumps(self.toJSON())

    def on_change(self, propname, newval, oldval):
        """
        Callback for change in self.properties.

        :param propname: Name of the property that has changed.
        :param newval: New value of the property.
        :param oldval: Previous value of the property.
        :returns: None
        """
        print(f"{self.__class__.__name__}.on_change('{propname}')")
        self.message({'event': 'properties',
                      'properties': {propname: newval}})


class Div(Widget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class HBox(Widget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, style={
            'display': 'flex',
            'flex-direction': 'row'
        }, **kwargs)


class VBox(Widget):

    def __init__(self, *args, **kwargs):
        style = {
            'display': 'flex',
            'flex-direction': 'column'
        }
        if 'style' in kwargs:
            style.update(kwargs['style'])
            del kwargs['style']
        super().__init__(*args, style=style, **kwargs)


class Button(Widget):
    """
    Plain HTML button.

    Supported events: click.
    """

    def __init__(self, label="button", **kwargs):
        super().__init__(**kwargs)
        self.tagname = "button"

        self.template_txt = "{{ label }}"

        self.properties = {
            'label': label
        }

        self._jshandlers['click'] = """
            this.message({event: 'click'});
        """

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
    """
    Single-line text input.

    Supported events: change.
    """

    def __init__(self, value='', **kwargs):

        super().__init__(**kwargs)

        # Do not overwrite self.properties. It is a LoudDict configured
        # to trigger events on change. Only create and assign to items.
        self.properties['value'] = value

        self.tagname = "input"

        # DOM NODE HANDLERS
        # _jshandlers appears as "hadlers" in the JSON representation.
        # These events are attached to the DOM node. In this case,
        # this is the event triggered when the text in the input
        # box changes. Here we save it to the model. This will
        # trigger the render method for the widget in the browser. See below.
        self._jshandlers['change'] = """
            console.log(`[${this.id}] custom change handler.`);
            this.model.set('value', this.el.value);
        """

        # RENDER METHOD OVERRIDE
        # We don't need to render the widget in the DOM, just
        # change it's 'value'.
        # _jsrender appers as "render" in the JSON representation.
        # TODO: Will this trigger the 'change' event in the DOM element
        #   again, and therefore a 'change' in the model once more and
        #   forever? In the model it may not get triggered again if the
        #   value is not different.
        self._jsrender = """
            console.log(`[${this.id}] custom render():`);
            this.el.value = this.model.get('value');
        """

    @event_handler("change")
    def on_change_msg(self, msg):
        """
        Event handler for the "change" event.

        :param msg:
        :return:
        """
        print(f'{self.__class__.__name__}.on_change_msg({msg})')

        # Use super().__setattr__ if you don't want to send an
        # update to the browser.
        # super().__setattr__('value', msg['properties']['value'])
        self.value = msg['properties']['value']

        for subscriber in self.subscribers['change']:
            subscriber(self)


class Dropdown(Widget):

    def __init__(self, value=None, options=None, **kwargs):

        super().__init__(**kwargs)

        self.tagname = 'select'

        # Different combinations for defaults when
        # value and/or options is missing.
        if value is None and options is not None:
            value = options[0]
        elif value is not None and options is None:
            options = [value]
        else:
            options = []
            value = None

        self.properties.update({
            'value': value,
            'options': options
        })

        self.template_txt = """
            {{#each options}}
                <option value="{{this}}"
                {{#if_eq ../value this}}
                selected
                {{/if_eq}}
                >{{this}}</option>
            {{/each}}
        """

        # DOM NODE HANDLERS
        # _jshandlers appears as "hadlers" in the JSON representation.
        # These events are attached to the DOM node. In this case,
        # this is the event triggered when the selection on the
        # dropdown changes. Here we save it to the model. This will
        # trigger the render method for the widget in the browser. See below.
        self._jshandlers['change'] = """
            console.log(`[${this.id}] custom change handler.`);
            this.model.set('value', this.el.value);
        """

    @event_handler("change")
    def on_change_msg(self, msg):
        """
        Event handler for the "change" event.

        :param msg:
        :return:
        """
        print(f'{self.__class__.__name__}.on_change_msg({msg})')

        self.value = msg['properties']['value']

        # super().__setattr__('value', msg['properties']['value'])
        for subscriber in self.subscribers['change']:
            subscriber(self)


class Label(Widget):
    """
    Simple text label.

    The 'value' property is the text shown in the label. This
    member is part of the object's model, therefore it is
    immediately synchronized and updated in the browser
    when it changes.
    """

    def __init__(self, value="", **kwargs):
        """
        Simple text label.

        :param value: Text of the label.
        :type value: str
        :param kwargs: All other named arguments are passed intact
                       to the parent (Widget).
        """
        super().__init__(**kwargs)
        self.properties['value'] = value

        # This is the default. Not needed:
        # self.tagname = "div"

        self.template_txt = "<p>{{ value }}</p>"


class CheckBox(Widget):

    def __init__(self, checked=False, **kwargs):
        super().__init__(**kwargs)
        self.properties['checked'] = checked

        self.tagname = 'input'
        self.attributes['type'] = 'checkbox'

        # React to DOM events.
        self._jshandlers['change'] = """
            console.log(`[${this.id}] custom change handler.`);
            this.model.set('checked', this.el.checked);
        """

        # Do not re-render, just change the 'checked' value.
        self._jsrender = """
            console.log(`[${this.id}] custom render():`);
            this.el.checked = this.model.get('checked');
        """

    @event_handler("change")
    def on_change_msg(self, msg):
        """
        Event handler for the "change" event.

        :param msg:
        :return:
        """
        print(f'{self.__class__.__name__}.on_change_msg({msg})')

        # This will trigger a message back to the browser but wont
        # trigger another change event there.
        self.checked = msg['properties']['checked']

        print(f'{len(self.subscribers["change"])} subscribers.')
        for subscriber in self.subscribers['change']:
            subscriber(self)


class Image(Widget):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._data = ''
        self.tagname = 'img'

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value
        self.message({'event': 'attr',
                      'attr': {'src': f'data:image/png;base64,{value}'}})


class ProgressBar(Div):
    """
    Simple progress bar. Its 'value' property represents its progress
    from 0 to 100.
    """

    def __init__(self, value=0, *args):
        """
        Simple progress bar.

        TODO: Pass args to super constructor.

        :param value: Progress value, from 0 to 100.
        :param args:
        """
        super().__init__(style={
            'min-width': '300px',
            'max-width': '300px',
            'min-height': '28px',
            'max-height': '28px',
            'padding': '0px',
            'border': '0px',
            'margin': '8px',
            'background-color': '#dddddd'
        })

        self.inner = Div(style={
            'min-width': '0%',
            'max-width': '0%',
            'min-height': '28px',
            'max-height': '28px',
            'padding': '0px',
            'border': '0px',
            'margin': '0px',
            'background-color': 'rgb(99, 99, 210)'
        })

        self.children = [self.inner]

        self.properties['value'] = value

        # We don't want to re-render when 'value' changes.
        # We directly update CSS of self.inner instead.
        self.renderOnChange = False

    @property
    def value(self):
        return self.properties['value']

    def on_change(self, propname, newval, oldval):
        """
        Overrides the normal on_change, which sends a message to
        the browser notifying of the change to a property, by
        in addition, sending an update to CSS properties of
        one of its children.

        Notice that in this example the only property is 'value',
        so we don't even check for it.

        :param propname: Property name.
        :param newval: New value.
        :param oldval: Old value.
        :return: None
        """
        super().on_change(propname, newval, oldval)

        print(f"{self.__class__.__name__}.on_change('{propname}')")

        # Don't go past 100.
        value = self.value if self.value <= 100 else 100

        # Set the right value silently.
        dict.__setitem__(self.properties, 'value', value)

        self.inner.css({
            'min-width': f'{self.value}%',
            'max-width': f'{self.value}%'
        })


class Redirect(Widget):
    """
    A widget that allows triggering a page redirection.

    This widget is invisible and can be placed anywhere as a child
    of the main application or of another widget. It simply runs the
    required Javascript on the browser to redirect to another page
    when its redirect() method is called.
    """

    def __init__(self):

        super().__init__(style={
            'visibility': 'hidden',
            'display': 'none'
        })

        # Override the JS rendering method such that it never
        # attemps to render this widget in the DOM.
        self._jsrender = """
            // Do nothing.
        """

        # Custom JS methods are called from Python by sending a
        # message with 'event': 'name-of-method' and the method
        # receives a single parameter 'msg', which contains the
        # entire message.
        self._jscustomMethods['redirect'] = """
            console.log(`[${this.id}] redirect('${msg.location}')`);
            window.location.replace(msg.location)
        """

    def redirect(self, url):
        """
        Messages the widget in the browser to redirect to
        the given url using Javascript.

        :param url: Destination URL.
        :return: None
        """

        self.message({
            'event': 'redirect',
            'location': url
        })

