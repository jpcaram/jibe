Widgets
=======

Widgets are the building blocks of Jibe applications.
Widgets are objects that describe code and data that live
simultaneously in the server and in the browser, and are
automatically synchronized. You only write their code once,
on the server side and in Python.

A Jibe application is composed of a tree of widgets. Since
some widgets can have "children" widgets, we can build an
application starting with one widget and adding widgets to
it as its children. Its children can also have children, so
we can indefinitely nest widgets within widgets.
Some widgets serve only the purpuse of grouping widgets
together and laying them out in a desired fashion
(for example side by side, or top to bottom).

Jibe provides a rich collection of basic widgets that
can be used to build more complex widgets. However, it is
possible to build your own low-level widgets from scratch,
allowing you to control every little detail.

In :ref:`Example #1 <example1>` we create an application by defining
our own class ``ExampleApp``, which inherits from ``MainApp`` and,
``MainApp`` inherits from ``Widget``. So, an application is nothing
but a widget, except for some additional code in ``MainApp`` that
allows this widget to be an application. We see as well
that its member ``children`` is assigned in the constructor
and it is populated with two other widgets, a ``Button`` and
an ``Input``. Finally, we call the ``register()`` method of
the button to be able to respond to "click" events with
a call to ``on_button_click()``.

There is very little going on under the hood, except for the
behavior of two special variables as we'll see next.

Widget.children
---------------

The ``children`` variable of a widget is aware when it is
assigned to or changed. When this happens, the widget immediately
notifies the browser and triggers the necessary updates.
This means that the list of children can be updated at any
time, not just in the constructor of the widget, allowing
for dynamic updates to the client.

Widget.properties
-----------------

The ``properties`` dictionary of a widget is also aware of changes
and keeps the client automatically synchronized.

When a property changes it triggers a reaction on both
the server and the client. By default, the client will
re-render the widget such that it always properly reflects
the state of ``properties`` in the user interface. On the
server side we can react to the event by overriding the
``on_change()`` method of ``Widget``. For example::

   class MyWidget(Widget):
      def __init__(self, connection):
         super().__init__(connection)
         self.properties['open'] = False

      def on_change(propname, newval, oldval):
         super().on_change(propname, newval, oldval)
         # Do something else here
         print("Properties changed!")

It is important to call the parent's ``on_change()`` since it
takes care of updating the widget in the browser about the change.

Properties can alse be read and written as members of the widget
without the need to reference the `properties` variable::

   print(self.open)  # False
   self.open = True  # This triggers on_change()


