Examplained Examples
====================

These are all standalone examples, i.e. they are all you
need and should just run as-is.

The code for the exaples below can be found in the
``examples`` folder of the git repository.

The comments in the code have been removed for clarity but
further explanation is provided outside the code.

Basic
-----

This is the same example shown in the home page but
we disect it a little further. It contains the bare minimum
for a single-application server.

.. code-block:: python
    :linenos:

    from jibe import MainApp, Button, Input

    class ExampleApp(MainApp):

        def __init__(self, connection):
            super().__init__(connection)

            self.children = [
                Button(),
                Input(value='The value')
            ]
            self.children[0].register('click', self.on_button_click)

        def on_button_click(self, source, message):
            self.children[1].value = "Hello!"


    if __name__ == "__main__":
        ExampleApp.run(port=8881)


.. raw:: html

    <style>
    .widget {
        font-family: "Lato","proxima-nova","Helvetica Neue",Arial,sans-serif;
        font-size: 13px;
        margin: 0px;
    }
    input.widget {
        border-color: rgb(158,158,158);
        border-style: solid;
        border-width: 1px;
        padding: 4px;
        margin: 8px;
        box-shadow: inset 0 1px 3px #ddd;

        font-size: 13px;
        color: rgba(0,0,0,0.8);
    }
    button.widget {
        color: rgba(0,0,0,0.8);
        background-color: #eaeaea;
        padding: 6px 10px;  /* Top-bottom right-left */
        margin: 8px;
        border-width: 0;
        cursor: pointer;
    }

    button.widget:hover {
        box-shadow: 3px 3px 3px #a4a4a4;
    }

    button.widget:active {
        box-shadow: 0px 0px 0px #a4a4a4;
    }

    button.widget:focus {
        outline: 1px solid #709aa4;
    }
    </style>
    <button class="widget button" id="Button-b5g9ir05n9">button</button>
    <input class="widget input" id="Input-2jtlw9clni" value="The value">

This example shows a standalone Jibe application that we have defined
as ``ExampleApp``, starting on line 3.
It does not require a separate web server.
The server for the application is started on line
19 and it listens on port 8881 of the machine it is started
on. You can access it by going to ``http://localhost:8881``
on any web browser.

The application is defined by creating a class which inherits
from the ``MainApp`` class. All Jibe applications are defined
in this way. Jibe relies heavily on object orientation, so if
you are unfamiliar with concepts like classes and inheritance
we suggest that you strengthen your grasp of these concepts
first.

The ``MainApp`` class contains all the complexity that makes
a Jibe application. It is there for you to access it when you need
it, otherwise it is hidden to make your code clearer. To put
the ``MainApp``'s machinery into acction we must call it's
constructor (line 6) in our constructor (lines 5-12). Since
it requires a ``connection`` parameter, our constructor must
also accept this same parameter.

An important detail to know at this point is that the ``MainApp``
class also inherits from ``Widget``. Therefore, ``ExampleApp``
**is a** ``Widget``, as all Jibe applications are. Widgets can
have child widgets, which allows us to build complex widgets
out of simpler widgets simply by combining them together as children
of the complex widget.

In this case, our application (or top-level widget) contains
two children, a ``Button`` and an ``Input``. On lines 8 to 11
we creates instances of these two classes, we put them together
in a list and assign it to the ``children`` variable of the
application. The ``children`` variable is special in the sense
that it is "aware" of its changes. As soon as it is assigned to
(or changed), it communicates with the browser to update
the widget's representation there.

On line 12 we specify that we want to react to `click` events
on the button. The ``register`` method of widgets takes
the name of the event and a function (or method) to call
when it happens.

On lines 14 and 15 we defined the "event handler" that we
specified on line 12. Event handlers take 2 parameter: ``source``
is the widget that triggered the event (it will allways be
that specific button in this case), and ``message`` is
the message that was sent from the server that alerted us
that this event has happened. The message may contain useful additional
information about the event (which we don't need in this case).

The body of ``on_button_click`` is an assignment to the ``value``
variable of the ``Input`` widget. This variable is a **property**.
Properties are special variables, similar to ``children`` in that
they are also "aware" of changes, causing an immediate update
on the browser. Therefore, when the button is clicked, the value of
the Input, "The value", changes to "Hello!".


MultiApp
--------

This example illustrates how to have a multiple-application
server. For web platforms that require a little more complexity
is it convenient to have the ability to combine multiple
Jibe applications together.

.. code-block:: python
    :linenos:

    from jibe import MainApp, Button, Input, CheckBox, \
        Redirect, MultiApp

    class ExampleAppA(MainApp):

        def __init__(self, connection):
            super().__init__(connection)

            self.btn_go2b = Button(label='Go to B')
            self.btn = Button()
            self.input = Input(value='The value')
            self.redir = Redirect()

            self.children = [self.btn_go2b, self.btn,
                self.input, self.redir]

            self.btn.register('click', self.on_button_click)
            self.btn_go2b.register("click", self.on_go2b)

        def on_button_click(self, source, message):
            self.input.value = "Hello!"

        def on_go2b(self, source, message):
            self.redir.redirect('/b')


    class ExampleAppB(MainApp):

        def __init__(self, connection):
            super().__init__(connection)
            self.btn_go2a = Button(label='Go to A')
            self.chk = CheckBox()
            self.btn = Button()
            self.redir = Redirect()

            self.children = [self.btn_go2a, self.chk,
                self.btn, self.redir]

            self.btn_go2a.register("click", self.on_go2a)
            self.btn.register("click", self.on_btn_click)

        def on_btn_click(self, source, message):
            self.chk.checked = True

        def on_go2a(self, source, message):
            self.redir.redirect('/a')

    if __name__ == "__main__":
        mapp = MultiApp(
            a=ExampleAppA,
            b=ExampleAppB
        )
        mapp.run()


Application ``ExampleAppA`` at ``http://localhost:8881/a``:

.. raw:: html

    <button class="widget button" id="Button-tdqbur16xt">Go to B</button>
    <button class="widget button" id="Button-zctqayag9r">button</button>
    <input class="widget input" id="Input-i20rnurzma">


Apllication ``ExampleAppB`` at ``http://localhost:8881/b``:

.. raw:: html

    <button class="widget button" id="Button-wc7jzy40m2">Go to A</button>
    <input class="widget checkbox" type="checkbox" id="CheckBox-o97ziq1j3e">
    <button class="widget button" id="Button-t58j1bay8e">button</button>

A Jibe ``MultiApp`` allows us to serve multiple Jibe ``MainApp`` together.
On lines 49 to 52 we create an instance of ``MultiApp`` and pass the
individual applications as keyword parameter to the constructor. The keywords,
``a`` and ``b`` in this case, define the relative URLs of the apps.

Asside from the use of ``MultiApp``, there is little more to this example.
However, we make use of of the ``Redirect`` widget, which is invisible on
the page, but as its name implies, allow us redirect the browser to another
URL. In this case, we use it to jump from one application to the other
in response to the `click` event of the respective buttons, on lines 24
and 46.